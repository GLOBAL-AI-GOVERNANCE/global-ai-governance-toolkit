from __future__ import annotations

import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONSOLE = ROOT / "web/lead-agent"
RUNNER = ROOT / "web/tests/lead-agent-runner.mjs"


class LeadAgentConsoleFilesTests(unittest.TestCase):
    def test_console_files_exist(self) -> None:
        for name in ("index.html", "engine.mjs", "app.mjs", "lead-agent.css"):
            self.assertTrue((CONSOLE / name).is_file(), name)

    def test_page_never_asks_for_a_key(self) -> None:
        html = (CONSOLE / "index.html").read_text(encoding="utf-8")
        self.assertNotRegex(html, re.compile(r'type="password"|name="[^"]*key[^"]*"', re.I))
        self.assertIn("never asks for, stores or sends an API key", html)
        app = (CONSOLE / "app.mjs").read_text(encoding="utf-8")
        for storage in ("localStorage", "sessionStorage", "indexedDB", "document.cookie"):
            self.assertNotIn(storage, app)

    def test_connect_is_limited_to_this_machine(self) -> None:
        app = (CONSOLE / "app.mjs").read_text(encoding="utf-8")
        self.assertIn(r"if (!/^(localhost|127\.0\.0\.1|\[::1\])$/.test(url.hostname)) throw", app)
        calls = re.findall(r"fetch\(([^,]+),", app)
        self.assertEqual(calls, ['base + path', 'base + "/api/health"'])
        self.assertEqual(re.findall(r"\bbase = ([^;]+);", app), ["url.origin"])
        for api in ("XMLHttpRequest", "WebSocket", "sendBeacon", "serviceWorker"):
            self.assertNotIn(api, app)
        engine = (CONSOLE / "engine.mjs").read_text(encoding="utf-8")
        self.assertNotRegex(engine, r"fetch\(|XMLHttpRequest|WebSocket|sendBeacon")

    def test_public_name_is_lead_agent(self) -> None:
        for path in CONSOLE.iterdir():
            self.assertNotIn("jarvis", path.read_text(encoding="utf-8").lower(), path.name)


@unittest.skipUnless(shutil.which("node"), "Node.js is required for the lead agent engine tests")
class LeadAgentEngineTests(unittest.TestCase):
    def test_engine_scenario(self) -> None:
        completed = subprocess.run(["node", str(RUNNER)], cwd=ROOT, text=True, capture_output=True, check=False)
        report = json.loads(completed.stdout)
        failed = [check for check in report["checks"] if not check["ok"]]
        self.assertEqual(failed, [], completed.stderr)
        self.assertEqual(completed.returncode, 0)
        self.assertGreaterEqual(len(report["checks"]), 13)
        self.assertEqual(report["ledger"]["ledger_kind"], "global-ai-governance.lead-agent-audit")


if __name__ == "__main__":
    unittest.main()
