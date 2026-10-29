from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from automation.scripts.contract_verifier import validate_instance


ROOT = Path(__file__).resolve().parents[2]
VALID = ROOT / "automation/fixtures/valid-ai-inventory.csv"
CRITICAL = ROOT / "automation/fixtures/critical-ai-inventory.csv"
GAPS_SAMPLE = ROOT / "automation/sample-data/sample-ai-inventory.csv"
PIPELINE = ROOT / "automation/scripts/run_governance_checks.py"
RUNNER = ROOT / "web/tests/parity-runner.mjs"
UX_RUNNER = ROOT / "web/tests/ux-runner.mjs"
PROFILE_SURFACE_RUNNER = ROOT / "web/tests/profile-decision-surface-runner.mjs"
EVALUATION_TIME = "2026-08-29T12:00:00Z"


@unittest.skipUnless(shutil.which("node"), "Node.js is required for browser parity tests")
class BrowserParityTests(unittest.TestCase):
    def browser(self, fixture: Path) -> dict[str, object]:
        completed = subprocess.run(
            ["node", str(RUNNER), str(fixture), EVALUATION_TIME],
            cwd=ROOT, text=True, capture_output=True, check=True,
        )
        return json.loads(completed.stdout)

    def cli(self, fixture: Path, fail_on: str = "none") -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
        with tempfile.TemporaryDirectory() as temporary:
            outdir = Path(temporary)
            completed = subprocess.run(
                [sys.executable, "-B", str(PIPELINE), str(fixture), "--outdir", str(outdir), "--evaluation-time", EVALUATION_TIME, "--fail-on", fail_on],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            return tuple(json.loads((outdir / name).read_text(encoding="utf-8")) for name in ("normalized-inventory.json", "governance-findings.json", "governance-result.json"))

    def assert_parity(self, fixture: Path) -> None:
        browser = self.browser(fixture)
        normalized, findings, result = self.cli(fixture)
        self.assertEqual(browser["normalized"]["records"], normalized["records"])
        self.assertEqual(browser["findings"]["findings"], findings["findings"])
        for field in ("schema_version", "generator_version", "normalization_version", "policy_id", "policy_version", "evaluation_time", "input_digest", "validation_state", "governance_gate_state", "human_decision_state", "blocking_threshold", "finding_count", "system_ids"):
            self.assertEqual(browser["result"][field], result[field], field)
        self.assertEqual(browser["handoff"]["authority_effect"], "NONE")

    def test_browser_machine_outputs_validate_against_wave_a_contracts(self) -> None:
        browser = self.browser(VALID)
        contracts = ROOT / "automation/contracts"
        for key, schema in (
            ("normalized", "v1/normalized-inventory.schema.json"),
            ("findings", "v1/governance-findings.schema.json"),
            ("result", "v1/governance-result.schema.json"),
            ("manifest", "v1/decision-pack-manifest.schema.json"),
            ("handoff", "governance-decision-handoff.schema.json"),
        ):
            schema_path = contracts / schema
            validate_instance(
                browser[key],
                json.loads(schema_path.read_text(encoding="utf-8")),
                base=schema_path.parent,
            )

    def test_valid_fixture_matches_cli(self) -> None:
        self.assert_parity(VALID)

    def test_critical_fixture_matches_cli_in_report_only_mode(self) -> None:
        self.assert_parity(CRITICAL)

    def test_example_with_gaps_matches_cli_and_shows_findings(self) -> None:
        self.assert_parity(GAPS_SAMPLE)
        browser = self.browser(GAPS_SAMPLE)
        self.assertEqual(browser["result"]["governance_gate_state"], "BLOCKED")
        self.assertEqual(browser["result"]["human_decision_state"], "PENDING_HUMAN_DECISION")
        self.assertEqual(browser["handoff"]["authority_effect"], "NONE")
        rules = {item["rule_id"] for item in browser["findings"]["findings"]}
        self.assertTrue({"GAI-AUTO-001", "GAI-AUTO-002", "GAI-AUTO-003", "GAI-AUTO-004"} <= rules, rules)
        bundle = (ROOT / "web/contracts.generated.mjs").read_text(encoding="utf-8")
        self.assertIn(json.dumps(GAPS_SAMPLE.read_text(encoding="utf-8")), bundle)
        page = (ROOT / "web/index.html").read_text(encoding="utf-8")
        self.assertIn('id="run-gaps-sample"', page)
        self.assertIn("Both examples are synthetic inventories.", page)
        self.assertIn('loadCsv(contracts.gapsSampleCsv', (ROOT / "web/app.mjs").read_text(encoding="utf-8"))

    def test_static_surface_is_local_only_and_complete(self) -> None:
        combined = "\n".join((ROOT / "web" / name).read_text(encoding="utf-8") for name in ("index.html", "app.mjs", "governance-engine.mjs", "finding-guidance.mjs"))
        # Link-preview metadata must name the site's own absolute URLs; it triggers no request from the page.
        for metadata in (
            '<meta property="og:url" content="https://ai-governance.solutions/">',
            '<meta property="og:image" content="https://ai-governance.solutions/og-image.png">',
            '<link rel="canonical" href="https://ai-governance.solutions/">',
        ):
            self.assertIn(metadata, combined)
            combined = combined.replace(metadata, "")
        # Structured data is an inert JSON-LD block for search engines and agents; it triggers no request.
        start = combined.index('<script type="application/ld+json">')
        end = combined.index("</script>", start) + len("</script>")
        structured = json.loads(combined[start + len('<script type="application/ld+json">'):end - len("</script>")])
        self.assertEqual(structured["@context"], "https://schema.org")
        ids = {node["@id"] for node in structured["@graph"]}
        self.assertIn("https://ai-governance.solutions/#organization", ids)
        self.assertTrue(all(node_id.startswith("https://ai-governance.solutions/") for node_id in ids))
        combined = combined[:start] + combined[end:]
        for phrase in ("Run sample", "Run example with gaps", "Download blank template", "Load your CSV", "Normalization preview", "Governance results", "Machine outputs", "Decision Pack", "authority_effect", "What this means", "What to do next"):
            self.assertIn(phrase, combined)
        for forbidden in ("fetch(", "XMLHttpRequest", "WebSocket", "sendBeacon", "https://", "http://"):
            self.assertNotIn(forbidden, combined)

    def test_browser_contract_bundle_is_current(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-B", "automation/scripts/generate_browser_contract_bundle.py", "--check"],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_blank_template_is_generated_and_a_completed_copy_loads(self) -> None:
        blank = (ROOT / "web/ai-system-inventory-template.csv").read_text(encoding="utf-8-sig")
        canonical_blank = (ROOT / "spreadsheets/ai-system-inventory-template.csv").read_text(encoding="utf-8-sig")
        self.assertEqual(blank, canonical_blank)
        header = blank.splitlines()[0]
        self.assertTrue(header.startswith("Schema Version,"))
        # A completed copy replaces the example row (or fills a header-only sheet).
        row = "1.0.0,TEST-BEGINNER-001,Beginner Example,Casey Owner,Operations,Internal,Document search,Internal,No,No,No,No,No,None,No,Yes,Yes,Yes\n"
        with tempfile.TemporaryDirectory() as temporary:
            completed_template = Path(temporary) / "completed-template.csv"
            completed_template.write_text(header + "\n" + row, encoding="utf-8")
            browser = self.browser(completed_template)
        self.assertEqual(browser["normalized"]["records"][0]["system_id"], "TEST-BEGINNER-001")
        self.assertEqual(browser["result"]["governance_gate_state"], "PASSED_CURRENT_AUTOMATED_CHECKS")

    def test_machine_front_door_is_versioned_and_non_authorizing(self) -> None:
        interface = json.loads((ROOT / "web/machine-interface.json").read_text(encoding="utf-8"))
        self.assertEqual(interface["machine_interface_version"], "1.6.0")
        self.assertEqual(interface["discovery"]["agent_setup"], "./AGENT_SETUP.md")
        self.assertTrue((ROOT / "docs/AGENT_SETUP.md").is_file())
        pages = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
        self.assertIn("cp docs/AGENT_SETUP.md _site/AGENT_SETUP.md", pages)
        self.assertIn("https://ai-governance.solutions/AGENT_SETUP.md", (ROOT / "web/llms.txt").read_text(encoding="utf-8"))
        self.assertEqual(interface["discovery"]["llms_txt"], "./llms.txt")
        self.assertTrue((ROOT / "web/llms.txt").is_file())
        self.assertEqual(interface["authority_effect"], "NONE")
        self.assertEqual(interface["profiles"]["authority_effect"], "NONE")
        registry = json.loads((ROOT / "automation/profiles/registry.json").read_text(encoding="utf-8"))
        registry_ids = [item["id"] for item in registry["profiles"]]
        browser_ids = [item["id"] for item in registry["profiles"] if item.get("browser_support") is True]
        self.assertEqual(interface["profiles"]["cli_supported"], registry_ids)
        self.assertEqual(interface["profiles"]["browser_supported"], browser_ids)
        self.assertEqual(interface["profiles"]["supported"], browser_ids)
        self.assertIn("organizational-ai-maturity-v0.1", registry_ids)
        self.assertFalse(interface["runtime"]["upload"])
        self.assertFalse(interface["runtime"]["network_requests"])
        self.assertIn("not deployment approval", interface["review_boundary"])
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn(f'version = "{interface["release"].removeprefix("v")}"', pyproject)
        self.assertIn(f"/{interface['release']}/", interface["profiles"]["registry"])
        assurance = interface["profiles"]["independent_assurance"]
        self.assertIn(assurance["profile_id"], registry_ids)
        self.assertEqual(assurance["authority_effect"], "NONE")
        case_path = "automation/contracts/profiles/independent-assurance-case.schema.json"
        self.assertTrue(assurance["case_contract"].endswith(f"/{interface['release']}/{case_path}"))
        case_schema = json.loads((ROOT / case_path).read_text(encoding="utf-8"))
        self.assertIn(f"Contract {assurance['contract_version']}:", case_schema["description"])
        for field in assurance["autonomous_agent_requires"]:
            self.assertIn(field, case_schema["properties"])
        self.assertEqual(
            case_schema["properties"]["max_shutdown_test_age_days"]["maximum"],
            assurance["max_shutdown_test_age_days"],
        )
        for relative in (interface["input"]["template"], interface["input"]["sample"]):
            self.assertTrue((ROOT / "web" / relative.removeprefix("./")).is_file())

    def test_plain_language_guidance_covers_exact_policy_rules(self) -> None:
        completed = subprocess.run(
            ["node", str(UX_RUNNER), str(CRITICAL), EVALUATION_TIME],
            cwd=ROOT, text=True, capture_output=True, check=True,
        )
        payload = json.loads(completed.stdout)
        policy_ids = {
            rule["id"]
            for rule in json.loads((ROOT / "automation/policy-as-code/governance-rules.yaml").read_text(encoding="utf-8"))["rules"]
        }
        self.assertEqual(set(payload["findingGuidance"]), policy_ids)
        for guidance in payload["findingGuidance"].values():
            self.assertTrue(guidance["title"] and guidance["meaning"] and guidance["next"])
        for finding in payload["findings"]:
            self.assertIn(finding["rule_id"], payload["findingGuidance"])
            self.assertIn(finding["severity"], {"HIGH", "CRITICAL"})
        self.assertEqual(payload["result"]["evaluation_time"], EVALUATION_TIME)
        self.assertEqual(payload["handoff"]["authority_effect"], "NONE")

    def test_mobile_keeps_local_trust_statement_visible(self) -> None:
        css = (ROOT / "web/styles.css").read_text(encoding="utf-8")
        self.assertNotRegex(css, r"\.local-badge\s*\{[^}]*display\s*:\s*none")

    def test_profile_decision_surface_order_and_accessibility_semantics(self) -> None:
        completed = subprocess.run(["node", str(PROFILE_SURFACE_RUNNER)], cwd=ROOT, text=True, capture_output=True, check=True)
        payload = json.loads(completed.stdout)
        html = payload["html"]
        sequence = ['id="profile-decision-heading"', "Consequence", "Remaining risk", "Next action", "Timeline", "Technical evidence"]
        positions = [html.index(label) for label in sequence]
        self.assertEqual(positions, sorted(positions))
        self.assertEqual(payload["attributes"]["role"], "region")
        self.assertEqual(payload["attributes"]["aria-labelledby"], "profile-decision-heading")
        self.assertTrue(payload["attributes"]["focused"])
        for semantic in ('role="status"', 'aria-live="polite"', '<ol class="decision-surface"', '<time>', '<details>', '<summary>Technical evidence</summary>'):
            self.assertIn(semantic, html)
        self.assertEqual(payload["view"]["authorityEffect"], "NONE")
        self.assertNotIn(">Decision:", html)
        self.assertIn("not issued by this tool", html)
        self.assertIn("This tool grants no authorization.", html)
        index = (ROOT / "web/index.html").read_text(encoding="utf-8")
        self.assertIn("Run bounded synthetic example", index)
        self.assertIn('aria-describedby="profile-sample-boundary"', index)


if __name__ == "__main__":
    unittest.main()
