# apply-learning

## Trigger
This command runs automatically when the user pastes a block beginning with
==LEARNING_REVIEW== into the terminal. The user does not need to type
/apply-learning manually — detecting the paste marker is enough to begin.

## Step 1 — Validate the block
Check the pasted content starts with ==LEARNING_REVIEW== and ends with ==END_REVIEW==.
If malformed or incomplete: stop and say "Paste looks incomplete — copy again from the
browser form and paste the full block."
If valid: proceed silently. Do not echo the block back.

## Step 2 — Load CLAUDE.md
Read CLAUDE.md to get all file paths before writing anything.

## Step 3 — Process Section 1: Proposed changes
For each line marked [APPROVE]:
- Write the proposed rule to the exact target file specified
- Do it silently — no confirmation needed, user already approved in the form

For each line marked [REJECT]:
- Append to the pipeline memory file listed in CLAUDE.md under a new run entry:
  REJECTED [DATE]: [rule text] — not applied

For each line marked [NO ANSWER]:
- Skip it, log to the pipeline memory file listed in CLAUDE.md as deferred

## Step 4 — Process Section 2: Style Q&A
For each Q&A pair where an answer is not "(no answer)":
- Read the question and the answer
- Derive the most specific rule possible from the answer
- Determine the correct target file using the paths from CLAUDE.md:
  - Wording or tone preference → the supervisor style guide file listed in CLAUDE.md → Wording preferences
  - Formatting detail → the style rules skill references/typography.md (derived from the style rules skill path in CLAUDE.md)
  - Section ordering or layout → the style rules skill references/structure.md
  - General style principle → the style rules skill file listed in CLAUDE.md
  - Absolute rule → the hard rules skill file listed in CLAUDE.md
  - Technical term → the hard rules skill references/terminology.md
- Write the derived rule directly to that file — no confirmation needed
- The rule must be a single actionable sentence, not a summary of the answer

For each Q&A pair where the answer is "(no answer)":
- Skip silently

## Step 5 — Process Section 3: Project context
Work through each field. For any field that is not "none":

New members:
- Parse name, organisation, title from the value
- Add a new row to the project roster table in CLAUDE.md
- Write directly — no confirmation needed

Departed:
- Find the matching row in CLAUDE.md project roster
- Remove or annotate as departed with the date
- Write directly

New orgs:
- Add to the organisation names list in CLAUDE.md
- Write directly

Scope changes:
- Append a note to CLAUDE.md under a "Scope notes" section (create if not exists)
- Write directly

New terms:
- Add each term to the hard rules references/terminology.md (derived from the hard rules skill path in CLAUDE.md)
- Infer the category from the term
- If category is unclear, add under a new "Other" section
- Write directly

Other:
- Determine the correct file from context
- Write directly

## Step 6 — Move the final file
Read the "Issued archive" path from CLAUDE.md.
Check the intake folder (listed in CLAUDE.md) for the issued file.
Read the existing filenames in the issued archive and follow the naming convention already
in use there rather than assuming one. Find the highest number, increment by 1, and move
the intake file to the archive under that name.

Do NOT delete anything in this step — Step 7 clears every folder at once, and only after
it has verified the archived file is really there.

## Step 7 — Clean up pipeline folders
Run the cleanup script, passing the exact filename you just archived:

```bash
bash "[MEETING_NOTES_FOLDER]/skills/pipeline-cleanup/cleanup-cycle.sh" "[archived filename]"
```

Add `--archive "[Issued archive path from CLAUDE.md]"` if the archive is not the default
`Archive/` folder beside the pipeline.

The script clears intake/, output/ and transcripts/ and deletes qa-session.html from the
project root, leaving the folders themselves in place. It refuses to delete anything unless
the named file is already present and non-empty in the archive, so the archive-confirmed
precondition is enforced by the script rather than by judgement. Never hand-roll `rm`
commands for this step, and never pass a filename you have not just verified in the archive.

Exit codes: 0 = cleared, 1 = archive not confirmed and nothing was deleted, 2 = bad usage.
If the script exits non-zero, nothing was deleted: report the error and stop.
If it is blocked by a permission prompt, say so plainly in the summary rather than
attempting the deletions another way.

Use `--dry-run` first if you want to show the user what will go before it goes.

This leaves each cycle's only surviving copy as the numbered file in the issued archive.

## Step 8 — Print summary and stop
Print this and nothing else:

---
Done.

Changes applied: [N]
Rules derived from Q&A: [N]
Project context updates: [N]

Files updated:
[list only files that were actually written to, one per line]

Archived to:
[Project Name] - Meeting Notes #[N].[ext]

Cleaned up:
intake/, output/ and transcripts/ cleared
---

Do not ask follow-up questions. Do not offer next steps.
The workflow is complete.
