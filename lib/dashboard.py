"""Localhost dashboard (:3333) — zero framework deps, http.server + HTMX."""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


class DashboardHandler(BaseHTTPRequestHandler):
    """Serve dashboard pages and API endpoints."""

    db_path: str = "~/.fuzzybee/cycles.db"

    def log_message(self, format, *args):
        # Suppress default logging
        pass

    def _send_json(self, data: dict, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_html(self, html: str, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def _send_sse(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

    def _db(self):
        db = Path(self.db_path).expanduser()
        db.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_number INTEGER NOT NULL,
                task_id TEXT NOT NULL,
                status TEXT NOT NULL,
                problem_type TEXT,
                tool_calls INTEGER DEFAULT 0,
                wall_clock_ms INTEGER DEFAULT 0,
                evidence_summary TEXT,
                next_step TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                completed_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_id INTEGER NOT NULL REFERENCES cycles(id),
                gate_name TEXT NOT NULL,
                command TEXT NOT NULL,
                expected TEXT NOT NULL,
                actual TEXT NOT NULL,
                status TEXT NOT NULL,
                duration_ms REAL DEFAULT 0,
                recorded_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS learnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                problem_type TEXT,
                gate_outcome TEXT,
                tool_count INTEGER,
                duration_ms INTEGER,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        conn.commit()
        return conn

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == "/":
            self._send_html(self._page_overview())
        elif path == "/burn":
            self._send_html(self._page_burn())
        elif path == "/cycles":
            self._send_html(self._page_cycles(qs))
        elif path.startswith("/cycles/") and path.count("/") == 2:
            cycle_id = path.split("/")[-1]
            self._send_html(self._page_cycle_detail(cycle_id))
        elif path.startswith("/cycles/") and path.endswith("/evidence"):
            cycle_id = path.split("/")[-2]
            self._send_json(self._api_evidence(cycle_id))
        elif path == "/agents":
            self._send_html(self._page_agents())
        elif path == "/analytics":
            self._send_html(self._page_analytics())
        elif path == "/api/cycles/stream":
            self._handle_sse()
        elif path == "/api/health":
            self._send_json({"status": "ok", "dashboard": "fuzzybee"})
        else:
            self._send_html("<h1>404</h1>", 404)

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    # ── Pages ────────────────────────────────────────────────

    def _page_overview(self) -> str:
        stats = self._get_stats()
        return self._base_html("""
        <h1>⚡ Fuzzybee Dashboard</h1>
        <div class="grid">
            <div class="card"><h3>Total Cycles</h3><div class="big">{total}</div></div>
            <div class="card"><h3>Pass Rate</h3><div class="big">{pass_rate}%</div></div>
            <div class="card"><h3>Active</h3><div class="big">{active}</div></div>
            <div class="card"><h3>Blocked</h3><div class="big">{blocked}</div></div>
        </div>
        <div class="card" style="margin-top:20px">
            <h3>Latest Cycle</h3>
            <pre>{latest}</pre>
        </div>
        <div hx-ext="sse" sse-connect="/api/cycles/stream" style="display:none"></div>
        """.format(
            total=stats["total"],
            pass_rate=stats["pass_rate"],
            active=stats["active"],
            blocked=stats["blocked"],
            latest=json.dumps(stats["latest"], indent=2, default=str) if stats["latest"] else "None",
        ))

    def _page_burn(self) -> str:
        report = self._get_burn_report()
        return self._base_html("""
        <h1>🔥 Burn Report</h1>
        <div class="card">
            <pre>{report}</pre>
        </div>
        """.format(report=report))

    def _page_cycles(self, qs: dict) -> str:
        status_filter = qs.get("status", [None])[0]
        rows = self._get_cycles(status=status_filter)
        rows_html = ""
        for r in rows:
            rows_html += f"""
            <tr>
                <td><a href="/cycles/{r[0]}">#{r[1]}</a></td>
                <td>{r[2]}</td>
                <td><span class="badge {r[3].lower()}">{r[3]}</span></td>
                <td>{r[4]}</td>
                <td>{r[5]:.1f}s</td>
            </tr>"""
        return self._base_html("""
        <h1>📋 Cycle History</h1>
        <div class="card">
            <table>
                <thead><tr><th>Cycle</th><th>Task</th><th>Status</th><th>Type</th><th>Duration</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """.format(rows=rows_html or "<tr><td colspan=5>No cycles yet</td></tr>"))

    def _page_cycle_detail(self, cycle_id: str) -> str:
        cycle = self._get_cycle(cycle_id)
        if not cycle:
            return self._base_html("<h1>Cycle not found</h1>")
        evidence = self._get_evidence(cycle_id)
        ev_html = ""
        for e in evidence:
            ev_html += f"""
            <div class="card" style="margin:8px 0">
                <strong>{e[0]}</strong> <span class="badge {e[4].lower()}">{e[4]}</span>
                <pre>cmd: {e[1]}
expected: {e[2]}
actual: {e[3]}
duration: {e[5]:.0f}ms</pre>
            </div>"""
        return self._base_html("""
        <h1>Cycle #{num} — {task}</h1>
        <div class="card">
            <p><strong>Status:</strong> <span class="badge {status}">{status}</span></p>
            <p><strong>Duration:</strong> {dur:.1f}s</p>
            <p><strong>Tools:</strong> {tools}</p>
            <p><strong>Next:</strong> {next_step}</p>
        </div>
        <h3>Evidence</h3>
        {evidence}
        """.format(
            num=cycle[1], task=cycle[2], status=cycle[3],
            dur=cycle[4]/1000 if cycle[4] else 0, tools=cycle[5],
            next_step=cycle[6] or "—", evidence=ev_html or "<p>No evidence</p>",
        ))

    def _page_agents(self) -> str:
        return self._base_html("""
        <h1>🤖 Agent Monitor</h1>
        <div class="card">
            <p>Active agents: <strong>fuzzybee</strong></p>
            <p>Session: <span id="session-kind">detecting...</span></p>
            <div hx-get="/api/health" hx-trigger="every 5s" hx-swap="none"
                 style="font-size:12px;color:#666"></div>
        </div>
        <script>
        document.addEventListener('DOMContentLoaded', () => {
            document.getElementById('session-kind').textContent = 'interactive';
        });
        </script>
        """)

    def _page_analytics(self) -> str:
        clusters = self._get_pattern_clusters()
        rows = ""
        for pattern, count in clusters:
            rows += f"<tr><td>{pattern}</td><td>{count}</td></tr>"
        return self._base_html("""
        <h1>📊 Analytics</h1>
        <div class="card">
            <table>
                <thead><tr><th>Pattern</th><th>Count</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """.format(rows=rows or "<tr><td colspan=2>No data</td></tr>"))

    def _handle_sse(self):
        self._send_sse()
        try:
            self.wfile.write(b"data: {\"event\": \"connected\"}\n\n")
            self.wfile.flush()
        except Exception:
            pass

    def _api_evidence(self, cycle_id: str) -> dict:
        evidence = self._get_evidence(cycle_id)
        return {
            "cycle_id": cycle_id,
            "evidence": [
                {"gate_name": e[0], "command": e[1], "expected": e[2],
                 "actual": e[3], "status": e[4], "duration_ms": e[5]}
                for e in evidence
            ],
        }

    # ── Data Access ──────────────────────────────────────────

    def _get_stats(self) -> dict:
        conn = self._db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM cycles")
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM cycles WHERE status = 'PASS'")
        passed = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM cycles WHERE status = 'BLOCKED'")
        blocked = cur.fetchone()[0]
        cur.execute("SELECT * FROM cycles ORDER BY id DESC LIMIT 1")
        latest = cur.fetchone()
        conn.close()
        return {
            "total": total,
            "pass_rate": round(passed / total * 100, 1) if total else 0,
            "active": total - blocked,
            "blocked": blocked,
            "latest": dict(zip(
                ["id","cycle_number","task_id","status","problem_type","tool_calls",
                 "wall_clock_ms","evidence_summary","next_step","created_at","completed_at"],
                latest,
            )) if latest else None,
        }

    def _get_burn_report(self) -> str:
        conn = self._db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*), AVG(wall_clock_ms), SUM(tool_calls) FROM cycles")
        total, avg_ms, tools = cur.fetchone()
        cur.execute("SELECT status, COUNT(*) FROM cycles GROUP BY status")
        by_status = dict(cur.fetchall())
        cur.execute("SELECT problem_type, COUNT(*) FROM cycles GROUP BY problem_type ORDER BY 2 DESC LIMIT 1")
        most_common = cur.fetchone()
        conn.close()

        lines = [
            f"Burn Report for {datetime.now().strftime('%Y-%m-%d')}",
            "─" * 40,
            f"Total cycles:  {total or 0}",
            f"Pass rate:     {by_status.get('PASS', 0)}/{total or 0}",
            f"Avg duration:  {avg_ms/1000:.0f}s" if avg_ms else "Avg duration:  N/A",
            f"Total tools:   {tools or 0} calls",
            f"Most common:   {most_common[0] or 'N/A'} ({most_common[1]} cycles)" if most_common else "Most common:   N/A",
        ]
        return "\n".join(lines)

    def _get_cycles(self, status: str = None) -> list:
        conn = self._db()
        cur = conn.cursor()
        if status:
            cur.execute("SELECT id, cycle_number, task_id, status, problem_type, wall_clock_ms FROM cycles WHERE status = ? ORDER BY id DESC", (status,))
        else:
            cur.execute("SELECT id, cycle_number, task_id, status, problem_type, wall_clock_ms FROM cycles ORDER BY id DESC LIMIT 50")
        rows = cur.fetchall()
        conn.close()
        return rows

    def _get_cycle(self, cycle_id: str) -> tuple:
        conn = self._db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM cycles WHERE id = ?", (cycle_id,))
        row = cur.fetchone()
        conn.close()
        return row

    def _get_evidence(self, cycle_id: str) -> list:
        conn = self._db()
        cur = conn.cursor()
        cur.execute("SELECT gate_name, command, expected, actual, status, duration_ms FROM evidence WHERE cycle_id = ?", (cycle_id,))
        rows = cur.fetchall()
        conn.close()
        return rows

    def _get_pattern_clusters(self) -> list:
        conn = self._db()
        cur = conn.cursor()
        cur.execute("SELECT problem_type || ':' || status, COUNT(*) FROM cycles GROUP BY problem_type, status")
        rows = cur.fetchall()
        conn.close()
        return rows

    # ── HTML Template ────────────────────────────────────────

    def _base_html(self, body: str) -> str:
        return f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fuzzybee Dashboard</title>
<script src="https://unpkg.com/htmx.org@1.9.12"></script>
<style>
:root {{ --bg: #0f172a; --card: #1e293b; --text: #e2e8f0; --accent: #38bdf8; --pass: #22c55e; --fail: #ef4444; --blocked: #f59e0b; }}
body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 24px; line-height: 1.5; }}
h1 {{ margin: 0 0 20px 0; font-size: 24px; }}
h3 {{ margin: 0 0 8px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; }}
.card {{ background: var(--card); border-radius: 12px; padding: 20px; margin-bottom: 16px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; }}
.big {{ font-size: 32px; font-weight: 700; color: var(--accent); margin-top: 4px; }}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #334155; }}
th {{ color: #94a3b8; font-weight: 500; text-transform: uppercase; font-size: 11px; letter-spacing: 0.05em; }}
a {{ color: var(--accent); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
pre {{ background: #0f172a; padding: 12px; border-radius: 8px; overflow-x: auto; font-size: 12px; line-height: 1.4; }}
.badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase; }}
.badge.pass {{ background: rgba(34,197,94,0.15); color: #4ade80; }}
.badge.fail {{ background: rgba(239,68,68,0.15); color: #f87171; }}
.badge.blocked {{ background: rgba(245,158,11,0.15); color: #fbbf24; }}
.badge.skipped {{ background: rgba(148,163,184,0.15); color: #cbd5e1; }}
</style>
</head><body>
<nav style="margin-bottom:24px;font-size:13px">
<a href="/">Overview</a> · <a href="/burn">Burn</a> · <a href="/cycles">Cycles</a> · <a href="/agents">Agents</a> · <a href="/analytics">Analytics</a>
</nav>
{body}
</body></html>"""


class DashboardServer:
    """Run the dashboard on localhost:3333."""

    def __init__(self, port: int = 3333, db_path: str = "~/.fuzzybee/cycles.db"):
        self.port = port
        self.db_path = db_path

    def run(self):
        DashboardHandler.db_path = self.db_path
        server = HTTPServer(("127.0.0.1", self.port), DashboardHandler)
        print(f"Dashboard running at http://127.0.0.1:{self.port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")
            server.shutdown()

    def run_in_thread(self) -> threading.Thread:
        DashboardHandler.db_path = self.db_path
        server = HTTPServer(("127.0.0.1", self.port), DashboardHandler)
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        return t
