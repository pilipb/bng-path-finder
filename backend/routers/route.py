from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import numpy as np

from pathfinding.grid import make_grid, wgs84_to_grid
from pathfinding.cost_raster import build_cost_raster
from pathfinding.astar import find_path
from pathfinding.smoother import smooth_path
from bng.calculator import calculate_segments
from layers.habitat_networks import get_habitat_raster

router = APIRouter(prefix="/api", tags=["route"])


class RouteRequest(BaseModel):
    point_a: tuple[float, float]  # [lat, lng]
    point_b: tuple[float, float]  # [lat, lng]


@router.post("/route")
async def calculate_route(req: RouteRequest, request: Request):
    """
    Calculate the BNG-optimal route between two points.
    """
    gee_available = getattr(request.app.state, "gee_available", False)

    try:
        # Build grid
        grid = make_grid(req.point_a, req.point_b)
        bbox = grid.bbox_wgs84

        # Build cost raster (fetches all layers in parallel)
        cost_raster, awi_mask, sssi_mask, lnrs_mask = build_cost_raster(
            grid, bbox, gee_available=gee_available
        )

        # Also get habitat raster for segment labelling
        habitat_d_raster, _ = get_habitat_raster(grid, bbox)

        # Find start/end grid positions
        start_rc = wgs84_to_grid(*req.point_a, grid)
        end_rc = wgs84_to_grid(*req.point_b, grid)

        # Run A*
        path_indices = find_path(cost_raster, start_rc, end_rc)

        if not path_indices:
            raise HTTPException(status_code=422, detail="No valid path found between points")

        # Smooth path
        smoothed_coords = smooth_path(path_indices, grid)

        # Calculate segments
        segments = calculate_segments(
            path_indices=path_indices,
            smoothed_coords=smoothed_coords,
            cost_raster=cost_raster,
            habitat_raster_raw=habitat_d_raster,
            awi_mask=awi_mask,
            sssi_mask=sssi_mask,
            lnrs_mask=lnrs_mask,
            grid=grid,
        )

        total_bng = sum(s["bng_units"] for s in segments)
        total_length = sum(s["length_m"] for s in segments)

        # Build GeoJSON LineString from smoothed coords
        route_geojson = {
            "type": "LineString",
            "coordinates": [[lng, lat] for lat, lng in smoothed_coords],
        }

        return {
            "route": route_geojson,
            "segments": segments,
            "total_bng_units": round(total_bng, 4),
            "total_length_m": round(total_length, 1),
            "cell_size_m": round(grid.cell_size_m, 1),
            "bbox_wgs84": list(bbox),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route calculation failed: {str(e)}")
