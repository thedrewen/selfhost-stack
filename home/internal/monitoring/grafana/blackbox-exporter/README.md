# blackbox-exporter

Probes your public sites from the server: availability, response time, HTTP status and **TLS certificate expiry**. Prometheus asks it to check each URL listed in `../prometheus/targets/blackbox.yml`, and [Grafana](../README.md) shows the result.

## Setup

1. Make sure the `shared` Docker network exists (created by `install.sh`).
2. List the sites to probe (one URL per site you host) in `../prometheus/targets/blackbox.yml`. It is empty by default.
3. Start it: `docker compose up -d`.
4. Recreate Prometheus once so it mounts the `targets/` folder (`docker compose up -d`, run in `../prometheus/`). After that, editing `targets/blackbox.yml` is enough: Prometheus reloads it by itself within a minute.

## Behavior

- No port is published: it is only reachable from containers on the `shared` network (`blackbox-exporter:9115`).
- `http_2xx` (`config.yml`): HTTPS required, redirects followed, 10 s timeout. Used by the `blackbox` job (`../prometheus/targets/blackbox.yml`).
- `icmp` (`config.yml`): ping, 5 s timeout. Used by the `blackbox-icmp` job (`../prometheus/targets/icmp.yml`, one IP or hostname per line, no `https://`). The compose file sets `net.ipv4.ping_group_range` so the non-root user of the image can send pings. Ping the real IP of a server: a domain proxied by Cloudflare would only ping Cloudflare.
- Add other modules there (TCP, DNS…) and reference them from `prometheus.yml`.
- The probes go through the server's public address, so they also test DNS and Traefik, as a visitor would.
- Dashboard: "Blackbox Exporter (HTTP + ICMP)" (based on grafana.com ID `13659`) is provisioned automatically in Grafana (`../provisioning/dashboards/blackbox.json`). It has an HTTP section and an ICMP (ping) section; use the `job` and `instance` variables to pick a target.
