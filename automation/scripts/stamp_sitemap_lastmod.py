#!/usr/bin/env python3
"""Stamp every sitemap <lastmod> with today's UTC date (CI deploy hygiene)."""
from __future__ import annotations
import re
from datetime import date, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / "web" / "sitemap.xml"
today = date.today().isoformat()
text = path.read_text(encoding="utf-8")
if "<lastmod>" in text:
    text = re.sub(r"<lastmod>[^<]+</lastmod>", f"<lastmod>{today}</lastmod>", text)
else:
    text = text.replace("</loc>", f"</loc>\n    <lastmod>{today}</lastmod>")
path.write_text(text, encoding="utf-8")
print("sitemap lastmod", today)
