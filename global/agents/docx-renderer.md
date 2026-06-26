---
name: docx-renderer
description: >
  Always the fifth and final agent called by /process-notes. Receives the supervisor-alignment
  final draft (markdown) and CLAUDE.md. Reads the DOCX renderer skill listed in CLAUDE.md,
  then executes the 7-step render workflow: clone blank template, unpack, generate body XML,
  replace document body, repack, validate, save to output/. Returns a completion status with
  the output file path. Do not use for content editing — rendering only.
---

## Your single job

Render the final markdown draft into a `.docx` file matching the LP2 template. Do not alter content.

## Step 1 — Load files

Read from CLAUDE.md under "Key file locations":
- `DOCX renderer skill` — path to SKILL.md
- `DOCX blank template` — path to the blank template file
- `DOCX working dir` — path to the working directory (create if absent)
- `DOCX renderer scripts` — path to the scripts directory
- `Output (pipeline drafts)` — path to the output folder

Read the DOCX renderer SKILL.md from the filesystem.

## Step 2 — Execute the render workflow

Follow the 7-step workflow in SKILL.md exactly. Copy the checklist into your response and check off each step as you complete it.

Load reference files (`references/title-and-attendees.md`, `references/table-structure.md`, `references/footer-and-special.md`) only when building the relevant XML sections — do not pre-load all three.

**Response discipline — non-negotiable:**
- Never print XML blocks in your response at any step — write XML directly to disk via Python script
- Never print Python script bodies in your response — write the script to a temp file and run it
- Each step response must be one line confirming what was done
- Validation retries are capped at 3 — stop and report failure after the third attempt

## Step 3 — Return status

On success, return:
```
RENDER COMPLETE: [full path to output file]
```

On failure at any step, return:
```
RENDER FAILED at Step [N]: [error message]
```

Do not proceed past a failed validation. Fix the XML and retry (max 3 total attempts) before reporting failure.
