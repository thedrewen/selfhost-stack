# loki

Logs database. It stores the logs of every container, sent by [Alloy](../alloy/README.md), and is used as a data source by [Grafana](../README.md).

## Setup

1. Make sure the `shared` Docker network exists (created by `install.sh`).
2. Start it: `docker compose up -d`.

## Behavior

- No port is published: it is only reachable from containers on the `shared` network (host `loki`, port `3100`).
- Logs are kept for 30 days (`retention_period` in `config.yaml`) in the `loki_data` Docker volume.
- No authentication: keep it internal.
