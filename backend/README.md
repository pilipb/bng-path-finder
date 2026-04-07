# BNG Path Planner — Backend

FastAPI backend that calculates Biodiversity Net Gain (BNG) optimal routes between two points in England. It fetches habitat and environmental constraint data from Natural England ArcGIS services and Google Earth Engine, builds a cost raster, runs A* pathfinding, and returns scored route segments.

## Prerequisites

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) (dependency manager)

## Setup

```bash
cd backend
uv sync
```

This installs all dependencies into a local `.venv`.

## Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Required for the water/GEE layer. Without these the water layer is disabled
# and the route is calculated using land-only data.
GEE_SERVICE_ACCOUNT=your-service-account@project.iam.gserviceaccount.com
GEE_CREDENTIALS_PATH=/path/to/credentials.json

# Required for PDF reports, summary and recommendations
ANTHROPIC_API_KEY=sk-ant-...
```

If `GEE_SERVICE_ACCOUNT` / `GEE_CREDENTIALS_PATH` are not set, the app starts normally but logs a warning and skips the water layer.

## Running

```bash
uv run uvicorn main:app --reload
```

The API is available at **http://localhost:8000**.  
Interactive docs (Swagger UI) are at **http://localhost:8000/docs**.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check — returns API name and GEE status |
| `POST` | `/api/route` | Calculate BNG-optimal route between two lat/lng points |
| `POST` | `/api/report` | Generate a PDF report for a calculated route |
| `POST` | `/api/form` | Submit developer details for the official BNG form |

### `POST /api/route`

**Request body:**
```json
{
  "point_a": [51.505, -0.09],
  "point_b": [51.51, -0.1]
}
```

**Response:** GeoJSON `LineString` route, array of scored segments (habitat type, condition, BNG units, length), totals, and grid metadata.

## Architecture

```
backend/
├── main.py               # FastAPI app, CORS, GEE init, router registration
├── pyproject.toml        # uv/pip dependencies
├── .env                  # local secrets (not committed)
├── routers/
│   ├── route.py          # POST /api/route — pathfinding orchestration
│   ├── report.py         # POST /api/report — PDF generation
│   └── form.py           # POST /api/form — BNG form submission
├── layers/               # Natural England data fetchers (ArcGIS REST + GEE)
│   ├── base.py           # Shared ArcGIS fetch helper
│   ├── habitat_networks.py
│   ├── ancient_woodland.py
│   ├── sssi_irz.py
│   ├── lnrs.py
│   └── water.py          # Google Earth Engine water layer
├── pathfinding/          # Grid construction, cost raster, A*, path smoother
├── bng/                  # BNG unit calculator
└── report/               # PDF report builder (builder.py)
```

### Data Sources

| Layer | Source |
|-------|--------|
| Priority Habitats | Natural England ArcGIS (Priority Habitats Inventory) |
| Ancient Woodland | Natural England ArcGIS |
| SSSI Impact Risk Zones | Natural England ArcGIS |
| Local Nature Recovery Strategies | Natural England ArcGIS |
| Water bodies | Google Earth Engine (JRC Global Surface Water) |
