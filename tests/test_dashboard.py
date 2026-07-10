"""Tests for dashboard.py — Pure Python http.server dashboard."""
import json
import threading
import time
import urllib.request

from lib.dashboard import DashboardServer


def test_dashboard_server_starts_and_serves():
    server = DashboardServer(port=13333)
    t = server.run_in_thread()
    time.sleep(0.3)  # Let server start

    try:
        # Health check
        req = urllib.request.urlopen("http://127.0.0.1:13333/api/health", timeout=2)
        data = json.loads(req.read().decode())
        assert data["status"] == "ok"

        # Overview page
        req = urllib.request.urlopen("http://127.0.0.1:13333/", timeout=2)
        html = req.read().decode()
        assert "Fuzzybee Dashboard" in html

        # Burn page
        req = urllib.request.urlopen("http://127.0.0.1:13333/burn", timeout=2)
        html = req.read().decode()
        assert "Burn Report" in html

        # Cycles page
        req = urllib.request.urlopen("http://127.0.0.1:13333/cycles", timeout=2)
        html = req.read().decode()
        assert "Cycle History" in html
    finally:
        # Can't cleanly shutdown http.server from outside, but thread is daemon
        pass
