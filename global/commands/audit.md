# Audit pipeline learning — meeting notes pipeline

## What this does
Summarises everything the pipeline has learned, rejected, and promoted across all
/learn cycles for the current project.

## Before starting
Load CLAUDE.md to get the project name and file locations.
Load the pipeline memory file listed in CLAUDE.md under "Key file locations".

## What to read and count

### From the pipeline memory file
- Count total /learn run entries (each entry is separated by a date header)
- Count approved changes, grouped by category:
  WORDING, FORMAT, STRUCTURE, ATTRIBUTION, STATUS, SCOPE, TERMINOLOGY, SUPERVISOR-PREF, HARD-RULE
- Count rejected changes (lines marked REJECTED) — list each with its reason text
- Count deferred items (lines marked as deferred or NO ANSWER)
- List any items marked [PROMOTED]

### From skill files
Note which of the following files have real content beyond template placeholders
(i.e. have entries that are not `[TO BE FILLED IN]` or template comment blocks):
- skills/style-rules/SKILL.md
- skills/style-rules/references/structure.md
- skills/style-rules/references/typography.md
- skills/hard-rules/references/terminology.md
- The supervisor style guide listed in CLAUDE.md

## Output
Print exactly this structure:

---
[PROJECT NAME] — Pipeline audit

LEARN CYCLES
  Total runs: N

APPROVED CHANGES BY CATEGORY
  WORDING:          N
  FORMAT:           N
  STRUCTURE:        N
  ATTRIBUTION:      N
  STATUS:           N
  SCOPE:            N
  TERMINOLOGY:      N
  SUPERVISOR-PREF:  N
  HARD-RULE:        N
  ─────────────────
  Total approved:   N

REJECTED CHANGES  (N total)
  [list each: "REJECTED [DATE]: [rule text] — [reason]"]
  [or "none" if empty]

DEFERRED  (N total)
  [or "none"]

PROMOTED TO PERMANENT
  [list each promoted rule]
  [or "none yet — rules promote after 3 confirmed repetitions"]

SKILL FILES WITH CONTENT
  [✓ has content] — filename
  [⬜ still template defaults] — filename
  (one line per file)
---

Do not ask follow-up questions. Print the report and stop.
