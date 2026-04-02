from concurrent.futures import ThreadPoolExecutor
import numpy as np

from pathfinding.grid import GridSpec
from layers.habitat_networks import get_habitat_raster
from layers.ancient_woodland import get_awi_raster
from layers.sssi_irz import get_sssi_raster
from layers.lnrs import get_lnrs_multiplier_raster
from layers.water import get_water_raster
from bng.weights import DISTINCTIVENESS_COST

MIN_COST = 1.0


def build_cost_raster(
    grid: GridSpec,
    bbox_wgs84: tuple[float, float, float, float],
    gee_available: bool = False,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Fetch all layers in parallel and assemble cost raster.

    Returns:
        cost_raster: (n_rows, n_cols) float32 — A* traversal cost
        awi_mask: (n_rows, n_cols) bool — True where ancient woodland
        sssi_mask: (n_rows, n_cols) bool — True where SSSI IRZ
        lnrs_mask: (n_rows, n_cols) bool — True where LNRS area
    """
    with ThreadPoolExecutor(max_workers=5) as ex:
        f_habitat = ex.submit(get_habitat_raster, grid, bbox_wgs84)
        f_awi     = ex.submit(get_awi_raster, grid, bbox_wgs84)
        f_sssi    = ex.submit(get_sssi_raster, grid, bbox_wgs84)
        f_lnrs    = ex.submit(get_lnrs_multiplier_raster, grid, bbox_wgs84)
        f_water   = ex.submit(get_water_raster, grid, bbox_wgs84, gee_available)

        habitat_raster, _ = f_habitat.result()
        awi_raster        = f_awi.result()
        sssi_raster       = f_sssi.result()
        lnrs_multiplier   = f_lnrs.result()
        water_raster      = f_water.result()

    # Convert habitat distinctiveness to cost
    habitat_cost = np.vectorize(lambda d: DISTINCTIVENESS_COST.get(int(d), 2.0))(habitat_raster)

    # Composite cost
    cost = (habitat_cost + sssi_raster + water_raster) * lnrs_multiplier
    cost = np.maximum(cost, MIN_COST).astype(np.float32)

    # Ancient woodland: very high cost (effectively impassable but A* can still route around)
    cost[awi_raster > 0] = awi_raster[awi_raster > 0]

    awi_mask  = awi_raster > 0
    sssi_mask = sssi_raster > 0
    lnrs_mask = lnrs_multiplier > 1.0

    return cost, awi_mask, sssi_mask, lnrs_mask
