# prometheus

Metrics database. It scrapes the [Traefik](../../../routing/traefik/README.md) metrics, the VPS statistics from [node-exporter](../node-exporter/README.md) and the per-container statistics from [cAdvisor](../cadvisor/README.md), and is used as a data source by [Grafana](../README.md).

## Setup

1. Make sure the `shared` Docker network exists (created by `install.sh`) and that Traefik is running.
2. Start it: `docker compose up -d`.

## Behavior

- No port is published: it is only reachable from containers on the `shared` network (host `prometheus`, port `9090`).
- Scrape targets are listed in `prometheus.yml`. Add a job there to monitor another service, then restart the container.
- The sites probed by [blackbox-exporter](../blackbox-exporter/README.md) are listed in `targets/blackbox.yml` (empty by default). This file is reloaded automatically within a minute: no restart needed. Use the same mechanism (`file_sd_configs`) for any other list of targets that changes often.
- The Inari instances probed by [inari-exporter](../inari-exporter/README.md) are listed the same way, in `targets/inari.yml` (empty by default).
- Metrics are kept for 30 days in the `prometheus_data` Docker volume.
