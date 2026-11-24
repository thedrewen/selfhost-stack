# blackbox-exporter

Probes your public sites from the server: availability, response time, HTTP status and **TLS certificate expiry**. Prometheus asks it to check each URL listed in `../prometheus/targets/blackbox.yml`, and [Grafana](../README.md) shows the result.

## Setup

1. Make sure the `shared` Docker network exists (created by `install.sh`).
2. List the sites to probe (one URL per site you host) in `../prometheus/targets/blackbox.yml`. It is empty by default.
3. Start it: `docker compose up -d`.
4. Recreate Prometheus once so it mounts the `targets/` folder (`docker compose up -d`, run in `../prometheus/`). After that, editing `targets/blackbox.yml` is enough: Prometheus reloads it by itself within a minute.

## Behavior

- No port is published: it is only reachable from containers on the `shared` network (`blackbox-exporter:9115`).
- The only module is `http_2xx` (`config.yml`): HTTPS required, redirects followed, 10 s timeout. Add other modules there (TCP, DNS, ICMP…) and reference them from `prometheus.yml`.
- The probes go through the server's public address, so they also test DNS and Traefik, as a visitor would.
- Dashboard: "Blackbox Exporter (HTTP prober)" (grafana.com ID `13659`) is provisioned automatically in Grafana (`../provisioning/dashboards/blackbox.json`). Use the `job` and `instance` variables to pick a site.
