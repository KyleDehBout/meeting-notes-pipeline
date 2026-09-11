# Process meeting notes

## Before starting
Load CLAUDE.md — project roster, org names, and all file locations.
All file paths used in this pipeline are read from CLAUDE.md under "Key file locations".

## Pre-flight check — run before Stage 1

Check the following in order.

### What counts as a transcript
Before any check below, build the candidate list from the transcripts folder. A file is a
candidate only if ALL of the following hold:
- the filename does not start with `.` (excludes `.DS_Store`, `.gitkeep`)
- the filename does not start with `~$` (excludes Word lock files)
- it is a file, not a directory
- it is non-empty

"The most recent transcript" means the candidate with the newest modification time. If two
share a timestamp, take the one whose name sorts last.

### Blocking (stop entirely):
- If the candidate list is empty:
  Print "No transcript found in [transcripts path] — add a transcript file and run /process-notes again."
  Stop. Do not proceed.
  (Say this even when the folder contains files, if none of them are candidates — name the
  files that were skipped and why.)

- If the DOCX blank template listed in CLAUDE.md does not exist on disk:
  Print "DOCX blank template not found at [path] — Stage 5 cannot render. Run
  setup_docx_renderer.py before /process-notes."
  Stop. Do not proceed. Stage 5 would fail after four stages of work have already run.

### Warnings (collect all, then ask once):
- CLAUDE.md roster contains a `[Name]` placeholder → "Roster has placeholder entries — attribution validation will be unreliable."
- The formatter skill file (listed in CLAUDE.md) contains `[TO BE FILLED IN]` → "Formatter skill file has unfilled sections — output quality may be low."
- The style rules skill file (listed in CLAUDE.md) contains `[TO BE FILLED IN]` → "Style rules skill file has unfilled sections — output quality may be low."
- The humanizer skill file (listed in CLAUDE.md) is missing, or its `references/` folder is empty → "Humanizer skill not found — Stage 2 will run the editorial pass only."
- More than one candidate transcript is present → "N transcripts present — only the most recent ([filename]) will be processed."
- The output folder already contains a draft whose name or content matches the transcript about to be processed → "[filename] appears to have been processed already — running again will produce a duplicate draft."

If any warnings exist, print all of them, then ask:
"Proceed anyway? (y/n)"
If n: stop. If y: proceed to Stage 1.
If no warnings: proceed to Stage 1 silently.

---

## Pipeline — 5 stages in strict order, no skipping

**If any stage fails, stop the pipeline there.** A stage has failed if its agent returns an
error, returns nothing, or returns a draft that is empty or obviously truncated. When that
happens: print "PIPELINE FAILED at Stage [N] ([agent name]): [what went wrong]", print the
notes collected from the stages that did complete, and stop. Never pass a failed or empty
draft to the next stage, never substitute your own draft for a failed agent's output, and
never print the summary report as though the run succeeded.

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
- The hard rules skill file listed in CLAUDE.md — Stage 4 is the last stage that edits
  text, so nothing re-validates what it applies; it needs the hard rules to know which
  preferences it must refuse

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
- Output file path from Stage 5 — or, if Stage 5 reported a render failure, the failure
  message and the path to the Stage 4 markdown draft so the work is not lost
