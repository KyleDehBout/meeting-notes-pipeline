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

If any warnings exist, print all of them, then ask:
"Proceed anyway? (y/n)"
If n: stop. If y: proceed to Stage 1.
If no warnings: proceed to Stage 1 silently.

---

## Pipeline — 4 stages in strict order, no skipping

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
- The style rules skill file listed in CLAUDE.md

Receive sharpened draft plus EDITORIAL NOTE.

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

## Output
Save final draft to the output folder listed in CLAUDE.md, named:
meeting-notes-YYYY-MM-DD.docx

## Summary report — print after saving
- Which transcript was processed and its date
- EDITORIAL NOTE from Stage 2
- DISCIPLINE NOTE from Stage 3
- SUPERVISOR NOTE from Stage 4 (if recurring corrections not yet at threshold)
