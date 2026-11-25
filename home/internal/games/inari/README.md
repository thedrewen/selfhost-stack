# inari

Self-hosted proximity voice chat for games ([Inari](https://inari.thedrewen.com)), routed by Traefik. A connector on the game server (e.g. Minecraft) links the game to Inari.

## Setup

1. Make sure the `shared` Docker network exists (created by `install.sh`) and that [Traefik](../../routing/traefik/README.md) is running.
2. Copy `.env.example` to `.env` and set `INARI_DOMAIN`, `INARI_API_KEY` and `INARI_SERVER_PUBLIC_IP`.
3. Open port `44444` (UDP and TCP) in your firewall.
4. Start it: `docker compose up -d`.
5. Configure your game connector with `https://<INARI_DOMAIN>` and the same API key.

## Behavior

- The web page and the WebSocket (`/ws`) are exposed by Traefik on `https://$INARI_DOMAIN` with a Let's Encrypt certificate (container port `3030`). HTTPS is required: browsers only allow microphone access on secure origins.
- The WebRTC audio port `44444` (UDP and TCP) is published directly on the host: it cannot go through Traefik. `INARI_SERVER_PUBLIC_IP` must be the server's public IP, not the domain (and not the Cloudflare proxy if you use one).
- `INARI_API_KEY` must be set: otherwise Inari generates a new one at each start and the connector stops working.
- Each channel is an isolated voice space: use several channels to serve several game servers with one instance.
- Anonymous telemetry is enabled by default; set `INARI_DISABLE_TELEMETRY=true` to disable it.
- Reference: [configuration](https://inari.thedrewen.com/guides/configuration/) and [reverse proxy](https://inari.thedrewen.com/guides/reverse-proxy/).
- Monitoring: Inari has no `/metrics` endpoint, so [`inari-exporter`](../../monitoring/grafana/inari-exporter/README.md) polls its REST API instead and feeds a Grafana dashboard (channels, connected users, most active users). It can monitor this instance and any number of other Inari instances by URL — list them in `../../monitoring/grafana/prometheus/targets/inari.yml`.
