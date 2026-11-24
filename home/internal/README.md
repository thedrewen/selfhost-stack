# internal

Internal programs such as Traefik, Grafana, Postgres, etc. These are infrastructure services: they are not developed by the user and are not exposed directly.

Each service has its own folder with its Docker Compose configuration. The list below is a starting point: delete the services you do not need and add your own according to your needs.

## Available configurations

| Folder | Description |
| --- | --- |
| [`traefik/`](traefik/README.md) | Reverse proxy with automatic Let's Encrypt certificates |
| [`stalwart/`](stalwart/README.md) | Mail server |
| [`postgres/`](postgres/README.md) | PostgreSQL database |
