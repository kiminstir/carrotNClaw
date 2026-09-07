# Carrot&Claw

Website for the Carrot&Claw tavern. Headless Wagtail CMS + SvelteKit frontend, deployed with Docker Compose behind Caddy.

## Requirements

- Docker with Compose v2
- [uv](https://docs.astral.sh/uv/) (Python 3.14 is installed automatically)
- Node 24 with pnpm (`corepack enable`)
- [just](https://github.com/casey/just)

## Quick start (development)

```bash
cp .env.example .env
just db                       # Postgres in Docker
cd backend && uv sync && cd ..
cd frontend && pnpm install && cd ..
just migrate
just bootstrap                # creates pages, settings and the admin user from .env
just dev                      # backend on :8000, frontend on :5173
```

Admin: http://localhost:8000/admin/ · Site: http://localhost:5173/

Sections on testing, deployment and editing content are filled in later in this plan (Task 13).
