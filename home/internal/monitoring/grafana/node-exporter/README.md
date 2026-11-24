# node-exporter

Exposes the global statistics of the VPS (CPU, memory, disk, network, load…) as Prometheus metrics. They are scraped by [Prometheus](../prometheus/README.md) and shown in [Grafana](../README.md).

## Setup

1. Make sure the `shared` Docker network exists (created by `install.sh`).
2. Start it: `docker compose up -d`.

## Behavior

- No port is published: metrics are only reachable from containers on the `shared` network (`node-exporter:9100`).
- The host filesystem is mounted read-only at `/host` so disk statistics reflect the VPS and not the container.
- Dashboard: "Node Exporter Full" (grafana.com ID `1860`) is provisioned automatically in Grafana (`../provisioning/dashboards/node-exporter.json`).
