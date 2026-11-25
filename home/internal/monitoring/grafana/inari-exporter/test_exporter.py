"""Manual test for exporter.py: run with `python3 test_exporter.py`.

Starts a tiny mock of Inari's /api/channels and /api/channels/<name> routes, then calls
probe() against it directly (no need to run the exporter's own HTTP server) and checks the
metrics it returns, including state that only shows up across several polls (channel
created/deleted counters, per-user connected time).
"""

import json
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

import exporter

CHANNELS_ROUND_1 = [
    {"name": "default", "has_connector": True, "clients_count": 2, "permanent": True},
]
CLIENTS_ROUND_1 = {
    "default": {
        "name": "default",
        "has_connector": True,
        "clients_count": 2,
        "permanent": True,
        "clients": [
            {
                "display_name": "Alice",
                "is_force_muted": False,
                "is_force_deafened": False,
                "is_muted": False,
                "is_deafened": False,
                "head_orientation": [0, 0, 0],
                "is_connector": False,
            },
            {
                "display_name": "connector-bot",
                "is_force_muted": False,
                "is_force_deafened": False,
                "is_muted": False,
                "is_deafened": False,
                "head_orientation": [0, 0, 0],
                "is_connector": True,
            },
        ],
    },
}

# Round 2: "default" lost its only human, a new ephemeral channel "squad-1" appeared.
CHANNELS_ROUND_2 = [
    {"name": "default", "has_connector": True, "clients_count": 0, "permanent": True},
    {"name": "squad-1", "has_connector": False, "clients_count": 1, "permanent": False},
]
CLIENTS_ROUND_2 = {
    "squad-1": {
        "name": "squad-1",
        "has_connector": False,
        "clients_count": 1,
        "permanent": False,
        "clients": [
            {
                "display_name": "Bob",
                "is_force_muted": False,
                "is_force_deafened": False,
                "is_muted": False,
                "is_deafened": False,
                "head_orientation": [0, 0, 0],
                "is_connector": False,
            },
        ],
    },
}

# Round 3: "squad-1" is gone too (its last user left).
CHANNELS_ROUND_3 = []


class _MockInariHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        channels, clients = self.server.round
        if self.path == "/api/channels":
            self._json(channels)
        elif self.path.startswith("/api/channels/"):
            name = self.path.removeprefix("/api/channels/")
            if name in clients:
                self._json(clients[name])
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def _json(self, payload):
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)


class ProbeTest(unittest.TestCase):
    def setUp(self):
        self.server = HTTPServer(("127.0.0.1", 0), _MockInariHandler)
        self.server.round = (CHANNELS_ROUND_1, CLIENTS_ROUND_1)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.target = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.thread.join()

    def test_full_lifecycle(self):
        # Round 1: one permanent channel, 2 clients (1 human + 1 connector).
        body = exporter.probe(self.target).decode()
        self.assertIn(f'inari_up{{target="{self.target}"}} 1.0', body)
        self.assertIn(f'inari_channels_total{{target="{self.target}"}} 1.0', body)
        self.assertIn(f'inari_channel_clients_total{{target="{self.target}"}} 2.0', body)
        self.assertIn('channel="default"', body)
        self.assertIn('permanent="true"', body)
        # The "currently connected" snapshot shows both right away, even on the very first poll...
        self.assertIn(
            f'inari_connected_user{{channel="default",display_name="Alice",is_connector="false",'
            f'target="{self.target}"}} 1.0',
            body,
        )
        self.assertIn(
            f'inari_connected_user{{channel="default",display_name="Connector",is_connector="true",'
            f'target="{self.target}"}} 1.0',
            body,
        )
        # ...but the cumulative counter needs an elapsed interval to credit: no baseline yet.
        self.assertNotIn("inari_user_connected_seconds_total{", body)

        time.sleep(1.1)

        # Round 2: "default" emptied out, ephemeral "squad-1" appeared with Bob in it.
        self.server.round = (CHANNELS_ROUND_2, CLIENTS_ROUND_2)
        body = exporter.probe(self.target).decode()
        self.assertIn(f'inari_channels_created_total{{target="{self.target}"}} 1.0', body)
        self.assertIn(f'inari_channels_deleted_total{{target="{self.target}"}} 0.0', body)
        self.assertIn(
            f'inari_connected_user{{channel="squad-1",display_name="Bob",is_connector="false",'
            f'target="{self.target}"}} 1.0',
            body,
        )
        # The exporter cannot tell *when* within the interval Bob joined, so like everyone
        # present at this poll he is credited with the whole elapsed time since the last one
        # (an over-estimate for someone who just joined - the same approximation as above).
        self.assertIn('inari_user_connected_seconds_total{channel="squad-1",display_name="Bob"', body)
        # The connector's raw display_name is never used, only the forced "Connector".
        self.assertNotIn("connector-bot", body)
        # Alice already left by the time of this poll (round 2's "default" has 0 clients): a
        # user who disconnects between two polls gets no credit for that interval, and drops
        # out of the "currently connected" snapshot immediately. Known approximation of
        # polling-based duration tracking, documented in the README.
        self.assertNotIn("Alice", body)

        time.sleep(1.1)

        # Round 3: everything emptied out; both channels disappear.
        self.server.round = (CHANNELS_ROUND_3, {})
        body = exporter.probe(self.target).decode()
        self.assertIn(f'inari_channels_total{{target="{self.target}"}} 0.0', body)
        self.assertIn(f'inari_channels_created_total{{target="{self.target}"}} 1.0', body)
        self.assertIn(f'inari_channels_deleted_total{{target="{self.target}"}} 2.0', body)
        # Bob's cumulative time survives after his channel is gone (all-time leaderboard)...
        self.assertIn(
            f'inari_user_connected_seconds_total{{channel="squad-1",display_name="Bob",'
            f'target="{self.target}"}}',
            body,
        )
        # ...but he is gone from the "currently connected" snapshot, like everyone else.
        self.assertNotIn("inari_connected_user{", body)

    def test_down_target(self):
        body = exporter.probe("http://127.0.0.1:1").decode()  # nothing listens there
        self.assertIn('inari_up{target="http://127.0.0.1:1"} 0.0', body)
        self.assertIn('inari_channels_total{target="http://127.0.0.1:1"} 0.0', body)


if __name__ == "__main__":
    unittest.main()
