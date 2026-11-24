# grafana

Dashboards and monitoring UI, routed by Traefik.

## Setup

1. Make sure the `shared` Docker network exists (created by `install.sh`) and that [Traefik](../traefik/README.md) is running.
2. Copy `.env.example` to `.env` and set `GRAFANA_ADMIN_PASSWORD` and `GRAFANA_DOMAIN` (`GRAFANA_ADMIN_USER` defaults to `admin`).
3. Start it: `docker compose up -d`.

## Behavior

- Exposed by Traefik on `https://$GRAFANA_DOMAIN` with a Let's Encrypt certificate. The domain must have a DNS record pointing to the server.
- Sign-up is disabled: only the admin account (and users it creates) can log in.
- The admin user and password are only applied on the **first start**, when `./data` is empty. Change the password afterwards from the Grafana UI.
- Data is stored in `./data`. Back it up.
- The [Prometheus](prometheus/README.md) and [Loki](loki/README.md) data sources are provisioned automatically from `./provisioning/datasources`.
- Traefik dashboard: in Grafana, go to Dashboards > New > Import, enter the grafana.com ID `17346` ("Traefik Official Standalone Dashboard") and pick the `Prometheus` data source.
- VPS dashboard: import the grafana.com ID `1860` ("Node Exporter Full"), see [node-exporter](node-exporter/README.md).
- Grafana can use the global [Postgres](../postgres/README.md) as a data source (host `postgres` on the `shared` network).

## Monitoring stack setup

Each service below has its own `compose.yaml`: run `docker compose up -d` in each folder. Only Grafana needs a `.env`; the other ones need no configuration. Start them in this order:

1. [`prometheus/`](prometheus/README.md) (needs Traefik running): stores the metrics and scrapes the targets listed in `prometheus/prometheus.yml`.
2. Exporters, which expose metrics for Prometheus (`node-exporter` and `cadvisor` need nothing else, Traefik already exposes its own):
   - [`node-exporter/`](node-exporter/README.md): VPS statistics (CPU, memory, disk, network). Dashboard ID `1860`.
   - [`cadvisor/`](cadvisor/README.md): per-container statistics. Dashboard: a cAdvisor ID from grafana.com (for example `14282`).
3. [`loki/`](loki/README.md) then [`alloy/`](alloy/README.md): logs. Loki stores them, Alloy reads the logs of every container and sends them to Loki. Query them in Grafana, Explore > `Loki` (e.g. `{service="traefik"}`).
4. Grafana itself (this folder): the `Prometheus` and `Loki` data sources are already provisioned, then import the dashboards above (Dashboards > New > Import).

To monitor another service, add a job to `prometheus/prometheus.yml` with its exporter (`host:port` on the `shared` network) and restart Prometheus (`docker compose restart prometheus`).

## Related services

These services only exist to feed Grafana, so they live in this folder:

- [`prometheus/`](prometheus/README.md): metrics database (scrapes Traefik and node-exporter).
- [`node-exporter/`](node-exporter/README.md): global VPS statistics.
- [`cadvisor/`](cadvisor/README.md): per-container statistics.
- [`loki/`](loki/README.md): logs database.
- [`alloy/`](alloy/README.md): collects the logs of every container and sends them to Loki.
