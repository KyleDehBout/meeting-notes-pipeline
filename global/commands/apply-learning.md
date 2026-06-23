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

## Step 2 — Process Section 1: Proposed changes
For each line marked [APPROVE]:
- Write the proposed rule to the exact target file specified
- Do it silently — no confirmation needed, user already approved in the form

For each line marked [REJECT]:
- Append to the pipeline memory file listed in CLAUDE.md under a new run entry:
  REJECTED [DATE]: [rule text] — not applied

For each line marked [NO ANSWER]:
- Skip it, log to the pipeline memory file listed in CLAUDE.md as deferred

## Step 3 — Process Section 2: Style Q&A
For each Q&A pair where an answer is not "(no answer)":
- Read the question and the answer
- Derive the most specific rule possible from the answer
- Determine the correct target file:
  - Wording or tone preference → the supervisor style guide file listed in CLAUDE.md → Wording preferences
  - Formatting detail → skills/style-rules/references/typography.md
  - Section ordering or layout → skills/style-rules/references/structure.md
  - General style principle → skills/style-rules/SKILL.md
  - Absolute rule → skills/hard-rules/SKILL.md
  - Technical term → skills/hard-rules/references/terminology.md
- Write the derived rule directly to that file — no confirmation needed
- The rule must be a single actionable sentence, not a summary of the answer

For each Q&A pair where the answer is "(no answer)":
- Skip silently

## Step 4 — Process Section 3: Project context
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
- Add each term to the correct category in skills/hard-rules/references/terminology.md
- Infer the category from the term
- If category is unclear, add under a new "Other" section
- Write directly

Other:
- Determine the correct file from context
- Write directly

## Step 5 — Move the final file
Check intake/ for the issued file.
Find the highest numbered file in Meeting Notes/.
Increment by 1.
Move intake file to Meeting Notes/ as: [Project Name] - Meeting Notes #[N].[original extension]
Clear intake/ folder.
Delete qa-session.html from the project root if it exists.

## Step 6 — Print summary and stop
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
---

Do not ask follow-up questions. Do not offer next steps.
The workflow is complete.
