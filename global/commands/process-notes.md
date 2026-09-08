# Process meeting notes

## Before starting
Load CLAUDE.md — project roster, org names, and all file locations.
All file paths used in this pipeline are read from CLAUDE.md under "Key file locations".

## Pre-flight check — run before Stage 1

Check the following in order.

### Blocking (stop entirely):
- If the transcripts folder (listed in CLAUDE.md) is empty:
  Print "No transcript found in [transcripts path] — add a transcript file and run /process-notes again."
  Stop. Do not proceed.

### Warnings (collect all, then ask once):
- CLAUDE.md roster contains a `[Name]` placeholder → "Roster has placeholder entries — attribution validation will be unreliable."
- The formatter skill file (listed in CLAUDE.md) contains `[TO BE FILLED IN]` → "Formatter skill file has unfilled sections — output quality may be low."
- The style rules skill file (listed in CLAUDE.md) contains `[TO BE FILLED IN]` → "Style rules skill file has unfilled sections — output quality may be low."
- The humanizer skill file (listed in CLAUDE.md) is missing, or its `references/` folder is empty → "Humanizer skill not found — Stage 2 will run the editorial pass only."

If any warnings exist, print all of them, then ask:
"Proceed anyway? (y/n)"
If n: stop. If y: proceed to Stage 1.
If no warnings: proceed to Stage 1 silently.

---

## Pipeline — 5 stages in strict order, no skipping

Agents return pipeline metadata lines after the draft: EDITORIAL NOTE, HUMANIZER NOTE,
DISCIPLINE NOTE, SUPERVISOR NOTE. Collect each one for the summary report, then strip it
before passing the draft to the next stage. No NOTE line ever reaches the docx-renderer.

### Stage 1 — formatter
Find the most recent file in the transcripts folder listed in CLAUDE.md.

Files to pass to the formatter agent:
- CLAUDE.md
- The formatter skill file listed in CLAUDE.md
- The style rules skill file listed in CLAUDE.md
- The style rules skill references/ subfolder (structure.md and typography.md, at the same path as the style rules skill)
- The hard rules skill file listed in CLAUDE.md
- The hard rules skill references/ subfolder (terminology.md, at the same path as the hard rules skill)

Receive complete first draft.

### Stage 2 — editorial-qa
Files to pass to the editorial-qa agent:
- Stage 1 draft
- CLAUDE.md
- The style rules skill file listed in CLAUDE.md
- The style rules typography reference (at the same path as the style rules skill)
- The hard rules skill file listed in CLAUDE.md
- The hard rules terminology reference (at the same path as the hard rules skill)
- The humanizer skill file listed in CLAUDE.md
- The humanizer references/ subfolder (at the same path as the humanizer skill)

The agent runs two passes: editorial sharpening, then AI-writing cleanup scoped by the
humanizer skill file. Stages 3 and 4 re-validate its output, so it runs here and nowhere else.

Receive sharpened draft plus EDITORIAL NOTE and HUMANIZER NOTE.

### Stage 3 — discipline-checker
Files to pass to the discipline-checker agent:
- Stage 2 draft
- CLAUDE.md
- The hard rules skill file listed in CLAUDE.md
- The hard rules terminology reference (at the same path as the hard rules skill)

Receive corrected draft plus DISCIPLINE NOTE.

### Stage 4 — supervisor-alignment
Files to pass to the supervisor-alignment agent:
- Stage 3 draft
- CLAUDE.md
- The supervisor style guide file listed in CLAUDE.md

Agent applies manually seeded preferences always, and recurring corrections once the
threshold in CLAUDE.md is reached.
Receive final draft.

### Stage 5 — docx-renderer
Files to pass to the docx-renderer agent:
- Stage 4 final draft (markdown)
- CLAUDE.md

Agent clones the blank template, replaces the document body with rendered XML, repacks,
validates, and saves the output file.
Receive completion status and output file path.

## Summary report — print after Stage 5 completes
- Which transcript was processed and its date
- EDITORIAL NOTE from Stage 2
- HUMANIZER NOTE from Stage 2
- DISCIPLINE NOTE from Stage 3
- SUPERVISOR NOTE from Stage 4 (if recurring corrections not yet at threshold)
- Output file path from Stage 5
