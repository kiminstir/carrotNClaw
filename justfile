set shell := ["bash", "-cu"]
set dotenv-load := true

export COREPACK_ENABLE_DOWNLOAD_PROMPT := "0"

default:
    @just --list

# --- local development -------------------------------------------------------

# Start only Postgres for local development
db:
    docker compose -f docker-compose.dev.yml up -d --wait db

# Run the Django dev server
backend: db
    cd backend && uv run python manage.py runserver 0.0.0.0:8000

# Run the SvelteKit dev server
frontend:
    cd frontend && pnpm dev

# Run Postgres, backend and frontend together (Ctrl+C stops all)
dev: db
    trap 'kill 0' EXIT; \
    (cd backend && uv run python manage.py runserver 0.0.0.0:8000) & \
    (cd frontend && pnpm dev) & \
    wait

migrate: db
    cd backend && uv run python manage.py migrate

makemigrations *ARGS: db
    cd backend && uv run python manage.py makemigrations {{ARGS}}

# Create the initial pages, settings and superuser (idempotent)
bootstrap: db
    cd backend && uv run python manage.py bootstrap_site

shell: db
    cd backend && uv run python manage.py shell

# --- quality -----------------------------------------------------------------

lint:
    cd backend && uv run ruff check . && uv run ruff format --check .
    cd frontend && pnpm lint && pnpm check

fmt:
    cd backend && uv run ruff check --fix . && uv run ruff format .
    cd frontend && pnpm format

test: db
    cd backend && uv run pytest
    cd frontend && pnpm test

test-backend *ARGS: db
    cd backend && uv run pytest {{ARGS}}

test-frontend:
    cd frontend && pnpm test

# End-to-end smoke test (needs `just backend` running in another terminal)
e2e:
    cd frontend && pnpm exec playwright test

# --- full stack --------------------------------------------------------------

up:
    docker compose up -d --build

down:
    docker compose down

logs *ARGS:
    docker compose logs -f {{ARGS}}
