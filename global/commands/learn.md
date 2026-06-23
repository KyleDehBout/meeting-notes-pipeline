# Learn from final issued notes

## Purpose
Compare what the pipeline produced against the final supervisor-approved version.
Extract every difference. Propose targeted improvements to skill files and agents.
Move the final file to Meeting Notes/ with correct numbering.

## Before starting — verify intake
Check intake/ for a file.
If empty: stop and tell the user "No file found in intake/ — drop your final issued
.docx or .pdf there and run /learn again."
If a file exists: proceed.

## Files to load
- intake/ — the final supervisor-approved version (source of truth)
- output/ — find the matching pipeline draft (match by closest date to the intake file)
- The pipeline memory file listed in CLAUDE.md under "Key file locations" — running learning log
- skills/style-rules/SKILL.md — may receive updates
- skills/hard-rules/SKILL.md — may receive updates
- The supervisor style guide file listed in CLAUDE.md under "Key file locations" — may receive updates
- /Users/kylefreeman/.claude/agents/ — agent descriptions may receive updates

## Hand off to learning-reviewer agent
Pass it both documents and all context files above.
The agent generates the browser review form and waits.

## After user pastes the review block
/apply-learning handles all writes automatically when the user pastes the ==LEARNING_REVIEW== block.
