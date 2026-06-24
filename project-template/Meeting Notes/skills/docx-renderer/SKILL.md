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

Read `DOCX blank template` and `DOCX working dir` from CLAUDE.md. Create the working dir if it does not exist.

```bash
cp "[DOCX blank template]" "[DOCX working dir]/meeting-notes-working.docx"
```

**Why clone?** The template contains image-based headers and footers embedded as XML relationships. These cannot be regenerated — they must be preserved from the original file.

---

## Step 2: Unpack

Read `DOCX renderer scripts` from CLAUDE.md for the scripts directory path.

```bash
python "[DOCX renderer scripts]/unpack.py" \
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

Build the replacement `<w:body>` content from the meeting notes markdown.

For full XML patterns, see:
- **[references/title-and-attendees.md](references/title-and-attendees.md)** — Title block and attendees section
- **[references/table-structure.md](references/table-structure.md)** — Main table, all row types
- **[references/footer-and-special.md](references/footer-and-special.md)** — Footer paragraph, superscripts, special chars

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
  [Content rows — one per agenda item]
  [Meetings row — final row, next meeting date]
[Footer paragraph — "Prepared by: [Organisation] Limited"]
[sectPr — copy exactly from template, do not recalculate]
```

---

## Step 4: Replace document body

Edit `[DOCX working dir]/unpacked/word/document.xml`. Replace only the content between `<w:body>` and `</w:body>`. Do not alter the root `<w:document>` element or its namespace declarations.

**CRITICAL rules:**
- Escape all ampersands: `&` → `&amp;`
- Add `xml:space="preserve"` to any `<w:t>` with leading or trailing spaces
- Do not define new numbering — `numbering.xml` already contains the list styles; reference them as-is
- Copy the `<w:sectPr>` block verbatim from the unpacked template XML

---

## Step 5: Repack

```bash
python "[DOCX renderer scripts]/repack.py" \
  "[DOCX working dir]/unpacked/" \
  "[DOCX working dir]/meeting-notes-final.docx"
```

---

## Step 6: Validate

```bash
python "[DOCX renderer scripts]/validate.py" \
  "[DOCX working dir]/meeting-notes-final.docx"
```

**If validation fails:**
1. Read the error message carefully
2. Return to Step 4 and fix the XML
3. Repack (Step 5)
4. Validate again
5. Do not proceed until validation passes

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
| No npm `docx` library | Template-clone + XML edit only |
| Action column | Company/team names only — never individual person names |
| Status values | `In Progress`, `Pending`, `Completed` — no other values permitted |
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
