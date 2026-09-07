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

## Everyday commands

| Command | What it does |
|---|---|
| `just dev` | Postgres + Django dev server (:8000) + SvelteKit dev server (:5173) |
| `just test` | Backend pytest and frontend vitest |
| `just lint` / `just fmt` | Ruff, ESLint, Prettier, svelte-check |
| `just e2e` | Playwright smoke test (needs `just backend` running) |
| `just makemigrations` / `just migrate` | Django migrations |
| `just up` / `just down` / `just logs` | Full production-like stack |

## Deployment (single VPS)

1. Install Docker with the Compose plugin, clone the repo, `cp .env.example .env`.
2. Set `SITE_DOMAIN` to your domain (DNS A/AAAA records must point at the server), a long `DJANGO_SECRET_KEY`, `DEBUG=false`, strong `POSTGRES_PASSWORD` and `DJANGO_SUPERUSER_PASSWORD`.
3. `docker compose up -d --build`. Caddy obtains the HTTPS certificate automatically.
4. Updates: `git pull && docker compose up -d --build`.
5. Backups: the `pgdata` volume (database) and `media` volume (uploads). Example: `docker compose exec db pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup.sql`.

## Editing content (for editors)

Log in at `https://<domain>/admin/`.

- **Pages** → every page is built from blocks: Hero, Rich text, Image, Image slider, Collapse, Video (paste a YouTube/Vimeo URL), Columns, Card grid (use for menu items and staff). Add a page with "Add child page" under the home page; it appears once you add it to the header menu.
- **Settings → Header**: logo, site title, menu links.
- **Settings → Footer**: text, links, copyright line.
- **Settings → Music**: upload audio files (mp3/ogg/m4a) as Documents and add them as tracks; toggle the player on/off and set volume.
- **Preview** in the page editor opens the real site with your unpublished changes. **Publish** makes changes live immediately.

## Architecture

Headless Wagtail exposes pages and settings as JSON (`/api/v2/…`). SvelteKit renders pages on the server from that JSON and maps each block type to a component in `frontend/src/lib/blocks/`. Caddy fronts everything: `/admin`, `/api`, `/django-admin`, `/documents` go to Django; `/media` and `/static` are served from volumes; everything else goes to SvelteKit. Block definitions live in `backend/apps/pages/blocks.py` and their TypeScript mirror in `frontend/src/lib/api/types.ts`; keep them in sync.
