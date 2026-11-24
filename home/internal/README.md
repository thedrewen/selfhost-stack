# internal

Internal programs such as Traefik, Grafana, Postgres, etc. These are infrastructure services that are not developed by the user. Databases and exporters are only reachable on the internal `shared` network (or from the server itself); web services such as Grafana or Forgejo are exposed through Traefik.

Each service has its own folder with its Docker Compose configuration. The list below is a starting point: delete the services you do not need and add your own according to your needs.

## Available configurations

Services are grouped by category. Each folder has its own Compose configuration and README.

| Category | Folder | Description |
| --- | --- | --- |
| Routing | [`routing/traefik/`](routing/traefik/README.md) | Reverse proxy with automatic Let's Encrypt certificates |
| Git | [`git/forgejo/`](git/forgejo/README.md) | Git forge (Forgejo) |
| Git | [`git/forgejo-runner/`](git/forgejo-runner/README.md) | Runner for Forgejo Actions (CI/CD), with its own Docker-in-Docker |
| Databases | [`databases/postgres/`](databases/postgres/README.md) | PostgreSQL database, usable as a global Postgres for every service |
| Databases | [`databases/redis/`](databases/redis/README.md) | Redis cache/queue, usable as a global Redis for every service |
| Monitoring | [`monitoring/grafana/`](monitoring/grafana/README.md) | Dashboards and monitoring, with its related [Prometheus](monitoring/grafana/prometheus/README.md), [node-exporter](monitoring/grafana/node-exporter/README.md), [cAdvisor](monitoring/grafana/cadvisor/README.md), [postgres-exporter](monitoring/grafana/postgres-exporter/README.md), [redis-exporter](monitoring/grafana/redis-exporter/README.md), [blackbox-exporter](monitoring/grafana/blackbox-exporter/README.md), [Loki](monitoring/grafana/loki/README.md) and [Alloy](monitoring/grafana/alloy/README.md) |
| Mail | [`mail/stalwart/`](mail/stalwart/README.md) | Mail server |
| Games | [`games/inari/`](games/inari/README.md) | Proximity voice chat for games (Inari) |
