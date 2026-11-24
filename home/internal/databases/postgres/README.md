# postgres

PostgreSQL database that can be used as a global Postgres by every service of the stack: create one database (and ideally one user) per service instead of running one Postgres per project. Any service, whether internal (such as [Stalwart](../../mail/stalwart/README.md)) or developed by you (`home/prod/`), can use it as its database: just join the `shared` network.

## Setup

1. Make sure the `shared` Docker network exists (created by `install.sh`).
2. Copy `.env.example` to `.env` and set `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB`.
3. Start it: `docker compose up -d`.

## Behavior

- The database is only reachable from containers on the `shared` network (host `postgres`, port `5432`) and from the server itself on `127.0.0.1:5432`. It is never exposed to the internet: do not change the port binding to `0.0.0.0`. To reach it from your computer, use an SSH tunnel: `ssh -L 5432:127.0.0.1:5432 <user>@<server>`.
- Data is stored in `./data`, mounted on `/var/lib/postgresql`. Since PostgreSQL 18 the image sets `PGDATA` to a version-specific folder (`/var/lib/postgresql/<major>/docker`, e.g. `/var/lib/postgresql/19/docker`) and its volume is `/var/lib/postgresql`, so mounting `/var/lib/postgresql/data` as before would not work. Mounting the parent folder also allows the faster `pg_upgrade --link` when upgrading between major versions. Back it up (e.g. with `pg_dump`).
- `POSTGRES_*` variables are only used on the **first start**, when `./data` is empty. Changing them afterwards does not change the existing user, password or database.
- The major version is pinned (`postgres:19`). Upgrading to another major version requires a dump/restore or `pg_upgrade`.

## Usage

Connect to the database from another container on the `shared` network:

```
postgresql://<POSTGRES_USER>:<POSTGRES_PASSWORD>@postgres:5432/<POSTGRES_DB>
```

Open a shell on the host:

```
docker compose exec postgres psql -U <POSTGRES_USER> -d <POSTGRES_DB>
```

Create a dedicated database and user for a service:

```
docker compose exec postgres psql -U <POSTGRES_USER> -d <POSTGRES_DB> \
  -c "CREATE USER myapp WITH PASSWORD '<password>';" \
  -c "CREATE DATABASE myapp OWNER myapp;"
```
