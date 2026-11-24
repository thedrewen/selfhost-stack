# redis-exporter

Exposes the statistics of the global [Redis](../../../databases/redis/README.md) (memory, clients, commands per second, hit ratio, keys, evictions…) as Prometheus metrics. They are scraped by [Prometheus](../prometheus/README.md) and shown in [Grafana](../README.md).

## Setup

1. Make sure the `shared` Docker network exists (created by `install.sh`) and that [Redis](../../../databases/redis/README.md) is running.
2. Start it: `docker compose up -d`. No configuration is needed.
3. Restart Prometheus so it reads the `redis-exporter` job (`docker compose restart prometheus`, run in `../prometheus/`).

## Behavior

- No port is published: metrics are only reachable from containers on the `shared` network (`redis-exporter:9121`).
- It connects to `redis:6379` without a password, like every other service of the stack.
- Dashboard: "Redis Exporter Quickstart and Dashboard" (grafana.com ID `14091`) is provisioned automatically in Grafana (`../provisioning/dashboards/redis.json`).
