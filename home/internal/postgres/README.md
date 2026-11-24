# postgres

PostgreSQL database shared by the other services of the stack.

## Setup

1. Make sure the `shared` Docker network exists (created by `install.sh`).
2. Copy `.env.example` to `.env` and set `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB`.
3. Start it: `docker compose up -d`.

## Behavior

- No port is published: the database is only reachable from containers on the `shared` network, with the host `postgres` and port `5432`.
- Data is stored in `./data`, mounted on `/var/lib/postgresql`: since PostgreSQL 18 the image stores data in a versioned subfolder (`/var/lib/postgresql/18/docker`), so mounting `/var/lib/postgresql/data` as before would not work. Back it up (e.g. with `pg_dump`).
- `POSTGRES_*` variables are only used on the **first start**, when `./data` is empty. Changing them afterwards does not change the existing user, password or database.
- The major version is pinned (`postgres:18`). Upgrading to another major version requires a dump/restore.

## Usage

Connect to the database from another container on the `shared` network:

```
postgresql://<POSTGRES_USER>:<POSTGRES_PASSWORD>@postgres:5432/<POSTGRES_DB>
```

Open a shell on the host:

```
docker compose exec postgres psql -U <POSTGRES_USER> -d <POSTGRES_DB>
```
