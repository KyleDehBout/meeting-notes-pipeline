# Setup Meeting Notes Pipeline

## What this does
Installs the global pipeline components into your Claude Code configuration and scaffolds
a new project folder ready to use. If you provide past meeting notes, the setup extracts
your style, roster, and organisation names automatically.

Project details are collected in a browser form, not in the terminal. On a fresh clone the
form opens by itself; the user fills it in, copies the generated block, and pastes it back
into Claude Code. See Step 1.

---

## Step 0 — Upload documents

Before asking any questions, prompt the user with exactly this:

---
Before we set up your project, do you have any past meeting notes you'd like to upload?

Upload one or two finished .docx files you're happy with — I'll extract your style, roster,
organisation names, and document branding automatically, and use them to pre-fill your project
files. Say "skip" to fill everything in manually.
---

Wait for the user to respond.

### Handling the upload:

Past meeting notes almost always carry the organisation's branded header, footer, and logo.
When a .docx is uploaded, it serves two purposes simultaneously:

1. **Template source** — the body content is stripped and the file becomes the blank template
   that every rendered output is cloned from, preserving headers, footers, logos, styles, and
   fonts automatically.
2. **Style reference** — the content is read to extract roster, tone, terminology, and structure.

Save the first uploaded .docx file path as TEMPLATE_SOURCE.

If the user uploads no .docx file (uploads only text/paste, or says "skip"):
- Set TEMPLATE_SOURCE to empty.
- Ask once: "Do you have a branded .docx file — any meeting notes or letterhead — I can use
  to set up the document template? This gives every output your organisation's header, footer,
  and logo automatically."
- If still none: set TEMPLATE_SOURCE to empty and warn at the end of setup:
  "⚠ No .docx uploaded — the DOCX renderer will not be fully set up. Run this when you have
  a file: python3 Meeting Notes/skills/docx-renderer/scripts/setup_docx_renderer.py <source.docx>
  <ProjectName> <Meeting Notes path>"

### Handling past notes:

If the user uploads or pastes past notes, read every document fully before proceeding. Extract
the following silently — do not print the analysis, just hold it for use in later steps:

**From the Attendees section:**
- Team roster: every person's full name, organisation, and title
- Organisation names: every org listed (these become the Action column source of truth)

**From the document structure:**
- Header layout: what appears, in what order, what formatting
- Section numbering format (e.g. 1. / 1.1 / 1.1.1 or A. / A.1 etc.)
- Whether subsections use bold, italic, or plain labels
- Column layout: how many columns, what they are, how they are headed

**From the content:**
- Tone and register: formal/informal, first/third person, outcome-focused vs. discussion-focused
- Action column convention: org name only, individual name, initials, or mixed
- Status values used and what they appear to mean
- Whether speaker attribution is used or avoided
- Preferred constructions (e.g. "[Org] to provide..." vs "[Org] will provide...")
- Date format used in the header
- Text weight conventions (what is bold, italic, plain)
- Any technical terms, abbreviations, or project-specific vocabulary

**Confidence flag each item** internally as HIGH (clearly consistent across the document),
MEDIUM (present but ambiguous), or LOW (inferred/uncertain). HIGH and MEDIUM items
are used to auto-populate files. LOW items are flagged for the user to confirm.

Save all extracted data as EXTRACTED_DATA for use in Steps 1–4.

### If the user says "skip" for past notes:
Set EXTRACTED_DATA to empty. Proceed to Step 1 and open the setup form with no prefill.

---

## Step 1 — Collect project information via the setup form

**Hardcoded rule: project information is always collected in the browser form, never by
asking the questions one at a time in the terminal.**

On a fresh clone the SessionStart hook (`scripts/first_run_check.py`, wired in
`.claude/settings.json`) has already generated and opened the form before this command
runs. In that case skip straight to Step 1c and wait for the paste.

If the form is not already open — the user ran `/setup-pipeline` by hand, or setup has run
on this machine before — generate and open it now.

### Step 1a — Build the prefill object

If EXTRACTED_DATA is empty, the prefill is `{}` — skip to Step 1b.

Otherwise build a JSON object from the HIGH and MEDIUM confidence items only. LOW
confidence items are left blank so the user fills them in deliberately. Use this exact
shape; every key is optional:

```json
{
  "project": "SFV",
  "path": "/Users/you/Projects/SFV",
  "folderName": "Site Minutes",
  "templateSource": "/Users/you/Documents/past-minutes.docx",
  "roster": [{"name": "Jane Smith", "org": "Acme Corp", "title": "Structural Engineer"}],
  "orgs": "Acme Corp, BuildCo, City Council",
  "actionColumn": "ORG_ONLY",
  "dateFormat": "Monday 22 June 2026",
  "numbering": "DECIMAL",
  "tone": "FORMAL_THIRD",
  "attribution": "NEVER",
  "statusValues": "In Progress, Pending, No Action",
  "terms": "precast panels, ROW, BQ",
  "threshold": "3",
  "sourceNote": "Prefilled from past-minutes.docx — check each field before submitting."
}
```

Dropdown values must match the option values in `assets/setup-form.html` exactly, or the
dropdown silently keeps its default:

- `actionColumn`: ORG_ONLY | INDIVIDUAL | INITIALS | MIXED
- `numbering`: DECIMAL | ALPHA | MIXED | NONE
- `tone`: FORMAL_THIRD | FORMAL_FIRST | NEUTRAL | INFORMAL
- `attribution`: NEVER | DECISIONS | ALWAYS
- `threshold`: 3 | 5 | 10
- `dateFormat`: one of the six literal strings listed in the form

Write the JSON to a temporary file rather than passing it inline — rosters and
organisation lists contain quotes and commas that break shell escaping.

### Step 1b — Generate and open the form

```bash
python3 "[repo-root]/scripts/generate_setup_form.py" \
  --out "[repo-root]" \
  --prefill "[path to prefill.json]"
```

Omit `--prefill` entirely when EXTRACTED_DATA is empty. The script writes
`setup-session.html` and opens it in the default browser. The file is self-contained — no
network, no CDN, works offline — and is gitignored.

If the script prints `not opened`, print the file path and ask the user to open it manually.

### Step 1c — Wait for the pasted block

Print exactly this and nothing else:

---
Setup form open in your browser.

Fill it in, click "Generate setup block", then either "Copy to clipboard" or
"Copy & close", and paste the result back here.
---

Then stop. Do not ask setup questions in the terminal. Do not proceed until the user
pastes. If the user answers in prose instead of pasting, accept the prose — do not send
them back to the form.

### Step 1d — Parse the pasted block

The paste is delimited by `==PROJECT_SETUP==` and `==END_SETUP==`. Read these values:

| Key in block | Variable | Notes |
|---|---|---|
| PROJECT_NAME | PROJECT_NAME | required |
| PROJECT_PATH | PROJECT_PATH | required — project root, not the Meeting Notes subfolder |
| MEETING_NOTES_FOLDER | MEETING_NOTES_FOLDER | |
| FOLDER_MODE | FOLDER_MODE | CREATE or EXISTING |
| EXISTING_DOCS | EXISTING_DOCS | ARCHIVE or LEAVE |
| TEMPLATE_SOURCE | TEMPLATE_SOURCE | `none` means empty |
| `--- ROSTER ---` rows | ROSTER | one `\| Name \| Organisation \| Title \|` row per person |
| ORG_NAMES | ORG_NAMES | |
| ACTION_COLUMN | ACTION_COLUMN | |
| DATE_FORMAT | DATE_FORMAT | |
| NUMBERING | NUMBERING | |
| TONE | TONE | |
| SPEAKER_ATTRIBUTION | SPEAKER_ATTRIBUTION | |
| STATUS_VALUES | STATUS_VALUES | |
| TERMINOLOGY | TERMINOLOGY | `none` means empty |
| SUPERVISOR_THRESHOLD | SUPERVISOR_THRESHOLD | |
| CREATE_LAUNCHER | CREATE_LAUNCHER | YES or NO |
| NOTES | NOTES | `none` means empty |

Then run these checks before continuing:

- PROJECT_PATH exists. If not, ask whether to create it.
- If FOLDER_MODE is EXISTING, PROJECT_PATH/MEETING_NOTES_FOLDER exists. If not, say so and
  create it.
- If TEMPLATE_SOURCE is set, the file exists and ends in `.docx`.

Ask about a failed check only. Everything that parsed cleanly is settled — do not read it
back to the user field by field for confirmation.

A value the user typed into the form always beats a value extracted from the uploaded
document. The form is the last word.

---

## Step 2 — Install global files

Determine the repo root (the directory containing this command's parent .claude/ folder).

Create ~/.claude/commands/ if it does not exist.
Create ~/.claude/agents/ if it does not exist.

For each file in [repo-root]/global/commands/:
- If a file with the same name already exists in ~/.claude/commands/:
  - Warn: "⚠ Skipped [filename] — already exists in ~/.claude/commands/. Review and merge manually if needed."
- Otherwise: copy it to ~/.claude/commands/.

For each file in [repo-root]/global/agents/:
- If a file with the same name already exists in ~/.claude/agents/:
  - Warn: "⚠ Skipped [filename] — already exists in ~/.claude/agents/. Review and merge manually if needed."
- Otherwise: copy it to ~/.claude/agents/.

---

## Step 3 — Scaffold project structure

### Handle existing Meeting Notes folder content
If MEETING_NOTES_FOLDER already existed and contains .pdf or .docx files directly in
its root (not in subfolders), ask:
"I found [N] document(s) in [MEETING_NOTES_FOLDER]/. These look like issued meeting notes.
Shall I move them to [MEETING_NOTES_FOLDER]/Archive/ to keep the folder clean? (y/n)"
If y: create Archive/ and move those files there.
If n: leave them in place.

### Create subfolders inside Meeting Notes
Create the following inside PROJECT_PATH/MEETING_NOTES_FOLDER/:
- Archive/
- transcripts/
- output/
- intake/
- working/
- skills/style-rules/references/
- skills/hard-rules/references/
- skills/humanizer/references/
- skills/docx-renderer/references/
- skills/docx-renderer/scripts/

### Copy template files
Copy all files from [repo-root]/project-template/Meeting Notes/ into
PROJECT_PATH/MEETING_NOTES_FOLDER/, with these renames — replace the literal string
[PROJECT] with PROJECT_NAME:
- supervisor-style-guide-[PROJECT].md → supervisor-style-guide-PROJECT_NAME.md
- pipeline-memory-[PROJECT].md → pipeline-memory-PROJECT_NAME.md
- meeting-notes-formatter-skill-[PROJECT].md → meeting-notes-formatter-skill-PROJECT_NAME.md

Copy skills/ subdirectory contents preserving folder structure.
Do not copy .gitkeep files.

### Run DOCX renderer setup

If TEMPLATE_SOURCE is set, run the setup script. This single step creates the blank
template AND extracts all formatting values (fonts, column widths, spacing, colours,
tab stops, numIds) from the source document, rendering them into the docx-renderer
reference files — no manual editing required.

```bash
python3 "[PROJECT_PATH/MEETING_NOTES_FOLDER/skills/docx-renderer/scripts/setup_docx_renderer.py]" \
  "[TEMPLATE_SOURCE]" \
  "[PROJECT_NAME]" \
  "[PROJECT_PATH/MEETING_NOTES_FOLDER]" \
  --date-format "[DATE_FORMAT]"
```

Pass DATE_FORMAT exactly as the form gave it — it is a literal example date, not a
strftime pattern. The renderer reference and the style skill's `typography.md` must state
the same convention; this flag is what keeps them in step.

**This runs once and only once.** The script writes
`skills/docx-renderer/references/.rendered.json` when it finishes. On any later run it
sees that marker and exits without touching a single file, so the reference files —
including anything the user has edited by hand — are never overwritten by a second
setup, by `/process-notes`, or by anything else in the pipeline.

Never add `--force` on your own initiative. It re-derives every reference file from a
new .docx and discards hand edits. Use it only when the user explicitly asks to rebuild
the template from a different document.

If the script completes successfully: save the blank template path as BLANK_TEMPLATE_PATH.
If it fails: print the error, set BLANK_TEMPLATE_PATH to empty, and warn the user they will
need to run setup_docx_renderer.py manually before using /process-notes.

If it prints "Setup has already run for this project", that is not an error — the project
already has its template. Save the existing blank template path as BLANK_TEMPLATE_PATH and
carry on.

### Create CLAUDE.md at project root
Copy [repo-root]/project-template/CLAUDE.md to PROJECT_PATH/CLAUDE.md.

### Create Claude launcher

Skip this whole section if CREATE_LAUNCHER is NO.

Create a file at PROJECT_PATH named exactly:
  Claude — PROJECT_NAME Meeting Notes Launcher.command

Write the following content into it:
```
#!/bin/bash
cd "$(dirname "$0")"
claude
```

Make it executable:
  chmod +x "PROJECT_PATH/Claude — PROJECT_NAME Meeting Notes Launcher.command"

---

## Step 4 — Populate project files

### CLAUDE.md
Open the newly created CLAUDE.md at PROJECT_PATH and make the following replacements:
- [PROJECT NAME] → PROJECT_NAME
- [FULL PATH TO PROJECT FOLDER] → PROJECT_PATH
- Every occurrence of `Meeting Notes/` in file location values → MEETING_NOTES_FOLDER/
- Every occurrence of [PROJECT] in file location values → PROJECT_NAME
- Placeholder roster rows → one table row per ROSTER entry: | Name | Organisation | Title |
- [Org1, Org2, Org3...] → ORG_NAMES (comma-separated, exactly as confirmed)
- `Supervisor activation threshold: 3` → SUPERVISOR_THRESHOLD

If NOTES is not empty, append a `## Project notes` section at the end of CLAUDE.md
containing that text verbatim.

### DOCX renderer entries in CLAUDE.md

In addition to the standard replacements, fill in the four DOCX renderer keys:
- `[PROJECT]_blank_template.docx` → BLANK_TEMPLATE_PATH (or leave with warning comment if not set)
- `DOCX renderer scripts` → `MEETING_NOTES_FOLDER/skills/docx-renderer/scripts/`
- `DOCX working dir` → `MEETING_NOTES_FOLDER/working/`
- `DOCX renderer skill` → `MEETING_NOTES_FOLDER/skills/docx-renderer/SKILL.md`
- `Humanizer skill` → `MEETING_NOTES_FOLDER/skills/humanizer/SKILL.md`

### Formatter skill file
Open meeting-notes-formatter-skill-PROJECT_NAME.md.
Replace [PROJECT NAME] in the heading with PROJECT_NAME.

For each section of the Established Style Profile:
- If EXTRACTED_DATA has HIGH or MEDIUM confidence: replace [TO BE FILLED IN] with extracted
  content written as specific, actionable rules. Style conventions only — no actual content
  (names, dates, decisions) from the uploaded notes.
- If EXTRACTED_DATA is empty or LOW confidence: leave [TO BE FILLED IN] but replace the
  comment block with a targeted prompt noting what to fill in.

### Apply the form's style answers

The form answers are explicit user choices, so they outrank anything inferred from the
uploaded document. Write each one into the formatter skill file as a stated rule:

- DATE_FORMAT → the header date convention, written out as the literal example
- NUMBERING → the section numbering scheme (DECIMAL `1. / 1.1 / 1.1.1`, ALPHA `A. / A.1`,
  MIXED `1) / a) / i)`, NONE for headings only)
- TONE → register (FORMAL_THIRD, FORMAL_FIRST, NEUTRAL, INFORMAL)
- SPEAKER_ATTRIBUTION → NEVER, DECISIONS, or ALWAYS
- ACTION_COLUMN → what goes in the Action column (ORG_ONLY, INDIVIDUAL, INITIALS, MIXED)
- STATUS_VALUES → the permitted status values, verbatim

Where a form answer and EXTRACTED_DATA disagree, the form wins and no question is asked.

If ACTION_COLUMN is anything other than ORG_ONLY, note in the hard rules skill that the
default org-only attribution rule has been overridden for this project, so
`discipline-checker` validates against the chosen convention instead.

### Style rules and hard rules skill files
Apply the same logic — populate where EXTRACTED_DATA is HIGH/MEDIUM, leave targeted
prompts elsewhere.

The hard rules terminology reference: add every term from TERMINOLOGY, plus any technical
terms extracted from uploaded notes, under the appropriate category.

### Humanizer skill file
Do not populate this one. It ships complete and is project-independent — copy
`skills/humanizer/` across as-is, including `references/`. It has no `[TO BE FILLED IN]`
sections and takes no extracted data.

---

## Step 5 — Mark setup complete

Write the marker that tells the first-run hook not to reopen the form. Without this the
setup form pops up again on the next session.

Write to `[repo-root]/.claude/.setup-state.json`:

```json
{
  "setupComplete": true,
  "completedAt": "[ISO 8601 timestamp]",
  "project": "[PROJECT_NAME]",
  "projectPath": "[PROJECT_PATH]"
}
```

Then delete the generated form so it does not sit stale in the repo root:

```bash
rm -f "[repo-root]/setup-session.html"
```

Both paths are gitignored. To set up a second project later, the user runs
`/setup-pipeline` by hand — the hook only ever fires on a fresh clone.

---

## Step 6 — Print confirmation

Print exactly this (substituting real values):

---
Pipeline installed.

Global files added to:
  ~/.claude/commands/
  ~/.claude/agents/

Project scaffolded at:
  PROJECT_PATH/
  └── CLAUDE.md  ← open Claude Code from here or any subfolder

Meeting Notes folder:
  PROJECT_PATH/MEETING_NOTES_FOLDER/
  ├── transcripts/       ← drop transcripts here
  ├── output/            ← pipeline drafts appear here
  ├── intake/            ← drop supervisor-approved files here
  ├── Archive/           ← issued notes archive
  ├── working/           ← docx renderer scratch space (not for manual editing)
  └── skills/            ← your style, hard rules, humanizer, and docx renderer

[If CREATE_LAUNCHER is YES:]
Launcher created:
  PROJECT_PATH/Claude — PROJECT_NAME Meeting Notes Launcher.command
  └── Double-click this in Finder to open Claude Code in the right folder

[If BLANK_TEMPLATE_PATH is set:]
DOCX blank template created:
  BLANK_TEMPLATE_PATH
  └── Headers, footers, and branding preserved from your uploaded file

[If BLANK_TEMPLATE_PATH is empty:]
⚠ DOCX blank template not created — create it before running /process-notes:
  python3 MEETING_NOTES_FOLDER/skills/docx-renderer/scripts/setup_docx_renderer.py <source.docx> PROJECT_NAME MEETING_NOTES_FOLDER

  This also renders the reference files. It runs once — afterwards the files are yours to
  edit, and setup will not overwrite them. To rebuild from a different .docx, add --force.

Settings applied from the setup form:
  Date format          DATE_FORMAT
  Section numbering    NUMBERING
  Tone                 TONE
  Speaker attribution  SPEAKER_ATTRIBUTION
  Action column        ACTION_COLUMN
  Supervisor threshold SUPERVISOR_THRESHOLD

[If past notes were uploaded, include this block:]
Auto-populated from your uploaded notes:
  ✓ Team roster ([N] members)
  ✓ Organisation names ([N] orgs)
  ✓ Style profile — [list sections that were filled in]
  ✓ Terminology — [N terms added] (or "none found")

Still needs your input:
  [List any Style Profile sections left as [TO BE FILLED IN]]

Next steps:
1. Open Claude Code from PROJECT_PATH or PROJECT_PATH/MEETING_NOTES_FOLDER
2. Complete any [TO BE FILLED IN] sections in the skill files
3. Drop a transcript in MEETING_NOTES_FOLDER/transcripts/ and run /process-notes
---

Do not ask follow-up questions. The setup is complete.
