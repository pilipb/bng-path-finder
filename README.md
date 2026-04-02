# BNG Path Planner

A full-stack web tool for calculating Biodiversity Net Gain (BNG) optimal routes in England. Drop two points on a map and the app fetches live habitat data from Natural England and Google Earth Engine, runs A* pathfinding weighted by BNG impact, and returns a scored route with a downloadable PDF report.


## The Idea

The problem is that in the UK to build an access road, the landowner must calculate the Biodiversity Net Gain (BNG) units as this is the value of the habitats that the development would be damaging and so the debt that the landowner will owe the government for the development. So if the road destroys more biodiversity than the landowner can "regrow" on their remaining land, they must buy off-site units. You can buy these onthe private market for anywhere between £15,000 and £30,000+ each, if no private units are available, the government sells them as a last resort. These can cost £42,000 to £125,000 per unit.

A route that avoids a high-value "Good Condition" oak grove in favor of a "Poor Condition" scrub patch could save the landowner hundreds of thousands of pounds in credit purchases alone.

The problem is that the current method for assessing this is through manual on site surveys so even getting a rough estimate requires an expert.

## The Thinking

## Reflections



## Setup

### Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| pnpm | latest | `npm install -g pnpm` |
| Python | 3.12+ | [python.org](https://python.org) |
| uv | latest | [docs.astral.sh/uv](https://docs.astral.sh/uv/) |

### 1. Backend

```bash
cd backend
cp .env.example .env   # then fill in your credentials (see backend/README.md)
uv sync
uv run uvicorn main:app --reload
```

API available at **http://localhost:8000** · Swagger docs at **http://localhost:8000/docs**

### 2. Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

App available at **http://localhost:5173**

> Both services must be running simultaneously — the frontend calls the backend directly at `http://localhost:8000`.

## Further Reading

- [`backend/README.md`](backend/README.md) — API endpoints, environment variables, architecture
- [`frontend/README.md`](frontend/README.md) — component structure, build commands
