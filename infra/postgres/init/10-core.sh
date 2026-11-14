#!/bin/sh
# Creates core_db and its two roles (T-10, docs/06 D1.6).
# PostgreSQL runs this only once: when the data volume is empty.
#   core_owner: owns the schema; used only by migrations (MIGRATION_DATABASE_URL).
#   core_app:   used by the running service (DATABASE_URL); can read and write
#               rows but cannot create, alter or drop tables.
set -eu

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres \
  -v owner_password="$CORE_OWNER_PASSWORD" \
  -v app_password="$CORE_APP_PASSWORD" <<'SQL'
CREATE ROLE core_owner LOGIN PASSWORD :'owner_password';
CREATE ROLE core_app LOGIN PASSWORD :'app_password';

CREATE DATABASE core_db OWNER core_owner;
-- Only these roles may connect: other services' roles (e.g. auth) cannot.
REVOKE ALL ON DATABASE core_db FROM PUBLIC;
GRANT CONNECT ON DATABASE core_db TO core_app;

\connect core_db

-- The public schema belongs to the database owner (core_owner).
-- Nobody else can create objects in it; core_app may only use it.
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO core_app;

-- Every table or sequence that core_owner creates later (in migrations)
-- is automatically usable by core_app. Tables that must stay insert-only
-- (stock movements, audit) revoke UPDATE and DELETE in their own migration.
ALTER DEFAULT PRIVILEGES FOR ROLE core_owner IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO core_app;
ALTER DEFAULT PRIVILEGES FOR ROLE core_owner IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO core_app;
SQL
