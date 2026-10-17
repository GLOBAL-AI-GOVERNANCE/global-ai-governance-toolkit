"""Regression tests for the static browser workspace: no stale evaluation can render or download (D1),
accessible view selection, keyboard-reachable scroll regions, skip links, and field-specific CSV guidance."""
from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "web/tests/evaluation-session-runner.mjs"
VALID = ROOT / "automation/fixtures/valid-ai-inventory.csv"
EVALUATION_TIME = "2026-08-29T12:00:00Z"


@unittest.skipUnless(shutil.which("node"), "Node.js is required for browser state tests")
class EvaluationStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        completed = subprocess.run(["node", str(RUNNER), str(VALID), EVALUATION_TIME], cwd=ROOT, text=True, capture_output=True, check=True)
        cls.payload = json.loads(completed.stdout)

    def test_valid_invalid_valid_invalidates_previous_output_and_downloads(self) -> None:
        self.assertEqual(self.payload["validInvalidValid"], {"readyAfterValid": True, "pendingClearsOutput": True, "errorState": True, "recovered": True})

    def test_stale_async_results_cannot_publish_or_download(self) -> None:
        self.assertEqual(self.payload["rapid"], {"staleAccepted": False, "newestKept": True, "staleErrorAccepted": False, "oldTokenCanDownload": False})

    def test_output_source_name_matches_displayed_input(self) -> None:
        self.assertEqual(self.payload["filename"]["session"], self.payload["filename"]["output"])

    def test_csv_errors_name_column_and_row_without_echoing_cells(self) -> None:
        m = self.payload["messages"]
        self.assertIn('column "autonomy_level"', m["enum"])
        self.assertIn("row 3", m["enum"])
        self.assertIn("Allowed values: None, Partial, Full", m["enum"])
        self.assertNotIn("SECRET-CELL-VALUE", m["enum"])
        self.assertIn('column "extra_col"', m["unknown"])
        self.assertIn("row 2", m["width"])
        self.assertTrue(m["empty"].startswith("EMPTY_INPUT"))
        self.assertTrue(m["runtime"].startswith("BROWSER_RUNTIME_ERROR"))

    def test_app_wires_session_tokens_into_rendering_and_downloads(self) -> None:
        app = (ROOT / "web/app.mjs").read_text(encoding="utf-8")
        for snippet in ("createEvaluationSession", "session.resolve(token", "session.canDownload(token)", "session.isCurrent(token)", "clearEvaluation("):
            self.assertIn(snippet, app)

    def test_view_tabs_and_output_switch_expose_selection(self) -> None:
        index = (ROOT / "web/index.html").read_text(encoding="utf-8")
        self.assertIn('role="tablist" aria-label="Evaluation views"', index)
        self.assertEqual(index.count('role="tab"'), 4)
        self.assertEqual(index.count('role="tabpanel"'), 4)
        self.assertIn('aria-selected="true"', index)
        self.assertIn('role="group" aria-label="Machine output to show"', index)
        self.assertEqual(index.count("aria-pressed="), 4)
        self.assertNotIn('class="output-switch" role="tablist"', index)
        app = (ROOT / "web/app.mjs").read_text(encoding="utf-8")
        for key in ("ArrowRight", "ArrowLeft", "Home", "End", "aria-selected", "aria-pressed"):
            self.assertIn(key, app)

    def test_skip_links_and_keyboard_reachable_scroll_regions(self) -> None:
        for page in ("index.html", "connect.html"):
            html = (ROOT / "web" / page).read_text(encoding="utf-8")
            self.assertIn('<a class="skip-link" href="#top">Skip to main content</a>', html, page)
            self.assertIn('<main id="top" tabindex="-1">', html, page)
        connect = (ROOT / "web/connect.html").read_text(encoding="utf-8")
        self.assertIn('<pre tabindex="0" role="region" aria-label=', connect)
        self.assertIn('<div class="table-wrap" tabindex="0" role="region"', connect)
        css = (ROOT / "web/styles.css").read_text(encoding="utf-8")
        self.assertIn(".skip-link:focus", css)
        self.assertIn("table-layout:fixed", css)
        self.assertIn("hyphens:auto", css)

    def test_connect_page_states_agent_data_flow_and_passport_scope(self) -> None:
        connect = (ROOT / "web/connect.html").read_text(encoding="utf-8")
        self.assertIn("<strong>Where your data goes:</strong> the browser Toolkit processes files only in this browser.", connect)
        self.assertIn("a hosted assistant sends it to its provider", connect)
        self.assertIn("it does not monitor, enforce, or revoke anything at runtime", connect)

    def test_workspace_scroll_respects_reduced_motion(self) -> None:
        # The workspace scroll follows the page's CSS scroll-behavior, which reduced motion turns off.
        app = (ROOT / "web/app.mjs").read_text(encoding="utf-8")
        self.assertIn('byId("workspace").scrollIntoView();', app)
        self.assertNotIn('behavior: "smooth"', app)
        css = (ROOT / "web/styles.css").read_text(encoding="utf-8")
        self.assertIn("@media (prefers-reduced-motion: reduce) { html { scroll-behavior:auto; } }", css)


if __name__ == "__main__":
    unittest.main()
