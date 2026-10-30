#!/usr/bin/env python3
"""Render AGENT_SETUP.md and JOURNEYS.md to simple HTML with heading anchors."""
from __future__ import annotations
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
OUT = ROOT / "web"

def slug(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")

def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text

def render(md: str, title: str) -> str:
    lines = md.splitlines()
    body: list[str] = []
    in_code = False
    code_lang = ""
    list_type = None
    def close_list():
        nonlocal list_type
        if list_type:
            body.append(f"</{list_type}>")
            list_type = None
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            close_list()
            if not in_code:
                in_code = True
                code_lang = line[3:].strip()
                body.append(f'<pre tabindex="0"><code class="language-{html.escape(code_lang)}">')
            else:
                in_code = False
                body.append("</code></pre>")
            i += 1
            continue
        if in_code:
            body.append(html.escape(line) + "\n")
            i += 1
            continue
        if not line.strip():
            close_list()
            i += 1
            continue
        heading = re.match(r"^(#{1,3})\s+(.*)$", line)
        if heading:
            close_list()
            level = len(heading.group(1))
            text = heading.group(2).strip()
            hid = slug(text)
            body.append(f'<h{level} id="{html.escape(hid)}">{inline(text)}</h{level}>')
            i += 1
            continue
        if re.match(r"^[-*]\s+", line):
            if list_type != "ul":
                close_list()
                body.append("<ul>")
                list_type = "ul"
            item = re.sub(r"^[-*]\s+", "", line)
            body.append(f"<li>{inline(item)}</li>")
            i += 1
            continue
        if re.match(r"^\d+\.\s+", line):
            if list_type != "ol":
                close_list()
                body.append("<ol>")
                list_type = "ol"
            item = re.sub(r"^\d+\.\s+", "", line)
            body.append(f"<li>{inline(item)}</li>")
            i += 1
            continue
        if line.strip() == "---":
            close_list()
            body.append("<hr>")
            i += 1
            continue
        close_list()
        body.append(f"<p>{inline(line)}</p>")
        i += 1
    close_list()
    content = "\n".join(body)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'; worker-src 'none'">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} · Global AI Governance</title>
  <link rel="stylesheet" href="./styles.css?v=2.8.2">
  <link rel="canonical" href="https://ai-governance.solutions/{html.escape(title.replace(' ', '_'))}.html">
</head>
<body>
  <a class="skip-link" href="#top">Skip to main content</a>
  <nav class="gaig-bar shell" aria-label="Global AI Governance sites">
    <a class="gaig-brand" href="./">Global AI Governance</a>
    <span class="gaig-links"><a href="./start.html">Start here</a><a href="./#toolkit">Toolkit</a><a href="./connect.html">Connect</a><a href="./lead-agent/">Lead Agent</a><a href="./interoperability.html">Interop</a><a href="//global-ai-governance.github.io/containment-ledger/">Containment Ledger</a><a href="//global-ai-governance.github.io/peace-os/">Peace OS</a></span>
    <a class="gaig-cta" href="./connect.html#agents">Connect your agent</a>
  </nav>
  <main id="top" class="shell connect-section" tabindex="-1">
{content}
  </main>
  <footer class="shell gaig-footer"><p>Global AI Governance · Non-authorizing · <a href="https://github.com/GLOBAL-AI-GOVERNANCE">GitHub</a></p></footer>
</body>
</html>
"""

def main() -> None:
    mapping = {
        "AGENT_SETUP.md": ("Agent setup", "AGENT_SETUP.html"),
        "JOURNEYS.md": ("JOURNEYS", "JOURNEYS.html"),
    }
    for src, (title, out_name) in mapping.items():
        md = (DOCS / src).read_text(encoding="utf-8")
        # Prefer site HTML anchors over .md# in rendered copy
        md = md.replace("https://ai-governance.solutions/AGENT_SETUP.md#", "./AGENT_SETUP.html#")
        md = md.replace("https://ai-governance.solutions/AGENT_SETUP.md", "./AGENT_SETUP.html")
        md = md.replace("https://ai-governance.solutions/JOURNEYS.md", "./JOURNEYS.html")
        (OUT / out_name).write_text(render(md, title), encoding="utf-8")
        print("wrote", out_name)

if __name__ == "__main__":
    main()
