#!/usr/bin/env python3
"""Refresh Toolkit site and docs pins from the profile suite-manifest.json.

Source of truth is GLOBAL-AI-GOVERNANCE/suite-manifest.json (GitHub release tags).
This script rewrites automation/suite-pins.json and replaces the previous pin
strings in the listed site/docs files. Schema $id URLs that intentionally stay
on an older tag (for example v2.7.2) are untouched because only values present
in suite-pins.json are substituted.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PINS_PATH = ROOT / "automation" / "suite-pins.json"
DEFAULT_MANIFEST = (
    "https://raw.githubusercontent.com/GLOBAL-AI-GOVERNANCE/"
    "GLOBAL-AI-GOVERNANCE/main/suite-manifest.json"
)
TARGET_FILES = (
    "automation/suite-pins.json",
    "docs/AGENT_SETUP.md",
    "docs/JOURNEYS.md",
    "web/bootstrap.sh",
    "web/connect.html",
    "web/index.html",
    "web/llms.txt",
    "web/machine-interface.json",
    "web/start.html",
    "README.md",
)


def load_json(path_or_url: str) -> dict:
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        # Prefer gh api for the canonical suite-manifest on main (retries TLS flakes).
        if path_or_url.rstrip("/") == DEFAULT_MANIFEST.rstrip("/") or path_or_url.endswith(
            "/GLOBAL-AI-GOVERNANCE/main/suite-manifest.json"
        ):
            last_error: Exception | None = None
            for _ in range(5):
                try:
                    completed = subprocess.run(
                        [
                            "gh",
                            "api",
                            "repos/GLOBAL-AI-GOVERNANCE/GLOBAL-AI-GOVERNANCE/contents/suite-manifest.json?ref=main",
                            "-H",
                            "Accept: application/vnd.github.raw",
                        ],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    return json.loads(completed.stdout)
                except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as error:
                    last_error = error
                    continue
            if last_error:
                pass  # fall through to urllib
        token = None
        try:
            token = subprocess.run(
                ["gh", "auth", "token"], check=True, capture_output=True, text=True
            ).stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            token = None
        request = urllib.request.Request(
            path_or_url,
            headers={
                "User-Agent": "gaig-toolkit-site-sync",
                **({"Authorization": f"Bearer {token}"} if token else {}),
            },
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    return json.loads(Path(path_or_url).read_text(encoding="utf-8"))


def pins_from_manifest(manifest: dict) -> dict:
    pins = manifest["pins"]
    toolkit = pins["global-ai-governance-toolkit"]
    mcp = pins["ai-governance-mcp"]
    peace = pins["peace-os"]
    agentic = pins["agentic-ai-governance"]
    mcp_bundle = mcp.get("bundled_toolkit") or {}
    return {
        "schema_version": "1.0.0",
        "source_manifest": DEFAULT_MANIFEST,
        "toolkit": toolkit["tag"],
        "toolkit_naked": toolkit["version_naked"],
        "toolkit_sha": toolkit["commit_sha"],
        "toolkit_wheel": toolkit["wheel"],
        "mcp": mcp["tag"],
        "mcp_naked": mcp["version_naked"],
        "mcp_bundled_toolkit": mcp_bundle.get("tag") or "",
        "mcp_bundled_toolkit_sha": mcp_bundle.get("commit_sha") or "",
        "mcp_bundled_agentic_sha": (mcp.get("bundled_agentic") or {}).get("commit_sha") or "",
        "peace_os": peace["tag"],
        "agentic": agentic["tag"],
        "agentic_naked": agentic["version_naked"],
    }


def replacement_pairs(old: dict, new: dict) -> list[tuple[str, str]]:
    keys = (
        "toolkit_sha",
        "toolkit_wheel",
        "toolkit",
        "toolkit_naked",
        "mcp",
        "mcp_naked",
        "peace_os",
        "agentic",
        "agentic_naked",
    )
    pairs = []
    for key in keys:
        if old.get(key) and new.get(key) and old[key] != new[key]:
            pairs.append((old[key], new[key]))
    # Longest first so naked versions do not partially rewrite tags.
    pairs.sort(key=lambda item: len(item[0]), reverse=True)
    return pairs


def apply_replacements(text: str, pairs: list[tuple[str, str]]) -> str:
    for old, new in pairs:
        text = text.replace(old, new)
    return text


def rewrite_mcp_bundle_block(text: str, pins: dict) -> str:
    """Keep the MCP UPSTREAM_LOCK sentence accurate after toolkit pin rewrites."""
    begin, end = "<!-- gaig:mcp-bundle -->", "<!-- /gaig:mcp-bundle -->"
    if begin not in text or end not in text:
        return text
    bundled = pins.get("mcp_bundled_toolkit") or ""
    bundled_sha = pins.get("mcp_bundled_toolkit_sha") or ""
    agentic_sha = pins.get("mcp_bundled_agentic_sha") or ""
    if not (bundled and bundled_sha and agentic_sha):
        return text
    body = (
        f"`gaig-mcp` {pins['mcp']} bundles the Toolkit at {bundled} "
        f"(commit `{bundled_sha}`) and Agentic AI Governance at commit "
        f"`{agentic_sha}`. Its outputs report those commits in `source`. "
        "Bundle pins come from MCP `UPSTREAM_LOCK.json`, not from the Toolkit release tag."
    )
    start = text.index(begin) + len(begin)
    stop = text.index(end)
    return text[:start] + "\n" + body + "\n" + text[stop:]





def apply_journey_badges(text: str, badges: dict[str, str], *, html: bool) -> str:
    """Rewrite product badge labels from suite-manifest journey_badges."""
    import re

    if not badges or not html:
        return text

    for slug, label in badges.items():
        slug_pat = re.escape(slug)
        id_re = re.compile(
            rf'(<li\b[^>]*\bid="{slug_pat}"[^>]*>)(.*?)(</li>)',
            re.DOTALL | re.IGNORECASE,
        )

        def id_sub(m, label=label):
            inner = re.sub(
                r'(<span class="g-badge"[^>]*>)(.*?)(</span>)',
                rf'\g<1>{label}\g<3>',
                m.group(2),
                count=1,
                flags=re.DOTALL,
            )
            return m.group(1) + inner + m.group(3)

        text2, n = id_re.subn(id_sub, text, count=1)
        if n:
            text = text2
            continue

        li_re = re.compile(r'(<li\b[^>]*>)(.*?)(</li>)', re.DOTALL | re.IGNORECASE)
        replaced = False
        parts: list[str] = []
        last = 0
        for m in li_re.finditer(text):
            parts.append(text[last : m.start()])
            block = m.group(0)
            href_m = re.search(r'<a\b[^>]*\bhref="([^"]+)"', block, re.IGNORECASE)
            href = href_m.group(1) if href_m else ''
            hit = (
                f"github.com/GLOBAL-AI-GOVERNANCE/{slug}" in href
                or f"global-ai-governance.github.io/{slug}" in href
                or href.rstrip("/").endswith(f"/{slug}")
                or (slug == "global-ai-governance-toolkit" and "#toolkit" in href)
            )
            if hit and not replaced:
                block = re.sub(
                    r'(<span class="g-badge"[^>]*>)(.*?)(</span>)',
                    rf"\g<1>{label}\g<3>",
                    block,
                    count=1,
                    flags=re.DOTALL,
                )
                replaced = True
            parts.append(block)
            last = m.end()
        parts.append(text[last:])
        text = "".join(parts)
    return text



def sync(*, manifest_url: str, check_only: bool) -> int:
    manifest = load_json(manifest_url)
    new_pins = pins_from_manifest(manifest)
    old_pins = json.loads(PINS_PATH.read_text(encoding="utf-8")) if PINS_PATH.exists() else {}
    pairs = replacement_pairs(old_pins, new_pins) if old_pins else []

    # Always rewrite structured machine-interface release field from new pins.
    planned: dict[str, str] = {}
    for rel in TARGET_FILES:
        path = ROOT / rel
        if not path.is_file():
            continue
        original = path.read_text(encoding="utf-8")
        updated = apply_replacements(original, pairs) if pairs else original
        if rel == "docs/AGENT_SETUP.md":
            updated = rewrite_mcp_bundle_block(updated, new_pins)
        if rel in ("web/index.html", "web/connect.html"):
            updated = apply_journey_badges(
                updated, manifest.get("journey_badges") or {}, html=True
            )
        if rel == "web/machine-interface.json":
            data = json.loads(updated)
            data["release"] = new_pins["toolkit"]
            updated = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        if rel == "automation/suite-pins.json":
            updated = json.dumps(new_pins, indent=2, ensure_ascii=False) + "\n"
        if updated != original:
            planned[rel] = updated

    if check_only:
        if planned:
            print("FAIL site pins drift: " + ", ".join(sorted(planned)))
            return 1
        # Also require suite-pins to equal manifest-derived pins.
        if old_pins != new_pins:
            print("FAIL automation/suite-pins.json disagrees with suite-manifest")
            return 1
        print("PASS site pins match suite-manifest")
        return 0

    if not planned and old_pins == new_pins:
        print("site pins already match suite-manifest")
        return 0

    for rel, content in planned.items():
        (ROOT / rel).write_text(content, encoding="utf-8")
    if "automation/suite-pins.json" not in planned:
        PINS_PATH.write_text(json.dumps(new_pins, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"synced {len(planned) or 1} path(s) from suite-manifest")
    for key in ("toolkit", "mcp", "peace_os", "agentic"):
        print(f"  {key}: {new_pins[key]}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help="suite-manifest URL or path")
    parser.add_argument("--check", action="store_true", help="exit 1 when a rewrite is needed")
    args = parser.parse_args()
    return sync(manifest_url=args.manifest, check_only=args.check)


if __name__ == "__main__":
    sys.exit(main())
