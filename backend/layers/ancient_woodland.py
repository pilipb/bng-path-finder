import logging

import numpy as np
import rasterio.features

from layers.base import fetch_layer
from pathfinding.grid import GridSpec

logger = logging.getLogger(__name__)

ANCIENT_WOODLAND_COST = np.inf  # truly impassable — A* will never route through


def get_awi_raster(grid: GridSpec, bbox_wgs84: tuple[float, float, float, float]) -> np.ndarray:
    """Returns a cost raster where ancient woodland = np.inf (impassable), 0 elsewhere."""
    geojson = fetch_layer("ancient_woodland", bbox_wgs84)
    features = geojson.get("features", [])
    logger.info("ancient_woodland: %d features fetched", len(features))

    raster = np.zeros((grid.n_rows, grid.n_cols), dtype=np.float32)

    if not features:
        return raster

    shapes_vals = [
        (feat["geometry"], ANCIENT_WOODLAND_COST)
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
