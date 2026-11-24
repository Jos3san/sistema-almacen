#!/bin/sh
# Creates auth_db and its two roles (T-12, docs/06 D1.6). Same pattern as 10-core.sh.
# PostgreSQL runs this only once: when the data volume is empty.
#   auth_owner: owns the schema; used only by migrations.
#   auth_app:   used by the running auth service; rows only.
# core's roles cannot connect to auth_db, and auth's roles cannot connect to core_db.
set -eu

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres \
  -v owner_password="$AUTH_OWNER_PASSWORD" \
  -v app_password="$AUTH_APP_PASSWORD" <<'SQL'
CREATE ROLE auth_owner LOGIN PASSWORD :'owner_password';
CREATE ROLE auth_app LOGIN PASSWORD :'app_password';

CREATE DATABASE auth_db OWNER auth_owner;
REVOKE ALL ON DATABASE auth_db FROM PUBLIC;
GRANT CONNECT ON DATABASE auth_db TO auth_app;

\connect auth_db

REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO auth_app;

ALTER DEFAULT PRIVILEGES FOR ROLE auth_owner IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO auth_app;
ALTER DEFAULT PRIVILEGES FOR ROLE auth_owner IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO auth_app;
SQL
