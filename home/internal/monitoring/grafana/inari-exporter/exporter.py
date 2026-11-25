"""Prometheus exporter for Inari (https://inari.thedrewen.com).

Inari has no native /metrics endpoint: this polls its public REST API
(/api/channels, /api/channels/<name>) instead and exposes the result as
Prometheus metrics, one Inari instance per request, in the same /probe
style as blackbox-exporter. Prometheus picks the instances to poll from
../prometheus/targets/inari.yml.
"""

import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from prometheus_client import CollectorRegistry, generate_latest
from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily

LISTEN_PORT = int(os.environ.get("INARI_EXPORTER_PORT", "9900"))
REQUEST_TIMEOUT = float(os.environ.get("INARI_EXPORTER_TIMEOUT", "5"))

# Per-target state (known channels, cumulative counters) and the lock guarding it.
# Kept in memory only: it resets if this process restarts.
_registry_lock = threading.Lock()
_state: dict[str, dict] = {}
_state_locks: dict[str, threading.Lock] = {}


def _lock_for(target: str) -> threading.Lock:
    with _registry_lock:
        if target not in _state_locks:
            _state_locks[target] = threading.Lock()
            _state[target] = {
                "channels": {},  # name -> {permanent, has_connector, clients_count}
                "created_total": 0,
                "deleted_total": 0,
                "user_seconds": {},  # (channel, display_name) -> cumulative seconds
                "connected_now": {},  # (channel, display_name, is_connector) -> client count
                "last_poll": None,
            }
        return _state_locks[target]


def _fetch_json(url: str):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        return json.loads(resp.read())


def probe(target: str) -> bytes:
    """Polls one Inari instance (its base URL) and returns the Prometheus exposition text for it."""
    start = time.monotonic()
    lock = _lock_for(target)

    try:
        channels = _fetch_json(f"{target}/api/channels")
        is_up = True
    except (urllib.error.URLError, OSError, ValueError):
        is_up = False
        channels = []

    # Fetched outside the lock: these are the slow network calls, and they only need the
    # current snapshot, not the shared state.
    details = {}
    if is_up:
        for channel in channels:
            if channel.get("clients_count", 0) > 0:
                name = channel["name"]
                try:
                    details[name] = _fetch_json(
                        f"{target}/api/channels/{urllib.parse.quote(name, safe='')}"
                    )
                except (urllib.error.URLError, OSError, ValueError):
                    pass  # channel may have emptied out between the two calls

    now = time.time()

    with lock:
        state = _state[target]

        if is_up:
            current_names = {channel["name"] for channel in channels}
            previous_names = set(state["channels"].keys())
            # On the very first poll of a target there is no baseline to diff against: every
            # channel already there would otherwise be counted as "created".
            is_first_poll = state["last_poll"] is None
            if not is_first_poll:
                state["created_total"] += len(current_names - previous_names)
                state["deleted_total"] += len(previous_names - current_names)

            elapsed = 0.0 if is_first_poll else max(0.0, now - state["last_poll"])
            state["last_poll"] = now

            new_channels = {}
            connected_now = {}
            for channel in channels:
                name = channel["name"]
                has_connector = bool(channel.get("has_connector", False))
                new_channels[name] = {
                    "permanent": bool(channel.get("permanent", False)),
                    "has_connector": has_connector,
                    "clients_count": int(channel.get("clients_count", 0)),
                }

                # The connector's presence comes from the channel's own has_connector flag, not
                # from the clients list: some Inari versions count it in clients_count and
                # has_connector but never actually list it among "clients" (always an empty
                # client entry for it, or none at all). Only one connector per channel is ever
                # allowed, so this is always exactly one row.
                if has_connector:
                    now_key = (name, "Connector", True)
                    connected_now[now_key] = connected_now.get(now_key, 0) + 1

                detail = details.get(name)
                if detail:
                    for client in detail.get("clients") or []:
                        if client.get("is_connector"):
                            continue  # already accounted for above, from has_connector
                        display_name = client.get("display_name", "")

                        now_key = (name, display_name, False)
                        connected_now[now_key] = connected_now.get(now_key, 0) + 1

                        if elapsed > 0:
                            seconds_key = (name, display_name)
                            state["user_seconds"][seconds_key] = (
                                state["user_seconds"].get(seconds_key, 0.0) + elapsed
                            )

            state["channels"] = new_channels
            state["connected_now"] = connected_now

        metrics = _build_metrics(target, is_up, state)

    metrics.append(
        _gauge(
            "inari_probe_duration_seconds",
            "Time spent polling the instance",
            target,
            time.monotonic() - start,
        )
    )

    registry = CollectorRegistry()
    registry.register(_StaticCollector(metrics))
    return generate_latest(registry)


def _gauge(name: str, doc: str, target: str, value: float) -> GaugeMetricFamily:
    family = GaugeMetricFamily(name, doc, labels=["target"])
    family.add_metric([target], value)
    return family


def _build_metrics(target: str, is_up: bool, state: dict) -> list:
    channels_total = len(state["channels"]) if is_up else 0
    clients_total = (
        sum(info["clients_count"] for info in state["channels"].values()) if is_up else 0
    )

    metrics = [
        _gauge(
            "inari_up",
            "Whether the instance answered /api/channels (1) or not (0)",
            target,
            1 if is_up else 0,
        ),
        _gauge("inari_channels_total", "Channels currently open", target, channels_total),
        _gauge(
            "inari_channel_clients_total",
            "Users currently connected across all channels",
            target,
            clients_total,
        ),
    ]

    channel_clients = GaugeMetricFamily(
        "inari_channel_clients",
        "Users currently connected in a channel",
        labels=["target", "channel", "permanent", "has_connector"],
    )
    for name, info in state["channels"].items():
        channel_clients.add_metric(
            [target, name, str(info["permanent"]).lower(), str(info["has_connector"]).lower()],
            info["clients_count"],
        )
    metrics.append(channel_clients)

    connected_now = GaugeMetricFamily(
        "inari_connected_user",
        'Users currently connected (usually 1, more if several share the same name); a '
        'connector always reports display_name="Connector"',
        labels=["target", "channel", "display_name", "is_connector"],
    )
    current = state.get("connected_now", {}) if is_up else {}
    for (channel, display_name, is_connector), count in current.items():
        connected_now.add_metric([target, channel, display_name, str(is_connector).lower()], count)
    metrics.append(connected_now)

    created_total = CounterMetricFamily(
        "inari_channels_created",
        "Channels seen appearing since the exporter started (non-permanent channels are "
        "created when their first user joins)",
        labels=["target"],
    )
    created_total.add_metric([target], state["created_total"])
    metrics.append(created_total)

    deleted_total = CounterMetricFamily(
        "inari_channels_deleted",
        "Channels seen disappearing since the exporter started (non-permanent channels are "
        "deleted when their last user leaves)",
        labels=["target"],
    )
    deleted_total.add_metric([target], state["deleted_total"])
    metrics.append(deleted_total)

    user_seconds = CounterMetricFamily(
        "inari_user_connected_seconds",
        "Cumulative time a display name has spent connected, since the exporter started",
        labels=["target", "channel", "display_name"],
    )
    for (channel, display_name), seconds in state["user_seconds"].items():
        user_seconds.add_metric([target, channel, display_name], seconds)
    metrics.append(user_seconds)

    return metrics


class _StaticCollector:
    """Wraps an already-built list of metric families as a one-shot collector."""

    def __init__(self, metrics: list):
        self._metrics = metrics

    def collect(self):
        return self._metrics


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # noqa: D401 - quiet the default access log
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/probe":
            query = urllib.parse.parse_qs(parsed.query)
            targets = query.get("target")
            if not targets:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"missing target parameter\n")
                return
            body = probe(targets[0].rstrip("/"))
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.end_headers()
            self.wfile.write(body)
        elif parsed.path in ("/", "/health"):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok\n")
        else:
            self.send_response(404)
            self.end_headers()


def main():
    server = ThreadingHTTPServer(("0.0.0.0", LISTEN_PORT), _Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
