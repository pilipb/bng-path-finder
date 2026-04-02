import logging
import requests
from typing import Any

logger = logging.getLogger(__name__)

# Known Natural England ArcGIS REST service URLs
# These use the standard NE AGOL organisation endpoint
NE_BASE = "https://services.arcgis.com/JJzESW51TqeY9uat/arcgis/rest/services"

LAYER_URLS = {
    "habitat_networks": f"{NE_BASE}/Priority_Habitats_Inventory_England/FeatureServer/0/query",
    "ancient_woodland": f"{NE_BASE}/Ancient_Woodland_England/FeatureServer/0/query",
    "sssi_irz": f"{NE_BASE}/SSSI_Impact_Risk_Zones_England/FeatureServer/0/query",
    "lnrs": f"{NE_BASE}/LNRS_Area/FeatureServer/0/query",
}


def fetch_layer(
    layer_key: str,
    bbox_wgs84: tuple[float, float, float, float],
    extra_params: dict[str, Any] | None = None,
) -> dict:
    """
    Fetch GeoJSON features from a Natural England ArcGIS REST Feature Service
    for the given WGS84 bounding box.
    Returns a GeoJSON FeatureCollection dict.
    """
    min_lng, min_lat, max_lng, max_lat = bbox_wgs84

    params: dict[str, Any] = {
        "f": "geojson",
        "geometry": f"{min_lng},{min_lat},{max_lng},{max_lat}",
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects",
        "inSR": "4326",   # query bbox is in WGS84
        "outSR": "27700", # return geometries in OSGB36 (metres) to match the raster grid CRS
        "outFields": "*",
        "resultRecordCount": 2000,
        "where": "1=1",
    }
    if extra_params:
        params.update(extra_params)

    url = LAYER_URLS.get(layer_key)
    if not url:
        raise ValueError(f"Unknown layer: {layer_key}")

    logger.debug("Fetching layer '%s' from %s", layer_key, url)
    for attempt in range(2):
        try:
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            # Some ArcGIS errors come back as 200 with an "error" key
            if "error" in data:
                raise RuntimeError(f"ArcGIS error for {layer_key}: {data['error']}")
            n_features = len(data.get("features", []))
            logger.debug("Layer '%s' returned %d features", layer_key, n_features)
            return data
        except (requests.RequestException, RuntimeError) as e:
            if attempt == 1:
                logger.warning("Could not fetch layer '%s': %s — returning empty FeatureCollection", layer_key, e)
                return {"type": "FeatureCollection", "features": []}

    return {"type": "FeatureCollection", "features": []}
