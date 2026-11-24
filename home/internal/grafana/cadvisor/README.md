# cadvisor

Exposes the CPU, memory, network and disk usage of **each Docker container** as Prometheus metrics. They are scraped by [Prometheus](../prometheus/README.md) and shown in [Grafana](../README.md). For the statistics of the VPS itself, see [node-exporter](../node-exporter/README.md).

## Setup

1. Make sure the `shared` Docker network exists (created by `install.sh`).
2. Start it: `docker compose up -d`.

## Behavior

- No port is published: metrics are only reachable from containers on the `shared` network (`cadvisor:8080`).
- Only Docker containers are reported (`--docker_only=true`).
- It runs `privileged` with read-only mounts of the host to read the containers' cgroups. Keep it internal.
- Dashboard: "Cadvisor exporter" (grafana.com ID `14282`) is provisioned automatically in Grafana (`../provisioning/dashboards/cadvisor.json`).
