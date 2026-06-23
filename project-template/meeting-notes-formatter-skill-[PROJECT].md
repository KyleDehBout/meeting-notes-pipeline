---
name: meeting-notes-formatter
description: >
  Format raw meeting transcripts into polished professional meeting notes matching
  the established style for this project. Use this skill whenever a raw transcript
  or rough notes need to be reformatted into the official document style.
  Trigger on any mention of: "meeting notes", "format these notes", "process transcript",
  "reformat", or any time raw meeting content is provided for formatting.
  CRITICAL: Never carry over any content, facts, names, dates, action items, or
  decisions from one set of notes to another. Each session is isolated.
---

# Meeting Notes Formatter — [PROJECT NAME]

## Core Purpose
Transform raw transcripts or rough notes into polished professional meeting notes
matching the established document style for this project.

**This skill operates in two distinct phases. Always identify which phase applies before proceeding.**

---

## ABSOLUTE DATA ISOLATION RULES

These rules are non-negotiable and override everything else:

1. **No content carryover.** Facts, names, dates, decisions, action items, or any specific
   information from one set of notes MUST NEVER appear in another.
2. **Style is the only transferable element.** The Style Profile below defines tone, vocabulary,
   structure, and formatting — it never carries content.
3. **Never assume.** If information is missing from the raw notes being formatted, leave it
   blank or mark `[not provided]`. Do not fill gaps from memory, prior uploads, or inference.
4. **Each upload is a clean slate.** Treat every new transcript as if it is the first document
   you have ever seen from this project.
5. **When in doubt, omit.** If you are uncertain whether something came from the current upload
   or a previous one, do not include it.

---

## Phase 1: Style Analysis (Learning Mode)

**Trigger:** User uploads one or more past/completed meeting notes for style learning.

Analyze uploaded documents and extract a Style Profile covering ONLY: tone, sentence structure,
vocabulary register, formatting patterns, abbreviation conventions, and section organisation.
Do not summarise, reproduce, or reference any actual content from the samples.

Present the Style Profile to the user for confirmation before proceeding to any formatting work.

---

## Established Style Profile

<!-- 
SETUP INSTRUCTIONS: Fill in this section based on your organisation's existing meeting notes.
The more specific you are here, the better the pipeline output. Use past issued notes as reference.

Replace each section below with your actual conventions. Delete these instruction comments
once the profile is complete.
-->

### 1. Tone & Register
<!--
Define the tone of your meeting notes. Examples to consider:
- Formal / semi-formal / informal
- First person / third person / organisation-driven
- Outcome-focused vs. discussion-focused
- Any specific preferred constructions (e.g. "[Org] to provide..." vs "[Org] will provide...")
- Whether speaker attribution is used or avoided
-->
[TO BE FILLED IN — describe the tone and register of your meeting notes]

### 2. Action & Status Columns
<!--
Define how the Action and Status columns work in your notes table. Examples:
- What goes in the Action column (org name, individual name, initials?)
- How two parties sharing an action are shown (e.g. "Org A / Org B")
- What status values are used and what they mean
-->
[TO BE FILLED IN — define Action and Status column conventions]

### 3. Document Structure
<!--
Define the strict section order of your meeting notes. Example:
1. Header block (project name, date, time, meeting number)
2. Attendees list
3. Main items table (numbered sections and subsections)
4. Next meeting / closing
5. Prepared by line

Include any rules about column layout, numbering format, heading styles.
-->
[TO BE FILLED IN — define the document structure in strict order]

### 4. Typographic Conventions
<!--
Define formatting specifics. Examples:
- Date format (e.g. "Thursday April 9, 2026" vs "09/04/2026")
- Which elements are bold, italic, or plain
- Column alignment (centred, left-aligned)
- Whether bullets are used within cells
- Company branding in the prepared-by line
-->
[TO BE FILLED IN — define typographic and formatting conventions]

### 5. Scope & Content Discipline
<!--
Define what gets included and excluded. Examples:
- Only items with a decision or action — omit pure discussion
- Consolidate multiple exchanges into single outcome points
- How to handle missing information (mark as [not provided], omit, etc.)
- Whether a standalone Action Items section exists or all actions are inline
-->
[TO BE FILLED IN — define scope and content rules]

---

## Phase 2: Note Generation (Formatting Mode)

**Trigger:** User provides raw transcript, notes, or document for formatting.

### Step-by-Step Process

1. **Read the raw notes completely** before writing a single word of output.
2. **Extract organisation names from the Attendees list** in the transcript — these are the
   only names used in the Action column throughout the document.
3. **Apply the Style Profile above** exactly.
4. **Format, never fabricate** — only include content from the raw source.
5. **Exercise scope discipline** — include only items with a decision, action, or informational
   value. Omit conversational filler.
6. **Default output is a Word (.docx) file** unless the user requests otherwise.

---

## What NOT To Do

- Never use content from any previous meeting notes
- Never add agenda items, context, or background not in the raw source
- Never correct or second-guess technical information — transcribe as given
- Never add summaries, overviews, or closing remarks
- Never use individual names in the Action column unless your style profile explicitly calls for it
- Never carry forward anything from a previous formatting session
