# grafana

Dashboards and monitoring UI, routed by Traefik.

## Setup

1. Make sure the `shared` Docker network exists (created by `install.sh`) and that [Traefik](../../routing/traefik/README.md) is running.
2. Copy `.env.example` to `.env` and set `GRAFANA_ADMIN_PASSWORD` and `GRAFANA_DOMAIN` (`GRAFANA_ADMIN_USER` defaults to `admin`).
3. Start it: `docker compose up -d`.

## Behavior

- Exposed by Traefik on `https://$GRAFANA_DOMAIN` with a Let's Encrypt certificate. The domain must have a DNS record pointing to the server.
- Sign-up is disabled: only the admin account (and users it creates) can log in.
- The admin user and password are only applied on the **first start**, when the `grafana-data` volume is empty. Change the password afterwards from the Grafana UI.
- Data (users, dashboards, settings) is stored in the `grafana-data` Docker volume and in an embedded SQLite database: Grafana does not need an external database. Back the volume up.
- The [Prometheus](prometheus/README.md) and [Loki](loki/README.md) data sources are provisioned automatically from `./provisioning/datasources`.
- Dashboards in `./provisioning/dashboards/` are loaded automatically (add other `.json` files there): the official [Traefik dashboard](https://grafana.com/grafana/dashboards/17346) (ID `17346`) the [Logs / App dashboard](https://grafana.com/grafana/dashboards/13639) (ID `13639`) for the Loki logs (pick the app with the `app` variable), the [Node Exporter Full dashboard](https://grafana.com/grafana/dashboards/1860) (ID `1860`) for the VPS and the [Cadvisor exporter dashboard](https://grafana.com/grafana/dashboards/14282) (ID `14282`) for the containers.
- Optional: Grafana can store its own data in the global [Postgres](../../databases/postgres/README.md) instead of SQLite (`GF_DATABASE_*` variables, host `postgres` on the `shared` network), or query it as a data source for dashboards. Neither is configured by default.

## Monitoring stack setup

Each service below has its own `compose.yaml`: run `docker compose up -d` in each folder. Only Grafana needs a `.env`; the other ones need no configuration. Start them in this order:

1. [`prometheus/`](prometheus/README.md) (needs Traefik running): stores the metrics and scrapes the targets listed in `prometheus/prometheus.yml`.
2. Exporters, which expose metrics for Prometheus (`node-exporter` and `cadvisor` need nothing else, Traefik already exposes its own):
   - [`node-exporter/`](node-exporter/README.md): VPS statistics (CPU, memory, disk, network). Dashboard provisioned.
   - [`cadvisor/`](cadvisor/README.md): per-container statistics. Dashboard provisioned.
3. [`loki/`](loki/README.md) then [`alloy/`](alloy/README.md): logs. Loki stores them, Alloy reads the logs of every container and sends them to Loki. Query them in Grafana, Explore > `Loki` (e.g. `{service="traefik"}`).
4. Grafana itself (this folder): the `Prometheus` and `Loki` data sources and all the dashboards (Traefik, Loki logs, VPS, containers) are already provisioned: nothing to import.

To monitor another service, add a job to `prometheus/prometheus.yml` with its exporter (`host:port` on the `shared` network) and restart Prometheus (`docker compose restart prometheus`, run in `prometheus/`).

## Related services

These services only exist to feed Grafana, so they live in this folder:

- [`prometheus/`](prometheus/README.md): metrics database (scrapes Traefik, node-exporter and cAdvisor).
- [`node-exporter/`](node-exporter/README.md): global VPS statistics.
- [`cadvisor/`](cadvisor/README.md): per-container statistics.
- [`loki/`](loki/README.md): logs database.
- [`alloy/`](alloy/README.md): collects the logs of every container and sends them to Loki.
