import numpy as np
import rasterio.features

from layers.base import fetch_layer
from pathfinding.grid import GridSpec

SSSI_COST = 50.0


def get_sssi_raster(grid: GridSpec, bbox_wgs84: tuple[float, float, float, float]) -> np.ndarray:
    """Returns a cost raster where SSSI IRZ = 50, 0 elsewhere."""
    geojson = fetch_layer("sssi_irz", bbox_wgs84)
    features = geojson.get("features", [])

    raster = np.zeros((grid.n_rows, grid.n_cols), dtype=np.float32)

    if not features:
        return raster

    shapes_vals = [
        (feat["geometry"], SSSI_COST)
        for feat in features
        if feat.get("geometry")
    ]

    if shapes_vals:
        rasterio.features.rasterize(
            shapes=shapes_vals,
            out=raster,
            transform=grid.transform,
            fill=0.0,
            dtype="float32",
            all_touched=True,
        )

    return raster
