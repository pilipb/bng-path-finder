from dataclasses import dataclass
import numpy as np
from pyproj import Transformer
import rasterio.transform


@dataclass
class GridSpec:
    transform: rasterio.transform.Affine
    crs: str
    n_rows: int
    n_cols: int
    cell_size_m: float
    bbox_osgb: tuple[float, float, float, float]  # minx, miny, maxx, maxy in OSGB36
    bbox_wgs84: tuple[float, float, float, float]  # minlng, minlat, maxlng, maxlat


_to_osgb = Transformer.from_crs("EPSG:4326", "EPSG:27700", always_xy=True)
_to_wgs84 = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)

MAX_CELLS = 2000
BUFFER_M = 500


def make_grid(point_a: tuple[float, float], point_b: tuple[float, float]) -> GridSpec:
    """
    Build a GridSpec from two WGS84 (lat, lng) points.
    Returns a 25m OSGB36 raster coordinate space with buffer.
    """
    lat_a, lng_a = point_a
    lat_b, lng_b = point_b

    # Reproject to OSGB36 (metres)
    xa, ya = _to_osgb.transform(lng_a, lat_a)
    xb, yb = _to_osgb.transform(lng_b, lat_b)

    # Bounding box with buffer
    minx = min(xa, xb) - BUFFER_M
    miny = min(ya, yb) - BUFFER_M
    maxx = max(xa, xb) + BUFFER_M
    maxy = max(ya, yb) + BUFFER_M

    width_m = maxx - minx
    height_m = maxy - miny

    # Compute cell size (cap grid at MAX_CELLS × MAX_CELLS)
    diagonal_m = (width_m**2 + height_m**2) ** 0.5
    cell_size_m = max(25.0, diagonal_m / MAX_CELLS)

    n_cols = max(2, int(np.ceil(width_m / cell_size_m)))
    n_rows = max(2, int(np.ceil(height_m / cell_size_m)))

    transform = rasterio.transform.from_bounds(minx, miny, maxx, maxy, n_cols, n_rows)

    # WGS84 bbox for API queries
    min_lng, min_lat = _to_wgs84.transform(minx, miny)
    max_lng, max_lat = _to_wgs84.transform(maxx, maxy)

    return GridSpec(
        transform=transform,
        crs="EPSG:27700",
        n_rows=n_rows,
        n_cols=n_cols,
        cell_size_m=cell_size_m,
        bbox_osgb=(minx, miny, maxx, maxy),
        bbox_wgs84=(min_lng, min_lat, max_lng, max_lat),
    )


def wgs84_to_grid(lat: float, lng: float, grid: GridSpec) -> tuple[int, int]:
    """Convert WGS84 lat/lng to (row, col) grid indices."""
    x, y = _to_osgb.transform(lng, lat)
    col, row = ~grid.transform * (x, y)
    row = int(np.clip(round(row), 0, grid.n_rows - 1))
    col = int(np.clip(round(col), 0, grid.n_cols - 1))
    return row, col


def grid_to_wgs84(row: int, col: int, grid: GridSpec) -> tuple[float, float]:
    """Convert grid (row, col) to WGS84 (lat, lng)."""
    x, y = grid.transform * (col + 0.5, row + 0.5)
    lng, lat = _to_wgs84.transform(x, y)
    return lat, lng
