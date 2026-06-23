# Setup Meeting Notes Pipeline

## What this does
Installs the global pipeline components into your Claude Code configuration and scaffolds
a new project folder ready to use. If you provide past meeting notes, the setup extracts
your style, roster, and organisation names automatically.

---

## Step 0 — Optional: Upload past notes

Before asking any questions, prompt the user with exactly this:

---
Before we set up your project, do you have any past meeting notes you've already
produced and are happy with? If so, upload one or two now — I'll extract your style,
roster, and organisation names automatically and use them to pre-fill your project files.

You can upload a .docx, .pdf, or paste the content directly.
If you don't have any, just say "skip" and I'll ask you for the details manually.
---

Wait for the user to respond.

### If the user uploads or pastes past notes:

Read every uploaded document fully before proceeding. Extract the following silently
— do not print the analysis, just hold it for use in later steps:

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

### If the user says "skip":
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
- skills/style-rules/references/
- skills/hard-rules/references/

### Copy template files
Copy all files from [repo-root]/project-template/Meeting Notes/ into
PROJECT_PATH/MEETING_NOTES_FOLDER/, with these renames — replace the literal string
[PROJECT] with PROJECT_NAME:
- supervisor-style-guide-[PROJECT].md → supervisor-style-guide-PROJECT_NAME.md
- pipeline-memory-[PROJECT].md → pipeline-memory-PROJECT_NAME.md
- meeting-notes-formatter-skill-[PROJECT].md → meeting-notes-formatter-skill-PROJECT_NAME.md

Copy skills/ subdirectory contents preserving folder structure.
Do not copy .gitkeep files.

### Create CLAUDE.md at project root
Copy [repo-root]/project-template/CLAUDE.md to PROJECT_PATH/CLAUDE.md.

### Create Claude launcher
Create a file at PROJECT_PATH named exactly:
  Claude Launcher — PROJECT_NAME.command

Write the following content into it:
```
#!/bin/bash
cd "$(dirname "$0")"
claude
```

Make it executable:
  chmod +x "PROJECT_PATH/Claude Launcher — PROJECT_NAME.command"

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
  └── skills/            ← your style and hard rules

Launcher created:
  PROJECT_PATH/Claude Launcher — PROJECT_NAME.command
  └── Double-click this in Finder to open Claude Code in the right folder

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
