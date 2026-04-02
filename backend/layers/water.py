import numpy as np

from pathfinding.grid import GridSpec

WATER_COST = 30.0


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
        return _fetch_from_gee(grid, bbox_wgs84)
    else:
        return np.zeros((grid.n_rows, grid.n_cols), dtype=np.float32)


def _fetch_from_gee(grid: GridSpec, bbox_wgs84: tuple[float, float, float, float]) -> np.ndarray:
    """Fetch JRC Global Surface Water occurrence layer from GEE."""
    try:
        import ee  # type: ignore

        min_lng, min_lat, max_lng, max_lat = bbox_wgs84
        region = ee.Geometry.Rectangle([min_lng, min_lat, max_lng, max_lat])

        gsw = ee.Image("JRC/GSW1_4/GlobalSurfaceWater")
        occurrence = gsw.select("occurrence")
        water_mask = occurrence.gt(10).multiply(WATER_COST)

        # Sample to grid dimensions using reproject
        resampled = water_mask.reproject(
            crs="EPSG:27700",
            scale=grid.cell_size_m,
        )

        # Use sampleRectangle — works for moderate grid sizes
        try:
            sample = resampled.sampleRectangle(region=region, defaultValue=0)
            arr = np.array(sample.get("occurrence").getInfo(), dtype=np.float32)
            # Resize to match grid dimensions if needed
            if arr.shape != (grid.n_rows, grid.n_cols):
                from skimage.transform import resize  # type: ignore
                arr = resize(arr, (grid.n_rows, grid.n_cols), order=0, preserve_range=True).astype(np.float32)
            return arr
        except Exception:
            # sampleRectangle has pixel limits; fall back to zeros
            print("[GEE] sampleRectangle failed (grid too large?), using zero water raster")
            return np.zeros((grid.n_rows, grid.n_cols), dtype=np.float32)

    except Exception as e:
        print(f"[GEE] Water fetch failed: {e}")
        return np.zeros((grid.n_rows, grid.n_cols), dtype=np.float32)
