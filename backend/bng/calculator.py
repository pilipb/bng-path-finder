import numpy as np
from pyproj import Transformer

from pathfinding.grid import GridSpec, grid_to_wgs84
from bng.weights import get_distinctiveness, DISTINCTIVENESS_COST

_to_osgb = Transformer.from_crs("EPSG:4326", "EPSG:27700", always_xy=True)

# BNG unit calculation: area destroyed × distinctiveness multiplier × condition factor
# For a road: area = length × road width (6m). Condition assumed "Good" for simplicity.
ROAD_WIDTH_M = 6.0
CONDITION_FACTOR = 1.0  # Good condition
HABITAT_UNITS_PER_HA_PER_DISTINCTIVENESS = 1.0  # simplified


def calculate_segments(
    path_indices: list[tuple[int, int]],
    smoothed_coords: list[tuple[float, float]],
    cost_raster: np.ndarray,
    habitat_raster_raw: np.ndarray,  # distinctiveness values (float)
    awi_mask: np.ndarray,
    sssi_mask: np.ndarray,
    lnrs_mask: np.ndarray,
    grid: GridSpec,
    habitat_name_lookup: dict | None = None,
) -> list[dict]:
    """
    Walk the raw path indices, group consecutive cells with same habitat zone,
    emit one segment per group.
    Returns list of segment dicts matching the RouteResponse contract.
    """
    if len(path_indices) < 2:
        return []

    # Group consecutive indices by distinctiveness value
    segments = []

    def cell_key(row: int, col: int) -> tuple:
        d = int(round(habitat_raster_raw[row, col]))
        is_awi = bool(awi_mask[row, col])
        is_sssi = bool(sssi_mask[row, col])
        is_lnrs = bool(lnrs_mask[row, col])
        return (d, is_awi, is_sssi, is_lnrs)

    current_key = cell_key(*path_indices[0])
    group_start_idx = 0

    groups = []
    for i in range(1, len(path_indices)):
        k = cell_key(*path_indices[i])
        if k != current_key:
            groups.append((group_start_idx, i - 1, current_key))
            group_start_idx = i
            current_key = k
    groups.append((group_start_idx, len(path_indices) - 1, current_key))

    # Build segments from groups
    seg_index = 0
    for g_start, g_end, key in groups:
        d, is_awi, is_sssi, is_lnrs = key

        # Get start/end coords from smoothed path (approximate by position ratio)
        start_coord = grid_to_wgs84(*path_indices[g_start], grid)
        end_coord = grid_to_wgs84(*path_indices[g_end], grid)

        # Calculate length in metres
        sx, sy = _to_osgb.transform(start_coord[1], start_coord[0])
        ex, ey = _to_osgb.transform(end_coord[1], end_coord[0])
        n_cells = g_end - g_start + 1
        length_m = float(n_cells) * grid.cell_size_m  # conservative approximation

        # BNG units = (length × road_width / 10000) × distinctiveness × condition
        area_ha = (length_m * ROAD_WIDTH_M) / 10_000
        cost_per_d = DISTINCTIVENESS_COST.get(d, 2.0)
        bng_units = area_ha * cost_per_d * CONDITION_FACTOR

        # Apply LNRS multiplier
        if is_lnrs:
            bng_units *= 1.15

        # Get habitat name from distinctiveness (reverse lookup, approximate)
        habitat_type = _d_to_label(d, is_awi)

        segments.append({
            "index": seg_index,
            "start": list(start_coord),
            "end": list(end_coord),
            "length_m": round(length_m, 1),
            "habitat_type": habitat_type,
            "distinctiveness": d,
            "bng_units": round(bng_units, 4),
            "sssi_flag": is_sssi,
            "lnrs_flag": is_lnrs,
            "ancient_woodland": is_awi,
        })
        seg_index += 1

    return segments


def _d_to_label(d: int, is_awi: bool) -> str:
    if is_awi:
        return "Ancient Woodland"
    labels = {
        8: "High Distinctiveness Habitat",
        6: "Medium-High Distinctiveness Habitat",
        4: "Medium Distinctiveness Habitat",
        2: "Low Distinctiveness Habitat",
        0: "Modified / Artificial Surface",
    }
    return labels.get(d, f"Habitat (distinctiveness {d})")
