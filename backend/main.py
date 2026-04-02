import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# GEE initialisation (optional)
GEE_AVAILABLE = False

_GEE_SERVICE_ACCOUNT = os.getenv("GEE_SERVICE_ACCOUNT")
_GEE_CREDENTIALS_PATH = os.getenv("GEE_CREDENTIALS_PATH")

if _GEE_SERVICE_ACCOUNT and _GEE_CREDENTIALS_PATH:
    try:
        import ee  # type: ignore
        credentials = ee.ServiceAccountCredentials(_GEE_SERVICE_ACCOUNT, _GEE_CREDENTIALS_PATH)
        ee.Initialize(credentials)
        GEE_AVAILABLE = True
        print("[GEE] Initialized successfully")
    except Exception as e:
        print(f"[GEE] Could not initialize: {e}. Water layer will use fallback.")
else:
    print("[GEE] No credentials configured. Water layer disabled.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.gee_available = GEE_AVAILABLE
    yield


app = FastAPI(title="BNG Path Finder API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
    print("[main] report router not yet available")


@app.get("/")
def root():
    return {"message": "BNG Path Finder API", "gee_available": GEE_AVAILABLE}
