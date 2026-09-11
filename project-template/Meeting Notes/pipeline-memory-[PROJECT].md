# Pipeline memory log — [PROJECT NAME]

## How this file is used
- Written to by /apply-learning at the end of every /learn cycle
- Read by /audit (counts and reports) and by /learn (prior context)
- /process-notes does NOT read this file — rules must live in the skill files to take effect
- Patterns appearing 2+ times are worth watching; promote at 3

## What gets logged here
- Approved changes (written to skill files — logged for pattern tracking)
- Rejected proposed changes (logged with reason)
- Judgment calls that don't yet have enough repetitions to become rules

## Promotion threshold
When a pattern appears in 3+ separate run entries below, manually promote it
to the appropriate skill file and mark it [PROMOTED] here.

## Entry format
One dated header per cycle, then one line per change. /audit counts run entries by the
date header and approved changes by the CATEGORY tag, so the tags must not be dropped.

```
## 2026-06-18 — site-meeting-14.txt
APPROVED WORDING: Use "site team" not "the guys on site" — applied to skills/style-rules/SKILL.md
DERIVED FORMAT: Dates carry no ordinal suffix — applied to skills/style-rules/references/typography.md
REJECTED 2026-06-18: Merge the Actions column into Content — not applied
DEFERRED 2026-06-18: Shorten section titles to four words — no answer given
```

CATEGORY is one of WORDING, FORMAT, STRUCTURE, ATTRIBUTION, STATUS, SCOPE,
TERMINOLOGY, SUPERVISOR-PREF, HARD-RULE.

---
<!-- Run entries appear below — newest at bottom -->
