# Process meeting notes

## Before starting
Load CLAUDE.md — project roster, org names, and file locations.

## Pipeline — 4 stages in strict order, no skipping

### Stage 1 — formatter
Find the most recent file in transcripts/ (newest by filename date or modification date).

Files to pass to the formatter agent:
- CLAUDE.md
- The formatter skill file listed in CLAUDE.md under "Key file locations"
- skills/style-rules/SKILL.md
- skills/style-rules/references/structure.md
- skills/style-rules/references/typography.md
- skills/hard-rules/SKILL.md
- skills/hard-rules/references/terminology.md

Receive complete first draft.

### Stage 2 — editorial-qa
Files to pass to the editorial-qa agent:
- Stage 1 draft
- skills/style-rules/SKILL.md

Receive sharpened draft plus EDITORIAL NOTE.

### Stage 3 — discipline-checker
Files to pass to the discipline-checker agent:
- Stage 2 draft
- CLAUDE.md
- skills/hard-rules/SKILL.md
- skills/hard-rules/references/terminology.md

Receive corrected draft plus DISCIPLINE NOTE.

### Stage 4 — supervisor-alignment
Files to pass to the supervisor-alignment agent:
- Stage 3 draft
- The supervisor style guide file listed in CLAUDE.md under "Key file locations"

Agent self-checks the style guide entry count and either applies preferences or reports
the guide is still being built.
Receive final draft.

## Output
Save final draft as:
output/meeting-notes-YYYY-MM-DD.docx

## Summary report — print after saving
- Which transcript was processed and its date
- EDITORIAL NOTE from Stage 2
- DISCIPLINE NOTE from Stage 3
- Whether Stage 4 applied corrections or passed through
