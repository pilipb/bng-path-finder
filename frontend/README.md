# BNG Path Planner — Frontend

React + TypeScript + Vite single-page application for the BNG Path Planner tool. Renders an interactive Leaflet map where users can drop two points and receive a BNG-optimal route with habitat scoring, cost breakdown, and a downloadable PDF report.

## Prerequisites

- Node.js 18+
- [`pnpm`](https://pnpm.io/) (`npm install -g pnpm`)

## Setup

```bash
cd frontend
pnpm install
```

## Development

```bash
pnpm dev
```

Starts the Vite dev server at **http://localhost:5173**.  
The app calls the backend at `http://localhost:8000` — make sure the backend is running before using the route/report features.

## Build

```bash
pnpm build     # type-check + production bundle → dist/
pnpm preview   # serve the production build locally
```

## Lint

```bash
pnpm lint
```

## Key Dependencies

| Package | Purpose |
|---------|---------|
| `react` / `react-dom` | UI framework |
| `leaflet` + `react-leaflet` | Interactive map |
| `vite` | Dev server and bundler |
| `typescript` | Type safety |

## Project Structure

```
frontend/
├── index.html              # Entry HTML — sets page title
├── public/
│   └── favicon.svg         # App icon
└── src/
    ├── main.tsx            # React root mount
    ├── App.tsx             # Top-level layout
    ├── types/
    │   └── api.ts          # Shared TypeScript types matching backend responses
    ├── components/
    │   ├── Header.tsx          # Top navigation bar
    │   ├── Sidebar.tsx         # Point picker, route controls
    │   ├── MapView.tsx         # Leaflet map wrapper
    │   ├── RouteLayer.tsx      # Draws route segments on the map
    │   ├── CostBreakdown.tsx   # Per-segment BNG unit table
    │   ├── ReportPanel.tsx     # PDF report download panel
    │   ├── InfoModal.tsx       # About / methodology modal
    │   └── DeveloperDetailsModal.tsx  # Official BNG form modal
    └── utils/
        └── geo.ts          # Formatting helpers (BNG units, length, colours)
```

## Connecting to the Backend

The frontend makes direct fetch calls to `http://localhost:8000`. There is no proxy configured — both services must be running simultaneously during development:

```bash
# Terminal 1 — backend
cd backend && uv run uvicorn main:app --reload

# Terminal 2 — frontend
cd frontend && pnpm dev
```
