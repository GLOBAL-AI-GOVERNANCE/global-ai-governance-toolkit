"""Keeps the "Start where you are" page, its Markdown copy, llms.txt, and machine-interface.json in sync."""

from __future__ import annotations

import html
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "web"
SITE = "https://ai-governance.solutions/"
SERVED_DOCS = {"AGENT_SETUP.md", "JOURNEYS.md"}


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def prompt(page: str, element_id: str) -> str:
    match = re.search(rf'<pre class="agent-prompt" id="{element_id}"[^>]*>(.*?)</pre>', page, re.S)
    assert match, element_id
    return html.unescape(match.group(1))


class JourneysSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.interface = json.loads(read("web/machine-interface.json"))
        self.start = read("web/start.html")
        self.guide = read("docs/JOURNEYS.md")
        self.llms = read("web/llms.txt")

    def test_journeys_are_an_open_list_with_stable_unique_ids(self) -> None:
        journeys = self.interface["journeys"]
        self.assertIsInstance(journeys, list)
        ids = [journey["id"] for journey in journeys]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("anyone", ids)
        self.assertIn("open, additive list", self.interface["discovery"]["journeys_open_list"])
        self.assertEqual(self.interface["discovery"]["start_here"], "./start.html")
        self.assertEqual(self.interface["discovery"]["journeys_guide"], "./JOURNEYS.md")
        for journey in journeys:
            self.assertTrue(journey["audience_examples"], journey["id"])
            self.assertTrue(journey["steps"], journey["id"])
            step_ids = [step["id"] for step in journey["steps"]]
            self.assertEqual(len(step_ids), len(set(step_ids)), journey["id"])

    def test_every_local_entry_resolves(self) -> None:
        anchors = set(re.findall(r'\bid="([^"]+)"', self.start))
        index_anchors = set(re.findall(r'\bid="([^"]+)"', read("web/index.html")))
        connect_anchors = set(re.findall(r'\bid="([^"]+)"', read("web/connect.html")))
        pages = read(".github/workflows/pages.yml")
        for journey in self.interface["journeys"]:
            entries = [journey["entry"]] + [step["entry"] for step in journey["steps"]]
            entries += [step["input"] for step in journey["steps"] if "input" in step]
            for entry in entries:
                if not entry.startswith("./"):
                    self.assertTrue(entry.startswith("https://"), entry)
                    continue
                path, _, anchor = entry[2:].partition("#")
                if path in SERVED_DOCS:
                    self.assertTrue((ROOT / "docs" / path).is_file(), entry)
                    self.assertIn(f"cp docs/{path} _site/{path}", pages)
                elif path:
                    self.assertTrue((WEB / path).exists(), entry)
                if anchor:
                    known = {"start.html": anchors, "": index_anchors, "connect.html": connect_anchors}[path]
                    self.assertIn(anchor, known, entry)

    def test_start_page_has_a_section_for_each_journey_and_no_walls(self) -> None:
        for journey in self.interface["journeys"]:
            if journey["entry"].startswith("./start.html#"):
                anchor = journey["entry"].split("#", 1)[1]
                self.assertIn(f'href="#{anchor}"', self.start, anchor)
                self.assertIn(f'href="./start.html#{anchor}"', read("web/index.html"), anchor)
        for wall in ("<form", 'type="email"', "sign up", "Sign up", "newsletter"):
            self.assertNotIn(wall, self.start)
        self.assertIn("no account or sign-up", self.start)

    def test_llms_txt_and_guide_name_every_journey(self) -> None:
        self.assertIn("## Start where you are", self.llms)
        self.assertIn(SITE + "JOURNEYS.md", self.llms)
        self.assertIn(SITE + "start.html", self.llms)
        for journey in self.interface["journeys"]:
            self.assertIn(f"- {journey['id']}:", self.llms)
        self.assertIn("open list", self.llms)
        self.assertIn(SITE + "start.html", self.guide)
        for heading in ("you use AI apps", "you build AI organizations or agent fleets", "you work at a frontier lab", "For anyone else"):
            self.assertIn(heading, self.guide)

    def test_prompts_match_the_inventory_contract(self) -> None:
        schema = json.loads(read("automation/contracts/v1/canonical-inventory-record.schema.json"))
        properties = schema["properties"]
        columns = [name for name in properties if name != "schema_version"]
        inventory = prompt(self.start, "prompt-inventory")
        header = next(line for line in inventory.splitlines() if line.startswith("system_id,"))
        self.assertEqual(header.split(","), columns)
        for name in ("vendor_internal", "data_sensitivity", "autonomy_level"):
            for value in properties[name]["enum"]:
                self.assertIn(value, inventory, f"{name}={value}")
        yes_no = [name for name in columns if properties[name].get("enum") == ["Yes", "No"]]
        self.assertTrue(yes_no)
        self.assertIn("Every other column is Yes or No.", inventory)
        for element_id in ("prompt-inventory", "prompt-rule"):
            text = prompt(self.start, element_id)
            indented = "\n".join("   " + line for line in text.splitlines())
            self.assertIn(indented, self.guide, element_id)

    def test_release_tags_match_the_homepage_badges(self) -> None:
        index = read("web/index.html")
        pairs = re.findall(r"([a-z-]+):(v[0-9][^:\s]*):", self.guide)
        self.assertGreaterEqual(len(pairs), 6)
        for repo, tag in pairs:
            badge = re.search(rf'<li id="{repo}">.*?class="g-badge"[^>]*>([^<]+)<', index)
            self.assertIsNotNone(badge, repo)
            self.assertTrue(badge.group(1).startswith(tag + " "), (repo, tag, badge.group(1)))

    def test_start_is_linked_from_every_page_and_listed_in_the_sitemap(self) -> None:
        for page, href in (("index.html", "./start.html"), ("connect.html", "./start.html"), ("maturity/index.html", "../start.html"), ("start.html", "./start.html"), ("lead-agent/index.html", "../start.html"), ("interoperability.html", "./start.html")):
            nav = re.search(r'<span class="gaig-links">(.*?)</span>', read(f"web/{page}"), re.S).group(1)
            self.assertIn(f'<a href="{href}"', nav, page)
        sitemap = read("web/sitemap.xml")
        for url in ("start.html", "JOURNEYS.md", "lead-agent/", "interoperability.html"):
            self.assertIn(f"<loc>{SITE}{url}</loc>", sitemap)
        pages = read(".github/workflows/pages.yml")
        # Pages deploys on every main push (no path filters) and stages JOURNEYS.
        self.assertIn("workflow_call:", pages)
        self.assertIn("cp docs/JOURNEYS.md _site/JOURNEYS.md", pages)
        self.assertNotIn("paths:", pages.split("on:", 1)[1].split("permissions:", 1)[0])
        self.assertIn("node --check web/start.mjs", pages)
        self.assertNotIn("Three ways in", read("web/index.html"))


if __name__ == "__main__":
    unittest.main()
