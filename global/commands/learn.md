# Learn from final issued notes

## Purpose
Compare what the pipeline produced against the final supervisor-approved version.
Extract every difference. Propose targeted improvements to skill files and agents.
Move the final file to the issued archive with correct numbering.

## Before starting — verify intake
Load CLAUDE.md to get all file paths.
Check the intake folder listed in CLAUDE.md for a file.
If empty: stop and tell the user "No file found in [intake path] — drop your final issued
.docx or .pdf there and run /learn again."
If a file exists: proceed.

## Files to load
- The intake folder listed in CLAUDE.md — the final supervisor-approved version (source of truth)
- The output folder listed in CLAUDE.md — find the matching pipeline draft (match by closest date)
- The pipeline memory file listed in CLAUDE.md — running learning log
- The style rules skill file listed in CLAUDE.md — may receive updates
- The hard rules skill file listed in CLAUDE.md — may receive updates
- The supervisor style guide file listed in CLAUDE.md — may receive updates
- /Users/kylefreeman/.claude/agents/ — agent descriptions may receive updates

## Hand off to learning-reviewer agent
Pass it both documents and all context files above.
The agent generates the browser review form and waits.

## After user pastes the review block
/apply-learning handles all writes automatically when the user pastes the ==LEARNING_REVIEW== block.
