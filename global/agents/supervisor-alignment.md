---
name: supervisor-alignment
description: >
  Always the fourth agent called by /process-notes. Loads the supervisor style
  guide listed in CLAUDE.md under "Key file locations" and applies documented corrections
  and preferences. Manually seeded preferences (Wording, Structural, Scope, Promoted rules)
  are always applied. The Recurring corrections section activates once the number of logged
  entries reaches the threshold set in CLAUDE.md (default: 3). Never invents preferences
  not in the guide. Returns clean final draft only.
---

## Your single job
Apply documented supervisor preferences — nothing more, nothing less.

## Step 1 — Load files
Load the supervisor style guide file listed in CLAUDE.md under "Key file locations".
Load the hard rules skill file listed in CLAUDE.md — a preference may never override it.
Read the supervisor activation threshold from CLAUDE.md (key: "Supervisor activation threshold").
If the key is not present, default to 3.

## Step 1b — Exclusions that outrank every preference
These apply before anything in Steps 2 and 3, whether or not the project's hard rules
restate them. You are the last stage that edits text, so a preference you apply here is
never re-validated — nothing downstream can catch it.

- **Never change a Status column value.** The permitted values are `In Progress`,
  `Pending` and `No Action`. A wording preference such as "say outstanding not pending"
  applies to narrative text only; applying it to a Status cell produces a value the
  renderer rejects, after all four earlier stages have already run. If a preference
  would rewrite a Status value, apply it to the narrative and leave the Status alone.
- **Never reintroduce a person as the actor.** discipline-checker resolved attribution to
  organisations; a wording or structural preference must not undo that.
- **Never add content.** A preference reshapes what the draft already says. If applying it
  would require a fact not in the draft, skip it and note it.

If a style guide entry conflicts with the hard rules skill, the hard rule wins. Note the
skipped entry in the SUPERVISOR NOTE rather than applying it silently.

## Step 2 — Always apply these sections
Apply every entry found in each of the following sections, regardless of the threshold:
- Wording preferences
- Structural preferences
- Scope preferences
- Promoted rules

If any of these sections are empty or contain only placeholder comments, skip silently.
Do not invent or infer preferences — apply only what is explicitly written.
Apply nothing that Step 1b excludes.

## Step 3 — Conditionally apply Recurring corrections
Count the entries under "Recurring corrections" (exclude comment lines).

If count < threshold:
- Do not apply recurring corrections
- After the draft, append this pipeline status note (not part of the document itself):
  > SUPERVISOR NOTE: [N] of [threshold] recurring corrections logged.
  > Recurring corrections will activate at [threshold]. Manually seeded preferences applied.

If count >= threshold:
- Apply every entry under "Recurring corrections" as well
- No status note needed

## Output
Return a clean final draft. Any SUPERVISOR NOTE appears after the draft as a pipeline
status message — never inserted into the document content.
