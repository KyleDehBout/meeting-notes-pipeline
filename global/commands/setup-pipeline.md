# Setup Meeting Notes Pipeline

## What this does
Installs the global pipeline components into your Claude Code configuration and scaffolds
a new project folder ready to use. If you provide past meeting notes, the setup extracts
your style, roster, and organisation names automatically.

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
  a file: python Meeting Notes/skills/docx-renderer/scripts/setup_docx_renderer.py <source.docx>
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
Set EXTRACTED_DATA to empty. Proceed to Step 1 with manual questions only.

---

## Step 1 — Collect project information

Ask the following questions. For any item where EXTRACTED_DATA contains a HIGH or MEDIUM
confidence answer, show the extracted value and ask the user to confirm or correct it
rather than asking from scratch.

1. "What is your project name or code? Use a short identifier — this becomes the suffix
   on your project files. (e.g. SFV, BRIDGE-02, RETAIL-Q4)"
   Save as PROJECT_NAME.

2. "Where is your project folder? Provide the full path to the root project folder —
   not the Meeting Notes subfolder, just the project root."
   Save as PROJECT_PATH.

3. "Does your project already have a Meeting Notes folder? If yes, tell me its name
   (e.g. 'Meeting Notes', 'Site Minutes', 'Minutes'). If not, I'll create one called
   'Meeting Notes' — just say 'create' or press enter to accept the default."
   - If user provides a name: save as MEETING_NOTES_FOLDER and verify the folder exists at PROJECT_PATH/MEETING_NOTES_FOLDER
   - If user says "create" or accepts default: set MEETING_NOTES_FOLDER = "Meeting Notes" and create it
   Save as MEETING_NOTES_FOLDER.

4. **Roster question** — handle based on EXTRACTED_DATA:
   - If roster was extracted with HIGH/MEDIUM confidence: present the extracted roster as a
     formatted table and ask "Does this look right? Add, remove, or correct any rows, then confirm."
   - If not extracted or LOW confidence: ask "List your team members. For each person enter:
     Name, Organisation, Title — one per line. Type DONE on its own line when finished."
   Save final list as ROSTER.

5. **Organisation names question** — handle based on EXTRACTED_DATA:
   - If org names were extracted with HIGH/MEDIUM confidence: present the extracted list and
     ask "Are these the organisation names that should appear in the Action column? Confirm or edit."
   - If not extracted or LOW confidence: ask "List all organisation names that will appear
     in the Action column, comma-separated. These must be exact — they are used for attribution validation."
   Save final list as ORG_NAMES.

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

If TEMPLATE_SOURCE is set, run the comprehensive setup script. This single step creates
the blank template AND extracts all formatting values (fonts, column widths, spacing,
colours, tab stops, numIds) from the source document to produce fully-populated reference
files — no manual editing of reference files required.

```bash
python "[PROJECT_PATH/MEETING_NOTES_FOLDER/skills/docx-renderer/scripts/setup_docx_renderer.py]" \
  "[TEMPLATE_SOURCE]" \
  "[PROJECT_NAME]" \
  "[PROJECT_PATH/MEETING_NOTES_FOLDER]"
```

If the script completes successfully: save the blank template path as BLANK_TEMPLATE_PATH.
If it fails: print the error, set BLANK_TEMPLATE_PATH to empty, and warn the user they will
need to run setup_docx_renderer.py manually before using /process-notes.

### Create CLAUDE.md at project root
Copy [repo-root]/project-template/CLAUDE.md to PROJECT_PATH/CLAUDE.md.

### Create Claude launcher
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

### DOCX renderer entries in CLAUDE.md

In addition to the standard replacements, fill in the four DOCX renderer keys:
- `[PROJECT]_blank_template.docx` → BLANK_TEMPLATE_PATH (or leave with warning comment if not set)
- `DOCX renderer scripts` → `MEETING_NOTES_FOLDER/skills/docx-renderer/scripts/`
- `DOCX working dir` → `MEETING_NOTES_FOLDER/working/`
- `DOCX renderer skill` → `MEETING_NOTES_FOLDER/skills/docx-renderer/SKILL.md`

### Formatter skill file
Open meeting-notes-formatter-skill-PROJECT_NAME.md.
Replace [PROJECT NAME] in the heading with PROJECT_NAME.

For each section of the Established Style Profile:
- If EXTRACTED_DATA has HIGH or MEDIUM confidence: replace [TO BE FILLED IN] with extracted
  content written as specific, actionable rules. Style conventions only — no actual content
  (names, dates, decisions) from the uploaded notes.
- If EXTRACTED_DATA is empty or LOW confidence: leave [TO BE FILLED IN] but replace the
  comment block with a targeted prompt noting what to fill in.

### Style rules and hard rules skill files
Apply the same logic — populate where EXTRACTED_DATA is HIGH/MEDIUM, leave targeted
prompts elsewhere.

The hard rules terminology reference: if technical terms were extracted from uploaded
notes, add them under the appropriate category.

---

## Step 5 — Print confirmation

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
  └── skills/            ← your style, hard rules, and docx renderer

Launcher created:
  PROJECT_PATH/Claude — PROJECT_NAME Meeting Notes Launcher.command
  └── Double-click this in Finder to open Claude Code in the right folder

[If BLANK_TEMPLATE_PATH is set:]
DOCX blank template created:
  BLANK_TEMPLATE_PATH
  └── Headers, footers, and branding preserved from your uploaded file

[If BLANK_TEMPLATE_PATH is empty:]
⚠ DOCX blank template not created — create it before running /process-notes:
  python MEETING_NOTES_FOLDER/skills/docx-renderer/scripts/create_blank_template.py <source.docx> MEETING_NOTES_FOLDER/PROJECT_NAME_blank_template.docx

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
