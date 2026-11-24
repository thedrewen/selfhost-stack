# postgres-exporter

Exposes the statistics of the global [Postgres](../../../databases/postgres/README.md) (connections, transactions, cache hit ratio, locks, database sizes…) as Prometheus metrics. They are scraped by [Prometheus](../prometheus/README.md) and shown in [Grafana](../README.md).

## Setup

1. Make sure the `shared` Docker network exists (created by `install.sh`) and that [Postgres](../../../databases/postgres/README.md) is running.
2. Copy `.env.example` to `.env` and set the same `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB` as Postgres.
3. Start it: `docker compose up -d`.

## Behavior

- No port is published: metrics are only reachable from containers on the `shared` network (`postgres-exporter:9187`).
- It connects to the `postgres` host on the `shared` network, with TLS disabled (the traffic never leaves the Docker network).
- The per-database statistics (`pg_stat_database`) cover every database of the server, not only `POSTGRES_DB`.
- Dashboard: "PostgreSQL Exporter" (grafana.com ID `12485`) is provisioned automatically in Grafana (`../provisioning/dashboards/postgres.json`). Pick the instance and the database with the variables at the top.
