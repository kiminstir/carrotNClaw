-- Error-tracking database for the Bugsink container. Runs automatically when Postgres initialises
-- a fresh volume (docker-entrypoint-initdb.d) and is piped through psql on every deploy for
-- volumes that predate it, so it must stay idempotent.
SELECT 'CREATE DATABASE bugsink'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'bugsink')\gexec
