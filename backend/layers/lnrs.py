import numpy as np
import rasterio.features

from layers.base import fetch_layer
from pathfinding.grid import GridSpec

LNRS_MULTIPLIER = 1.15


def get_lnrs_multiplier_raster(grid: GridSpec, bbox_wgs84: tuple[float, float, float, float]) -> np.ndarray:
    """Returns a multiplier raster: 1.15 where LNRS area, 1.0 elsewhere."""
    geojson = fetch_layer("lnrs", bbox_wgs84)
    features = geojson.get("features", [])

    raster = np.ones((grid.n_rows, grid.n_cols), dtype=np.float32)

    if not features:
        return raster

    shapes_vals = [
        (feat["geometry"], LNRS_MULTIPLIER)
        for feat in features
        if feat.get("geometry")
    ]

    if shapes_vals:
        rasterio.features.rasterize(
            shapes=shapes_vals,
            out=raster,
            transform=grid.transform,
            fill=1.0,
            dtype="float32",
            all_touched=True,
        )

    return raster
