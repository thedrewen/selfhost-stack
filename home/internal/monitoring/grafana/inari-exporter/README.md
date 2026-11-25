# inari-exporter

Polls one or more [Inari](../../../games/inari/README.md) instances' public REST API (`/api/channels`, `/api/channels/<name>`) and exposes them as Prometheus metrics: active channels, connected users per channel, channels created/deleted over time, and per-user cumulative connection time. Inari has no `/metrics` endpoint of its own (neither `stable` nor `nightly`), so this stands in for one. Scraped by [Prometheus](../prometheus/README.md) and shown in [Grafana](../README.md).

## Setup

1. Make sure the `shared` Docker network exists (created by `install.sh`).
2. List the Inari instances to monitor (one base URL per instance, e.g. `https://inari.example.com`, no trailing slash) in `../prometheus/targets/inari.yml`. It is empty by default. Add your own instance ([`../../games/inari/README.md`](../../games/inari/README.md)) and/or any other Inari instance you want to track — several instances are supported, each identified by its own URL.
3. Build and start it: `docker compose up -d --build`.
4. Recreate Prometheus once so it mounts the `targets/` folder (`docker compose up -d`, run in `../prometheus/`). After that, editing `targets/inari.yml` is enough: Prometheus reloads it by itself within a minute.

## Behavior

- No port is published: it is only reachable from containers on the `shared` network (`inari-exporter:9900`), probed the same way as [blackbox-exporter](../blackbox-exporter/README.md) — one `GET /probe?target=<url>` request per instance listed in `targets/inari.yml`.
- Inari's `/api/channels` and `/api/channels/<name>` routes are public (no API key needed): the exporter only reads them, it never writes anything to Inari.
- Metrics (all labeled `target` with the instance's URL):
  - `inari_up`: whether the instance answered.
  - `inari_channels_total`: number of channels currently open.
  - `inari_channel_clients{channel,permanent,has_connector}`: users currently in each channel.
  - `inari_channel_clients_total`: users currently connected across all channels of that instance.
  - `inari_connected_user{channel,display_name,is_connector}`: snapshot of who is connected right now (value is normally `1`, higher only if several clients share the same name). A connector always reports `display_name="Connector"` (its real one is whatever the game plugin sent, not a player name) and `is_connector="true"`, so it still shows up as a row instead of being silently dropped.
  - `inari_channels_created_total` / `inari_channels_deleted_total`: channels seen appearing/disappearing since the exporter started (non-permanent channels are created when their first user joins and deleted when their last user leaves — that is how "channels created/deleted" shows up, since Inari's API has no history of its own).
  - `inari_user_connected_seconds_total{channel,display_name}`: cumulative time each display name has spent connected, since the exporter started (connectors are excluded from this one). Use `topk(10, inari_user_connected_seconds_total)` in Grafana for the most active users.
- Limitations, both from polling a snapshot API instead of receiving real events:
  - State (the counters above, and the per-user time) is kept in memory only: it resets if the `inari-exporter` container restarts. For history across restarts, rely on Prometheus' own storage (30 days by default, see [`../prometheus/README.md`](../prometheus/README.md)) rather than the exporter's own counters.
  - A user who connects and disconnects entirely between two scrapes is invisible, and one who disconnects shortly before a scrape gets no credit for that last interval: connected time is only added for users still present at scrape time, for the duration since the previous scrape. Conversely, someone who only just joined is credited with the whole interval since the previous scrape, as if they had been there the whole time — the exporter cannot tell when within that window they actually connected.
  - `display_name` is chosen by the user in-app and is not a stable identity: someone renaming shows up as a different series, and a busy public instance where names are reused a lot will grow this metric's cardinality. Fine for the small/self-hosted scale this stack targets.
- Dashboard: "Inari" is provisioned automatically in Grafana (`../provisioning/dashboards/inari.json`). Use the `target` variable to pick an instance.
