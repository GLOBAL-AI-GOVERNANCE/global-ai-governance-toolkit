"""Schema enforcement tests for Independent Assurance."""

import unittest
from pathlib import Path

from automation.scripts.run_profile import run_profile


class IndependentAssuranceSchemaTest(unittest.TestCase):
    def test_unknown_property_rejected(self):
        fixture = Path("/tmp/invalid-assurance.json")
        fixture.write_text(
            '{"subject_id": "system-001", "authority_effect": "NONE", "unknown_field": true}',
            encoding="utf-8",
        )
        with self.assertRaises(ValueError) as ctx:
            run_profile("independent-assurance-v0.1", fixture, Path("/tmp"), None, None)
        self.assertIn("registered schema", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
