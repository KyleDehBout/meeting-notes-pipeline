# Supervisor style guide — [PROJECT NAME]

## Purpose
This file records every correction your supervisor makes to issued meeting notes.
It is read by the supervisor-alignment agent on every /process-notes run and updated
automatically by the learning-reviewer agent after every /learn cycle.

The supervisor-alignment stage is inactive until 5 or more corrections are logged under
"Recurring corrections". You can seed this file manually with known preferences, or leave
it blank and let it fill in through /learn cycles.

## Wording preferences
<!-- Add known wording preferences here. Example:
- Say "contractor to provide" not "contractor will provide"
- Say "outstanding" not "pending" for incomplete items
-->

## Structural preferences
<!-- Add known structural preferences here. Example:
- Decisions section always appears before Action Items
- Action items must include a deadline, even if approximate
-->

## Scope preferences
<!-- Add known scope preferences here. Example:
- Remove scheduling items unless a date was formally confirmed
- Do not include items where no decision or action was taken
-->

## Recurring corrections
<!--
Written to automatically by /learn after each approved revision cycle.
Do not edit manually unless adding a one-off correction you want captured immediately.

Format for each entry:
- [DATE] Changed "[pipeline wording]" to "[final wording]" — [category: WORDING / STRUCTURE / SCOPE / TERMINOLOGY]
-->

## Promoted rules (appeared 3+ times — now permanent)
<!--
Rules that started in Recurring corrections and have been seen enough times
to be treated as hard preferences. /learn moves them here automatically.
-->
