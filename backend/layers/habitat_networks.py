import numpy as np
import rasterio.features
import rasterio.transform
from shapely.geometry import shape

from layers.base import fetch_layer
from bng.weights import get_distinctiveness, DEFAULT_DISTINCTIVENESS
from pathfinding.grid import GridSpec


def get_habitat_raster(grid: GridSpec, bbox_wgs84: tuple[float, float, float, float]) -> tuple[np.ndarray, dict[tuple[int,int], str]]:
    """
    Returns:
    - cost array (n_rows, n_cols) float32 with distinctiveness values
    - cell_habitat: dict mapping (row, col) → habitat_type string for segment labelling
    """
    geojson = fetch_layer("habitat_networks", bbox_wgs84)
    features = geojson.get("features", [])

    raster = np.full((grid.n_rows, grid.n_cols), float(DEFAULT_DISTINCTIVENESS), dtype=np.float32)

    if not features:
        return raster, {}

    # Try common field names for habitat type
    HABITAT_FIELD_CANDIDATES = [
        "Main_Habit", "HabitatTyp", "Habitat_Type", "HAB_TYPE",
        "Habitat", "Phase_1", "NVC_Community", "Description",
    ]

    # Sort features by distinctiveness ascending so high-value burns last (wins)
    def get_feature_distinctiveness(f: dict) -> int:
        props = f.get("properties") or {}
        for field in HABITAT_FIELD_CANDIDATES:
            if field in props and props[field]:
                return get_distinctiveness(str(props[field]))
        return DEFAULT_DISTINCTIVENESS

    sorted_features = sorted(features, key=get_feature_distinctiveness)

    shapes_vals: list[tuple] = []
    for feat in sorted_features:
        geom = feat.get("geometry")
        props = feat.get("properties") or {}
        if not geom:
            continue

        habitat_type = "Unknown"
        for field in HABITAT_FIELD_CANDIDATES:
            if field in props and props[field]:
                habitat_type = str(props[field])
                break

        d = get_distinctiveness(habitat_type)
        shapes_vals.append((geom, float(d)))

    if shapes_vals:
        rasterio.features.rasterize(
            shapes=shapes_vals,
            out=raster,
            transform=grid.transform,
            fill=float(DEFAULT_DISTINCTIVENESS),
            dtype="float32",
            all_touched=True,
        )

    return raster, {}
