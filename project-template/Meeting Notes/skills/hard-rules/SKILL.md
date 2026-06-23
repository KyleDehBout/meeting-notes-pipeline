---
name: hard-rules
description: >
  Absolute rules that must never be violated at any stage of the meeting notes pipeline.
  Covers data isolation between sessions, attribution rules, speaker attribution prohibition,
  content discipline, and output format. Load references/terminology.md when processing
  any item involving technical or industry-specific terms.
compatibility: Designed for use with the meeting-notes-pipeline
metadata:
  version: "1.0"
allowed-tools: Read
---

## Data isolation — non-negotiable
- NEVER carry over any content, names, dates, decisions, or action items from a previous session
- Each transcript is a clean slate — treat it as the first document ever seen
- If information is missing from the current transcript, mark as `[not provided]` or omit
- Never fill gaps using memory, inference, or prior uploads
- When in doubt, omit

## Attribution — non-negotiable
- NEVER use individual names or initials in the Action column
- ONLY use organisation names sourced from the Attendees list in the current transcript
- NEVER use organisation names from memory, prior sessions, or this skill file

## Speaker attribution — non-negotiable
- NEVER write "he said", "she said", "[Name] said", or any variant
- NEVER attribute outcomes to speakers
- Report decisions and actions in neutral third-person only

## Content discipline — non-negotiable
- NEVER add summaries, overviews, or closing remarks not in the source transcript
- NEVER correct or second-guess technical information — transcribe as given
- NEVER add agenda items, context, or background not in the raw source
- NEVER invent or infer anything not explicitly in the transcript

## Output format — non-negotiable
- Default output is always a .docx file
- Never produce plain text output unless explicitly requested by the user

## Technical terms
See [terminology reference](references/terminology.md) for project-specific terms that
must be preserved exactly as written.
