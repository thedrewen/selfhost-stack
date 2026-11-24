# traefik

Reverse proxy of the stack. It routes HTTP/HTTPS traffic to the containers that opt in with labels, and gets TLS certificates from Let's Encrypt.

## Setup

1. Make sure the `shared` Docker network exists (created by `install.sh`, see the main README).
2. Copy `.env.example` to `.env` and set `ACME_EMAIL` (email used by Let's Encrypt for expiry notices).
3. Start it: `docker compose up -d`.

## Behavior

- Ports `80` and `443` are published. HTTP is permanently redirected to HTTPS.
- Certificates are issued by the Let's Encrypt resolver `le` (HTTP challenge) and stored in `./letsencrypt/acme.json`.
- Containers are **not** exposed by default (`exposedbydefault=false`): a container must set `traefik.enable=true` and be on the `shared` network.
- Extra static files (TLS options, middlewares…) can be put in `./dynamic/`; custom certificates in `./certs/`.
- The dashboard is only bound to `127.0.0.1:8080` and has no authentication (`api.insecure=true`). Reach it through an SSH tunnel: `ssh -L 8080:127.0.0.1:8080 <user>@<server>`, then open `http://localhost:8080`.
- Prometheus metrics are enabled on the dashboard entrypoint (`traefik:8080/metrics`) and scraped by [Prometheus](../../monitoring/grafana/prometheus/README.md), then shown in [Grafana](../../monitoring/grafana/README.md).

## Exposing a service

Add the service to the `shared` network and set labels in its own Compose file:

```yaml
services:
  app:
    image: my-image
    networks:
      - shared
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`app.example.com`)"
      - "traefik.http.routers.app.entrypoints=websecure"
      - "traefik.http.routers.app.tls.certresolver=le"
      - "traefik.http.services.app.loadbalancer.server.port=8080"

networks:
  shared:
    name: shared
    external: true
```

## Security note

Traefik mounts the Docker socket (`/var/run/docker.sock`), which gives it full control over Docker on the host. Keep this service limited to trusted setups.
