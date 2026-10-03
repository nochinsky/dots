#!/usr/bin/env python3
"""Check shipped data formats and local documentation links without installing."""

import json
from pathlib import Path
import re
import tomllib
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

for path in (ROOT / "modules").rglob("*.toml"):
    tomllib.loads(path.read_text())
for path in (ROOT / "examples").glob("*.toml"):
    tomllib.loads(path.read_text())
for path in (ROOT / "modules/fastfetch").rglob("*.jsonc"):
    # This snapshot is JSON with a .jsonc extension; no comments to strip.
    json.loads(path.read_text())
for path in (ROOT / "modules/fonts").rglob("*.conf"):
    ET.parse(path)

for path in [ROOT / "README.md", *(ROOT / "docs").glob("*.md")]:
    for link in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", path.read_text()):
        parsed = urlsplit(link)
        if parsed.scheme or not parsed.path or link.startswith("#"):
            continue
        target = path.parent / unquote(parsed.path)
        if not target.exists():
            raise SystemExit(f"Broken link in {path.relative_to(ROOT)}: {link}")
print("TOML, JSON, fontconfig XML, and local documentation links are valid.")
