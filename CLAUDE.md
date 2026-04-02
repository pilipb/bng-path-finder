# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Parallel Agents

Multiple agents may be working simultaneously. If you see build errors in files you did NOT edit, do not try to fix them. Wait 30 seconds and retry the build — the other agent is likely mid-edit.

## Project Overview

**bng-path-finder** is a Biodiversity Net Gain (BNG) path finder tool — a full-stack web application with a React (Vite + TypeScript) frontend and a Python FastAPI backend.

## Development Commands

### Frontend (`frontend/`)

```bash
pnpm install         # install dependencies
pnpm dev             # start dev server at http://localhost:5173
pnpm build           # production build
pnpm lint            # run ESLint
pnpm preview         # preview production build
```

### Backend (`backend/`)

```bash
# Dependencies are managed with uv
uv sync              # install/sync dependencies

# Run dev server with auto-reload at http://localhost:8000
uv run uvicorn main:app --reload
```

API docs are auto-generated at `http://localhost:8000/docs`.

## Architecture

```
bng-path-finder/
├── frontend/    # Vite + React + TypeScript SPA
└── backend/     # FastAPI application
```

**Frontend** is a standard Vite React TypeScript app. `src/` contains components, pages, and assets. The dev server proxies or calls the backend directly at `http://localhost:8000`.

**Backend** (`backend/main.py`) is the FastAPI entry point. CORS is configured to allow requests from the Vite dev server (`localhost:5173`). Add new routers as the app grows using `app.include_router(...)`.

The two services are run independently — there is no monorepo tooling or shared build step.
