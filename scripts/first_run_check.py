#!/usr/bin/env python3
"""First-run rule for the Meeting Notes Pipeline.

Wired to SessionStart in .claude/settings.json. On the first session after
someone clones this repo, it opens the project setup form in a browser and
tells Claude to wait for the pasted setup block. Every session after that it
does nothing.

The marker that makes it fire once lives at .claude/.setup-state.json and is
gitignored, so a fresh clone always gets the form.

Escape hatches:
  MNP_SKIP_FIRST_RUN=1   skip entirely
  Delete .claude/.setup-state.json to make the form fire again.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MARKER = REPO / ".claude" / ".setup-state.json"
GENERATOR = REPO / "scripts" / "generate_setup_form.py"
FORM_TEMPLATE = REPO / "assets" / "setup-form.html"

CONTEXT = """\
FIRST RUN — Meeting Notes Pipeline setup has been triggered automatically.

The project setup form has been opened in the user's browser at:
  {form}

This replaces the terminal questions in Step 1 of /setup-pipeline. Do not ask the
user for project name, path, roster, or organisation names in the terminal — the
form collects all of it.

Say exactly this and then stop and wait:

---
Welcome — this looks like a fresh install, so I have opened the project setup form
in your browser.

Fill it in, click "Generate setup block", then either "Copy to clipboard" or
"Copy & close", and paste the result back here. Setup runs automatically from there.

Optional: if you have past meeting notes as a .docx, upload the file here first and
I will read your roster, organisation names, and style out of it and reopen the form
with those fields already filled in.
---

When the user pastes a block that starts with ==PROJECT_SETUP==, follow
/setup-pipeline from Step 2 onward using the pasted values. Do not re-ask anything
the block already answers.

If the user uploads a .docx first, extract EXTRACTED_DATA per Step 0 of
/setup-pipeline, then regenerate the form with those values:
  python3 scripts/generate_setup_form.py --prefill '<json>'
"""


def emit(context=None):
    """SessionStart hooks pass text to Claude via additionalContext."""
    if context:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context,
            }
        }))
    sys.exit(0)


def main():
    if os.environ.get("MNP_SKIP_FIRST_RUN"):
        emit()

    # Already set up, or not actually this repo — stay quiet.
    if MARKER.exists() or not FORM_TEMPLATE.is_file() or not GENERATOR.is_file():
        emit()

    try:
        result = subprocess.run(
            [sys.executable, str(GENERATOR), "--out", str(REPO)],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        emit(f"First-run setup form could not be opened ({exc}). "
             f"Tell the user to run /setup-pipeline manually.")

    if result.returncode != 0:
        emit(f"First-run setup form failed to generate:\n{result.stderr.strip()}\n"
             f"Tell the user to run /setup-pipeline manually.")

    form_path = result.stdout.strip().splitlines()[0] if result.stdout.strip() else str(REPO / "setup-session.html")
    emit(CONTEXT.format(form=form_path))


if __name__ == "__main__":
    main()
