# Project status — meeting notes pipeline

## What this does
Prints a snapshot of the current project state: what is in each folder, how complete
the style guide is, and what to do next.

## Before starting
Load CLAUDE.md to get the project name, file locations, and supervisor activation threshold.

## Check each area

### Folders
Check each folder and note the file count and most recent filename:
- transcripts/
- output/
- intake/
- Meeting Notes/

### Style guide health
Load the supervisor style guide listed in CLAUDE.md.
Count non-comment, non-blank entries in each section:
- Wording preferences
- Structural preferences
- Scope preferences
- Recurring corrections
- Promoted rules

Read the activation threshold from CLAUDE.md (key: "Supervisor activation threshold", default 3).
Determine whether recurring corrections are active (count >= threshold).

### Skill file completeness
Check each of the following files for any remaining `[TO BE FILLED IN]` text:
- The formatter skill file listed in CLAUDE.md
- skills/style-rules/SKILL.md
- skills/style-rules/references/structure.md
- skills/style-rules/references/typography.md
- skills/hard-rules/references/terminology.md

### Suggested next action
Determine one clear next step:
- If any skill file has `[TO BE FILLED IN]`: "Complete your style profile before running /process-notes — see files listed above"
- Else if transcripts/ is empty: "Drop a transcript in transcripts/ and run /process-notes"
- Else if output/ is empty: "Run /process-notes to generate your first draft"
- Else if intake/ is empty: "Review the draft in output/, get supervisor approval, drop the final version in intake/ and run /learn"
- Else if intake/ has files: "Run /learn to compare the pipeline draft against your supervisor's version"

## Output
Print exactly this structure:

---
[PROJECT NAME] — Pipeline status

FOLDERS
  transcripts/     [N files | empty] [most recent: filename]
  output/          [N files | empty] [most recent: filename]
  intake/          [N files | empty]
  Meeting Notes/   [N archived | none yet] [most recent: filename]

SUPERVISOR STYLE GUIDE
  Wording preferences:    N
  Structural preferences: N
  Scope preferences:      N
  Recurring corrections:  N / THRESHOLD  [active | not yet active]
  Promoted rules:         N

SKILL FILES
  [✓ Complete | ⚠ Placeholders remain] — [filename]
  (one line per file checked)

NEXT
  [single recommended action]
---

Do not ask follow-up questions. Print the report and stop.
