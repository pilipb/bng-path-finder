from shapely.geometry import LineString
from shapely.ops import unary_union
import numpy as np

from pathfinding.grid import GridSpec, grid_to_wgs84


def smooth_path(
    path_indices: list[tuple[int, int]],
    grid: GridSpec,
    tolerance_m: float = 25.0,
) -> list[tuple[float, float]]:
    """
    Convert grid indices to WGS84 coords and apply Douglas-Peucker smoothing.
    Returns list of (lat, lng) tuples.
    """
    if len(path_indices) < 2:
        return [grid_to_wgs84(r, c, grid) for r, c in path_indices]

    # Convert to WGS84
    coords_wgs84 = [grid_to_wgs84(r, c, grid) for r, c in path_indices]

    # Build LineString in OSGB36 for metric simplification
    from pyproj import Transformer
    to_osgb = Transformer.from_crs("EPSG:4326", "EPSG:27700", always_xy=True)

    osgb_coords = [to_osgb.transform(lng, lat) for lat, lng in coords_wgs84]
    line_osgb = LineString(osgb_coords)
    simplified = line_osgb.simplify(tolerance_m, preserve_topology=False)

    # Convert back to WGS84
    from pyproj import Transformer as T2
    to_wgs84 = T2.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)

    result = []
    for x, y in simplified.coords:
        lng, lat = to_wgs84.transform(x, y)
        result.append((lat, lng))

    return result
