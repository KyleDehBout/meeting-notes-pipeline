---
name: rendering-meeting-notes-docx
description: Renders polished meeting notes markdown into a properly formatted [PROJECT NAME]-template Word document (.docx). Use when the supervisor-alignment agent has completed its pass and a .docx output file is required. Handles the template-clone approach, XML body replacement, header/footer preservation, and validation. Do not use for content editing — rendering only.
---

# Meeting Notes DOCX Renderer

Converts finalised meeting notes markdown into a `.docx` file that exactly matches the project branded template. This agent renders only — content decisions belong to earlier pipeline stages.

## Workflow

Copy this checklist into your response and check off each step as you complete it:

```
Render Progress:
- [ ] Step 1: Clone the blank template
- [ ] Step 2: Unpack
- [ ] Step 3: Generate body XML
- [ ] Step 4: Replace document body
- [ ] Step 5: Repack
- [ ] Step 6: Validate
- [ ] Step 7: Save to output/
```

---

## Step 1: Clone the blank template

Read `DOCX blank template` and `DOCX working dir` from CLAUDE.md.

**Always clean the working directory first — even on a restart:**

```bash
rm -rf "[DOCX working dir]"
mkdir -p "[DOCX working dir]"
cp "[DOCX blank template]" "[DOCX working dir]/meeting-notes-working.docx"
```

**Why clone?** The template contains image-based headers and footers embedded as XML relationships. These cannot be regenerated — they must be preserved from the original file.

---

## Step 2: Unpack

Read `DOCX renderer scripts` from CLAUDE.md for the scripts directory path.

```bash
python3 "[DOCX renderer scripts]/unpack.py" \
  "[DOCX working dir]/meeting-notes-working.docx" \
  "[DOCX working dir]/unpacked/"
```

Do NOT touch these files after unpacking:
- `word/header1.xml`, `word/header2.xml`
- `word/footer1.xml`, `word/footer2.xml`
- `word/media/` (all image files)
- `word/_rels/` (all relationship files)
- `word/numbering.xml`

---

## Step 3: Generate body XML

**NEVER print XML in your response.** Write all XML directly to disk using a Python script. Your response for this step must be one line: `Step 3: body XML written to [path]`.

Read the reference files silently to understand the XML patterns, then write and run a Python script that generates the complete body XML and saves it to `[DOCX working dir]/body.xml`. Do not print the script or any XML in your response.

For XML patterns, read silently:
- **[references/title-and-attendees.md](references/title-and-attendees.md)** — Title block and attendees section
- **[references/table-structure.md](references/table-structure.md)** — Main table, all row types
- **[references/footer-and-special.md](references/footer-and-special.md)** — Footer paragraph, superscripts, special chars

These three files were rendered once, during `/setup-pipeline`, from this project's own
branded .docx. They are project-owned: read them, never rewrite them. Nothing in the render
workflow regenerates them, and the user may have edited them by hand since setup. If a value
in them looks wrong, say so and stop — do not correct it yourself.

Document structure (top to bottom):

```
[Empty paragraph]
[Title block — 4 centred bold paragraphs: project name, "Held on", date, time]
[Empty paragraph]
[Empty paragraph]
[Attendees: label]
[Attendee rows — tab-separated]
[Empty paragraph]
[Empty paragraph]
[Main table]
  [Header row]
  [Content rows — ONE PER SECTION: each row holds that section's title,
   its subsection labels and all its sub-items as paragraphs in col 2.
   Never one row per sub-item — see references/table-structure.md]
  [Meetings row — final row, next meeting date]
[Footer paragraph — "Prepared by: [Organisation] Limited"]
[sectPr — copy exactly from template, do not recalculate]
```

---

## Step 4: Replace document body

Use a Python script to replace the body of `[DOCX working dir]/unpacked/word/document.xml` with the content of `[DOCX working dir]/body.xml`. Do not print the script or any XML in your response — just run it and confirm success in one line.

Replace only the content between `<w:body>` and `</w:body>`. Do not alter the root `<w:document>` element or its namespace declarations.

**CRITICAL rules:**
- Escape all ampersands: `&` → `&amp;`
- Add `xml:space="preserve"` to any `<w:t>` with leading or trailing spaces
- Do not define new numbering — `numbering.xml` already contains the list styles; reference them as-is
- Copy the `<w:sectPr>` block verbatim from the unpacked template XML
- **Never type a section/sub-item number into `<w:t>` text.** Numbering is rendered by
  Word from `numPr` (`ilvl` + a live `numId`) — writing "1.", "1.1" or "1.1.1" as literal
  characters means the `numPr` wiring is wrong. Fix the wiring, not the text.
- **`numId="0"` at `ilvl="0"` on a section title is correct and deliberate.** It suppresses
  that paragraph's own number so the col 1 counter supplies it. It is the one place
  `numId="0"` belongs; omitting `<w:numPr>` altogether there is the bug. See
  [references/table-structure.md](references/table-structure.md) for the exact pattern.

---

## Step 5: Repack

```bash
python3 "[DOCX renderer scripts]/repack.py" \
  "[DOCX working dir]/unpacked/" \
  "[DOCX working dir]/meeting-notes-final.docx"
```

---

## Step 6: Validate

```bash
python3 "[DOCX renderer scripts]/validate.py" \
  "[DOCX working dir]/meeting-notes-final.docx"
```

**If validation fails, attempt the automatic repair before touching the XML yourself.**
`repair.py` fixes the known renderer failure modes mechanically — a typed-in section
number that duplicates the one Word supplies, and numbering that was never linked to a
live list. It repairs nothing it cannot fix safely, backs the file up to
`.pre-repair.docx`, appends every run to the render log, and re-runs `validate.py`
itself, so its exit code means the document is genuinely valid.

```bash
python3 "[DOCX renderer scripts]/repair.py" \
  "[DOCX working dir]/meeting-notes-final.docx" \
  --log "[DOCX working dir]/render-log.tsv"
```

Exit code 0 means validation now passes — continue to Step 7. Exit 1 means still
invalid. Exit 2 means the file could not be read at all.

Do not add `--restyle` unless the validation failure is specifically about chat-UI
paragraph styles. It remaps every `font-claude-*` / `claude-*` style in the document,
and a document can carry those legitimately — running it by reflex silently changes
formatting nobody asked to change.

Report the repair output as one line. Repair prints at most 5 fixes; the full list goes
to the log file, so never paste the log into your response.

**If validation still fails after the repair:**
1. Read the error message carefully
2. Return to Step 4 and fix the XML (via Python script — do not print XML in response)
3. Repack (Step 5)
4. Validate again
5. **Maximum 3 validation attempts total.** If validation has not passed after 3 attempts, stop and report: `RENDER FAILED: validation error after 3 attempts — [error message]`. Do not continue looping.

---

## Step 7: Save to output/

Read the output folder path from CLAUDE.md. Extract the meeting date from the markdown title block.

```bash
cp "[DOCX working dir]/meeting-notes-final.docx" \
   "[output folder]/[PROJECT NAME]-Meeting-Notes-YYYY-MM-DD.docx"
```

Return: `RENDER COMPLETE: [output path]`

---

## Hard rules

| Rule | Detail |
|------|--------|
| **No inline XML in responses** | Never print XML blocks in response text — always write to disk via script. One-line confirmation only. |
| **No inline scripts in responses** | Write Python scripts to a temp file and run them — do not print the script body in your response. |
| **Validation cap** | Maximum 3 validation attempts — fail and report after that, do not loop further. |
| **Clean working dir on start** | Always rm -rf the working dir before Step 1, even on a restart. |
| No npm `docx` library | Template-clone + XML edit only |
| Action column | Company/team names only — never individual person names |
| Status values | `In Progress`, `Pending`, `No Action` — no other values permitted |
| `numbering.xml` | Copy unchanged from template — never redefine list styles |
| Validation | Must pass before saving output |
| Content | Do not alter content — rendering only |

---

## Reference files

| File | When to read |
|------|--------------|
| [references/title-and-attendees.md](references/title-and-attendees.md) | Building the title block or attendees section |
| [references/table-structure.md](references/table-structure.md) | Building any part of the main table |
| [references/footer-and-special.md](references/footer-and-special.md) | Footer paragraph, superscript dates, special characters |
