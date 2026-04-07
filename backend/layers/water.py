import logging

import numpy as np

from pathfinding.grid import GridSpec

logger = logging.getLogger(__name__)

WATER_COST = np.inf


def get_water_raster(
    grid: GridSpec,
    bbox_wgs84: tuple[float, float, float, float],
    gee_available: bool,
) -> np.ndarray:
    """
    Returns water cost raster. If GEE is available, fetches JRC Global Surface Water.
    Otherwise returns zeros (water cost = 0, conservative fallback).
    """
    if gee_available:
        logger.debug("water: fetching from GEE")
        return _fetch_from_gee(grid, bbox_wgs84)
    else:
        logger.debug("water: GEE unavailable — returning zero raster")
        return np.zeros((grid.n_rows, grid.n_cols), dtype=np.float32)


def _fetch_from_gee(grid: GridSpec, bbox_wgs84: tuple[float, float, float, float]) -> np.ndarray:
    """
    Fetch JRC Global Surface Water as a GeoTIFF download.
    Returns a binary mask rasterized to the grid, then converts water cells to WATER_COST.
    """
    try:
        import io
        import ee        # type: ignore
        import requests  # type: ignore
        import rasterio  # type: ignore

        min_lng, min_lat, max_lng, max_lat = bbox_wgs84
        region = ee.Geometry.Rectangle([min_lng, min_lat, max_lng, max_lat])

        # Binary mask: 1 where permanent/semi-permanent water (>10% occurrence).
        # Do NOT multiply by WATER_COST (np.inf) — GEE can't handle that; apply it locally.
        water_binary = (
            ee.Image("JRC/GSW1_4/GlobalSurfaceWater")
            .select("occurrence")
            .gt(10)
        )

        url = water_binary.getDownloadURL({
            "region": region,
            "dimensions": f"{grid.n_cols}x{grid.n_rows}",
            "format": "GeoTIFF",
            "crs": "EPSG:27700",
        })

        resp = requests.get(url, timeout=60)
        resp.raise_for_status()

        with rasterio.open(io.BytesIO(resp.content)) as ds:
            arr = ds.read(1).astype(np.float32)

        result = np.zeros((grid.n_rows, grid.n_cols), dtype=np.float32)
        if arr.shape != (grid.n_rows, grid.n_cols):
            from skimage.transform import resize  # type: ignore
            arr = resize(arr, (grid.n_rows, grid.n_cols), order=0, preserve_range=True).astype(np.float32)
        result[arr > 0] = WATER_COST  # np.inf for water cells

        n_water = int(np.isposinf(result).sum())
        logger.info("water (GEE GeoTIFF): %d impassable water cells", n_water)
        return result

    except Exception as e:
        logger.error("water: GEE GeoTIFF fetch failed: %s — returning zero raster", e)
        return np.zeros((grid.n_rows, grid.n_cols), dtype=np.float32)
