#!/usr/bin/env python3
"""Write and open the project setup form.

Renders assets/setup-form.html into a standalone setup-session.html with any
values extracted from an uploaded .docx injected as prefill, then opens it in
the default browser.

Usage:
  python scripts/generate_setup_form.py [--out DIR] [--prefill FILE|JSON] [--no-open]

The generated file is self-contained: no network, no CDN, works offline.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

PLACEHOLDER = "__PREFILL__"
TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "setup-form.html"


def load_prefill(raw):
    """Accept a path to a JSON file, a literal JSON string, or nothing."""
    if not raw:
        return {}
    candidate = Path(raw)
    if candidate.is_file():
        raw = candidate.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.exit(f"error: --prefill is not valid JSON ({exc})")
    if not isinstance(data, dict):
        sys.exit("error: --prefill must be a JSON object")
    return data


def open_in_browser(path):
    if sys.platform == "darwin":
        cmd = ["open", str(path)]
    elif sys.platform.startswith("win"):
        cmd = ["cmd", "/c", "start", "", str(path)]
    else:
        cmd = ["xdg-open", str(path)]
    try:
        subprocess.run(cmd, check=True)
        return True
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"warning: could not open a browser ({exc})", file=sys.stderr)
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=".", help="directory to write setup-session.html into")
    ap.add_argument("--prefill", default="", help="JSON file or literal JSON of extracted values")
    ap.add_argument("--no-open", action="store_true", help="write the file but do not open a browser")
    args = ap.parse_args()

    if not TEMPLATE.is_file():
        sys.exit(f"error: form template missing at {TEMPLATE}")

    html = TEMPLATE.read_text(encoding="utf-8")
    if PLACEHOLDER not in html:
        sys.exit(f"error: {PLACEHOLDER} not found in {TEMPLATE}")

    prefill = load_prefill(args.prefill)
    html = html.replace(PLACEHOLDER, json.dumps(prefill, ensure_ascii=False))

    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "setup-session.html"
    out_file.write_text(html, encoding="utf-8")

    opened = False if args.no_open else open_in_browser(out_file)
    print(str(out_file))
    print("opened" if opened else "not opened")


if __name__ == "__main__":
    main()
