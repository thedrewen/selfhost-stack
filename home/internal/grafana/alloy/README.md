# alloy

Log collector. It reads the logs of **every Docker container** and sends them to [Loki](../loki/README.md), so they can be searched in [Grafana](../README.md) (Explore > `Loki` data source).

## Setup

1. Make sure the `shared` Docker network exists (created by `install.sh`) and that Loki is running.
2. Start it: `docker compose up -d`.

## Behavior

- New containers are discovered automatically. Logs carry the labels `container`, `service` and `project` (the last two come from Docker Compose).
- Example query in Grafana: `{service="traefik"}`.
- No port is published.
- It mounts the Docker socket (`/var/run/docker.sock`). Even with `:ro`, this gives full control over Docker on the host: keep this service internal.
