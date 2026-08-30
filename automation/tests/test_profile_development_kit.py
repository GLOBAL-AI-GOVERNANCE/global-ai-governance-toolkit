from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from automation.scripts.run_profile import MODULES, run_profile
from automation.scripts.scaffold_profile import generate

ROOT = Path(__file__).resolve().parents[2]


class ProfileDevelopmentKitTests(unittest.TestCase):
    def test_generation_is_deterministic_complete_and_non_authorizing(self):
        with tempfile.TemporaryDirectory() as temporary:
            first, second = Path(temporary) / "first", Path(temporary) / "second"
            generate("example-profile", first)
            generate("example-profile", second)
            first_files = {p.relative_to(first): p.read_bytes() for p in first.rglob("*") if p.is_file()}
            second_files = {p.relative_to(second): p.read_bytes() for p in second.rglob("*") if p.is_file()}
        self.assertEqual(first_files, second_files)
        self.assertEqual(set(first_files), {Path(name) for name in (
            "claims-boundaries.md", "evaluator.py", "fixtures/fail.json", "fixtures/pass.json",
            "input.schema.json", "integration.json", "test_profile.py",
        )})
        integration = json.loads(first_files[Path("integration.json")])
        schema = json.loads(first_files[Path("input.schema.json")])
        self.assertEqual(integration["authority_effect"], "NONE")
        self.assertEqual(integration["registration_state"], "NOT_REGISTERED")
        self.assertEqual(schema["properties"]["authority_effect"]["const"], "NONE")

    def test_generation_does_not_bypass_registry_or_runtime_allow_list(self):
        registry_before = (ROOT / "automation/profiles/registry.json").read_bytes()
        modules_before = dict(MODULES)
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "profile"
            generate("unreviewed-profile", destination)
            with self.assertRaisesRegex(ValueError, "Unknown profile id"):
                run_profile("unreviewed-profile", destination / "fixtures/pass.json", destination / "out")
        self.assertEqual(registry_before, (ROOT / "automation/profiles/registry.json").read_bytes())
        self.assertEqual(modules_before, MODULES)


if __name__ == "__main__":
    unittest.main()
