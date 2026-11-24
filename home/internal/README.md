# internal

Internal programs such as Traefik, Grafana, Postgres, etc. These are infrastructure services that are not developed by the user. Databases and exporters are only reachable on the internal `shared` network (or from the server itself); web services such as Grafana or Forgejo are exposed through Traefik.

Each service has its own folder with its Docker Compose configuration. The list below is a starting point: delete the services you do not need and add your own according to your needs.

## Available configurations

| Folder | Description |
| --- | --- |
| [`traefik/`](traefik/README.md) | Reverse proxy with automatic Let's Encrypt certificates |
| [`stalwart/`](stalwart/README.md) | Mail server |
| [`postgres/`](postgres/README.md) | PostgreSQL database, usable as a global Postgres for every service |
| [`redis/`](redis/README.md) | Redis cache/queue, usable as a global Redis for every service |
| [`grafana/`](grafana/README.md) | Dashboards and monitoring, with its related [Prometheus](grafana/prometheus/README.md), [node-exporter](grafana/node-exporter/README.md), [cAdvisor](grafana/cadvisor/README.md), [Loki](grafana/loki/README.md) and [Alloy](grafana/alloy/README.md) |
| [`forgejo-runner/`](forgejo-runner/README.md) | Runner for Forgejo Actions (CI/CD), with its own Docker-in-Docker |
| [`forgejo/`](forgejo/README.md) | Git forge (Forgejo) |
