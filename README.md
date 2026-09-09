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
| `just lint` | Ruff check, Prettier check, ESLint, svelte-check |
| `just fmt` | Ruff format/fix and Prettier write |
| `just e2e` | Playwright smoke test (needs `just backend` running) |
| `just makemigrations` / `just migrate` | Django migrations |
| `just up` / `just down` / `just logs` | Full production-like stack |

## Deployment

Pushes to `develop` run `.github/workflows/develop.yml`: tests, then both images are built on the runner and pushed to GHCR, then the server pulls them and restarts (`main` will do the same for production once that server exists). The reusable pipeline in `deploy.yml` reads everything host-specific from a GitHub Environment of the same name, so `develop` and `production` use identical variable names with different values:

| Kind | Name | Example |
|---|---|---|
| variable | `SITE_DOMAIN` | `dev.example.com` |
| variable | `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_PATH` | `example.com`, `deploy`, `/srv/carrotnclaw` |
| variable | `DEPLOY_KNOWN_HOSTS` | output of `ssh-keyscan -t ed25519 <host>` |
| variable | `POSTGRES_DB`, `POSTGRES_USER` | `carrot` |
| variable | `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL` | |
| variable | `GUNICORN_WORKERS`, `CADDY_HTTP_LISTEN`, `CADDY_HTTPS_LISTEN` | optional, see `.env.example` |
| secret | `DEPLOY_SSH_KEY` | private key whose public half is in the deploy user's `authorized_keys` |
| secret | `DJANGO_SECRET_KEY`, `POSTGRES_PASSWORD`, `DJANGO_SUPERUSER_PASSWORD` | |

Images are tagged `sha-<short sha>` and `<environment>`. To roll back, re-run the workflow for an older commit, or on the server edit `BACKEND_IMAGE`/`FRONTEND_IMAGE` in `.env` and run `docker compose up -d --no-build`.

### Server requirements

- Docker with the Compose plugin; a non-root user in the `docker` group that owns the deploy directory.
- Ports 80 and 443 reachable. If another service already owns 443 on the host, route TLS by SNI to Caddy (nginx `stream` with `ssl_preread` and `proxy_protocol on`) and set `CADDY_HTTPS_LISTEN=127.0.0.1:4443`; the Caddyfile accepts PROXY protocol from private addresses so client IPs are preserved.
- DNS for `SITE_DOMAIN` pointing at the server before the first deploy; Caddy obtains the certificate automatically.

### Manual deploy

`cp .env.example .env`, set `SITE_DOMAIN`, `DEBUG=false`, a long `DJANGO_SECRET_KEY`, strong `POSTGRES_PASSWORD` and `DJANGO_SUPERUSER_PASSWORD`, then `docker compose up -d --build`.

### Backups

The `pgdata` volume (database) and `media` volume (uploads). Database: `docker compose exec db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > backup.sql` (runs inside the container, where those variables are set). Media: `docker run --rm -v carrotnclaw_media:/data -v "$PWD":/backup alpine tar czf /backup/media.tgz -C /data .` — Compose prefixes volume names with the project directory name, so check the real name first with `docker volume ls | grep media`.

## Editing content (for editors)

Log in at `https://<domain>/admin/`.

- **Pages** → every page is built from blocks: Hero, Rich text, Image, Image slider, Collapse, Video (paste a YouTube/Vimeo URL), Columns, Card grid (use for menu items and staff). Add a page with "Add child page" under the home page; it appears once you add it to the header menu.
- **Settings → Header**: logo, site title, menu links.
- **Settings → Footer**: text, links, copyright line.
- **Settings → Music**: upload audio files (mp3/ogg/m4a) as Documents and add them as tracks; toggle the player on/off and set volume.
- **Preview** in the page editor opens the real site with your unpublished changes. **Publish** makes changes live immediately.

## Architecture

Headless Wagtail exposes pages and settings as JSON (`/api/v2/…`). SvelteKit renders pages on the server from that JSON and maps each block type to a component in `frontend/src/lib/blocks/`. Caddy fronts everything: `/admin`, `/api`, `/django-admin`, `/documents` go to Django; `/media` and `/static` are served from volumes; everything else goes to SvelteKit. Block definitions live in `backend/apps/pages/blocks.py` and their TypeScript mirror in `frontend/src/lib/api/types.ts`; keep them in sync.
