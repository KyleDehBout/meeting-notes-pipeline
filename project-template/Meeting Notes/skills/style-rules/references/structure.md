# Document structure reference — [PROJECT NAME]

## Strict section order
<!--
Define the exact order of sections in your meeting notes document. Example:
1. Header block — centred, bold: Project name → Meeting number → Date → Time
2. Attendees — three tab-separated fields: Name / Organisation / Title
3. Main items table — FOUR columns: Row number / Content / Action / Status
4. Numbered top-level sections with bold title
5. Subsection labels
6. Sub-items, with Action and Status set only where an item has an owner
7. Next meeting row
8. Prepared by line

The four-column table is not optional — it is what the renderer builds. Column 1 is an
automatic section counter, so the section number is never typed into the content column.
See skills/docx-renderer/references/table-structure.md.
-->
[TO BE FILLED IN — define your document's strict section order]

## Table column rules
<!--
Define the column layout for your main items table. Example:
- Column 1: Row number — automatic section counter, centred, never typed by hand
- Column 2: Content — left aligned
- Column 3: Action — organisation name only, centred
- Column 4: Status — one of the defined status values, centred
-->
[TO BE FILLED IN]

## Sub-item rules
<!--
Define rules for sub-items within sections. Example:
- A table row is a SECTION, not an item. One top-level section = one row. All of that
  section's title, subsection labels and sub-items sit as separate paragraphs inside
  that single row's content cell
- Never open a new row per sub-item — column 1 is a section counter, so a row per item
  renumbers every line and breaks the hierarchy
- Action and Status are set on the line of the sub-item they belong to, and left blank
  on lines facing a section title or a subsection label
- Consolidate multiple transcript exchanges into a single sub-item outcome
- Bullet lists permitted within content cell for technical lists
-->
[TO BE FILLED IN]

## Closing rows
<!--
Define any standard closing rows (next meeting date, prepared by, etc.)

Transcribe the label wording from a real issued document rather than inventing it,
and note whether the closing row carries a col 1 counter paragraph — it usually
should not, or it renders an orphan section number.
-->
[TO BE FILLED IN]
