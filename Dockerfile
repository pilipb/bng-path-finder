FROM python:3.12-slim

RUN pip install uv --no-cache-dir

# Native libs required by geopandas/rasterio
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgdal-dev gdal-bin libgeos-dev libproj-dev libspatialindex-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/pyproject.toml backend/uv.lock* ./

RUN uv pip install --system --no-cache -r pyproject.toml

COPY backend/ .

ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
