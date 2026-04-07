import os
import logging
import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
})

logger = logging.getLogger(__name__)

# GEE initialisation (optional)
GEE_AVAILABLE = False

_GEE_SERVICE_ACCOUNT = os.getenv("GEE_SERVICE_ACCOUNT")
_GEE_CREDENTIALS_PATH = os.getenv("GEE_CREDENTIALS_PATH")
_GEE_CREDENTIALS_JSON = os.getenv("GEE_CREDENTIALS_JSON")  # Cloud Run: full JSON content

if _GEE_CREDENTIALS_JSON and not _GEE_CREDENTIALS_PATH:
    import tempfile
    import json as _json
    _tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    _tmp.write(_GEE_CREDENTIALS_JSON)
    _tmp.flush()
    _tmp.close()
    _GEE_CREDENTIALS_PATH = _tmp.name
    if not _GEE_SERVICE_ACCOUNT:
        try:
            _GEE_SERVICE_ACCOUNT = _json.loads(_GEE_CREDENTIALS_JSON).get("client_email")
        except Exception:
            pass

if _GEE_SERVICE_ACCOUNT and _GEE_CREDENTIALS_PATH:
    try:
        import ee  # type: ignore
        credentials = ee.ServiceAccountCredentials(_GEE_SERVICE_ACCOUNT, _GEE_CREDENTIALS_PATH)
        ee.Initialize(credentials)
        GEE_AVAILABLE = True
        logger.info("GEE initialized successfully")
    except Exception as e:
        logger.warning("GEE could not initialize: %s. Water layer will use fallback.", e)
else:
    logger.info("GEE: no credentials configured — water layer disabled")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.gee_available = GEE_AVAILABLE
    yield


app = FastAPI(title="BNG Path Finder API", lifespan=lifespan)

_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
_allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers.route import router as route_router  # noqa: E402

app.include_router(route_router)

try:
    from routers.report import router as report_router  # noqa: E402
    app.include_router(report_router)
except ImportError:
    logger.warning("Report router not yet available — skipping")

try:
    from routers.form import router as form_router  # noqa: E402
    app.include_router(form_router)
except ImportError:
    print("[main] form router not yet available")

try:
    from routers.recommendations import router as recommendations_router  # noqa: E402
    app.include_router(recommendations_router)
except ImportError:
    logger.warning("Recommendations router not yet available — skipping")


@app.get("/")
def root():
    return {"message": "BNG Path Finder API", "gee_available": GEE_AVAILABLE}
