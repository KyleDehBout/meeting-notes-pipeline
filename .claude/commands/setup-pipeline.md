# Setup Meeting Notes Pipeline

## What this does
Installs the global pipeline components into your Claude Code configuration and scaffolds
a new project folder ready to use.

## Step 1 — Collect project information
Ask the user the following questions one at a time. Wait for each answer before continuing.

1. "What is your project name or code? Use a short identifier — this becomes the suffix on your project files. (e.g. SFV, BRIDGE-02, RETAIL-Q4)"
   Save as PROJECT_NAME.

2. "Where should the project folder be created? Provide the full path. The folder will be created if it does not exist."
   Save as PROJECT_PATH.

3. "List your team members. For each person enter: Name, Organisation, Title — one per line. Type DONE on its own line when finished."
   Collect as a list of ROSTER entries.

4. "List all organisation names that will appear in the Action column of your meeting notes, comma-separated. These must be exact — they are used for attribution validation."
   Save as ORG_NAMES.

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

## Step 3 — Scaffold project folder

Create the following folder structure at PROJECT_PATH (create parent directories as needed):
- transcripts/
- output/
- intake/
- Meeting Notes/
- skills/style-rules/references/
- skills/hard-rules/references/
- .claude/

Copy all files from [repo-root]/project-template/ into PROJECT_PATH.
When copying, rename files as follows — replace the literal string [PROJECT] with PROJECT_NAME:
- supervisor-style-guide-[PROJECT].md → supervisor-style-guide-PROJECT_NAME.md
- pipeline-memory-[PROJECT].md → pipeline-memory-PROJECT_NAME.md
- meeting-notes-formatter-skill-[PROJECT].md → meeting-notes-formatter-skill-PROJECT_NAME.md

Copy subdirectory contents (skills/) preserving folder structure.
Do not copy .gitkeep files.

## Step 4 — Populate CLAUDE.md

Open the newly created CLAUDE.md at PROJECT_PATH and make the following replacements:
- [PROJECT NAME] → PROJECT_NAME (appears in the heading and project name field)
- [FULL PATH TO PROJECT FOLDER] → PROJECT_PATH
- Every occurrence of [PROJECT] in file location values → PROJECT_NAME
- The placeholder roster row → one table row per ROSTER entry, formatted as: | Name | Organisation | Title |
- [Org1, Org2, Org3...] → ORG_NAMES (comma-separated, exactly as the user provided)

## Step 5 — Print confirmation

Print exactly this (substituting real values):

---
Pipeline installed.

Global files added to:
  ~/.claude/commands/
  ~/.claude/agents/

Project scaffolded at:
  PROJECT_PATH

Next steps:
1. Open PROJECT_PATH in Claude Code
2. Fill in your style profile:
   meeting-notes-formatter-skill-PROJECT_NAME.md
3. Add your formatting rules to:
   skills/style-rules/ and skills/hard-rules/
4. Drop a transcript in transcripts/ and run /process-notes

The supervisor-alignment stage passes the draft through unchanged until
5 corrections are logged in supervisor-style-guide-PROJECT_NAME.md.
That file fills in automatically as you run /learn cycles.
---

Do not ask follow-up questions. The setup is complete.
