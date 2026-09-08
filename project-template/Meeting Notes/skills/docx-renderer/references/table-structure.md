# Main Table Structure Reference

> **Note:** Column widths and numbering IDs are specific to your branded template.
> After setup, verify the `numId` value for list styles against your unpacked
> `word/numbering.xml`, and verify column widths against your unpacked `word/document.xml`.

## Contents
- Table properties
- Header row
- Row model — one row per section
- Content row — col 1 (row number)
- Content row — col 2 (discussion content, list levels)
- Content row — col 3 (action)
- Content row — col 4 (status)
- Meetings row (final row)

---

## Table properties

[TO BE FILLED IN — verify total width and column widths against your unpacked template]

Standard 4-column structure:

```xml
<w:tbl>
  <w:tblPr>
    <w:tblStyle w:val="TableGrid"/>
    <w:tblW w:w="[total width in DXA]" w:type="dxa"/>
    <w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0"
               w:firstColumn="1" w:lastColumn="0"
               w:noHBand="0" w:noVBand="1"/>
  </w:tblPr>
  <w:tblGrid>
    <w:gridCol w:w="[col 1 width]"/>
    <w:gridCol w:w="[col 2 width]"/>
    <w:gridCol w:w="[col 3 width]"/>
    <w:gridCol w:w="[col 4 width]"/>
  </w:tblGrid>
  <!-- rows go here -->
</w:tbl>
```

| Col | Role | Alignment |
|-----|------|-----------|
| 1 | Auto row number | Centre |
| 2 | Discussion content | Left |
| 3 | Action (company name only) | Centre |
| 4 | Status | Centre |

---

## Header row

Row height typically 116 DXA. Col 1 is empty; cols 2–4 have bold centred text.

```xml
<w:tr>
  <w:trPr><w:trHeight w:val="116"/></w:trPr>
  <w:tc>
    <w:tcPr><w:tcW w:w="[col 1 width]" w:type="dxa"/></w:tcPr>
    <w:p><w:pPr><w:spacing w:after="0"/><w:jc w:val="center"/></w:pPr></w:p>
  </w:tc>
  <w:tc>
    <w:tcPr><w:tcW w:w="[col 2 width]" w:type="dxa"/></w:tcPr>
    <w:p>
      <w:pPr>
        <w:spacing w:after="0"/>
        <w:jc w:val="center"/>
        <w:rPr>
          <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>
          <w:b/><w:bCs/>
          <w:sz w:val="22"/><w:szCs w:val="22"/>
          <w:lang w:val="en-GB"/>
        </w:rPr>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>
          <w:b/><w:bCs/>
          <w:sz w:val="22"/><w:szCs w:val="22"/>
          <w:lang w:val="en-GB"/>
        </w:rPr>
        <w:t>[PROJECT NAME]</w:t>
      </w:r>
    </w:p>
  </w:tc>
  <!-- Repeat pattern for Action and Status columns -->
</w:tr>
```

---

## Row model — one row per section

**A table row is a SECTION, not an item.** One top-level section of the notes
occupies exactly one `<w:tr>`. Everything belonging to that section — its title,
its subsection labels and all of its numbered sub-items — lives as multiple
paragraphs inside that single row's col 2.

Do not open a new row for each sub-item. Col 1 carries the section counter, so a
row per sub-item advances the section number on every line: section titles lose
their number entirely and sub-items render with a zero in the middle ("3.0.1")
because the ilvl-1 counter never advanced. `validate.py` fails a document whose
rows advance the counter without carrying a section title.

```
<w:tr>                          ← section 1
  col 1: counter paragraph      ← numPr, ilvl 0, live numId   → renders "1."
  col 2: section title          ← numPr, ilvl 0, numId="0"    → number suppressed
         subsection label       ← numPr, ilvl 1, live numId   → renders "1.1"
         sub-item               ← numPr, ilvl 2, live numId   → renders "1.1.1"
         sub-item               ← numPr, ilvl 2, live numId   → renders "1.1.2"
  col 3: blank ×3, then "ONLE" on the paragraph facing its sub-item
  col 4: blank ×3, then "Pending" on the same index
</w:tr>
<w:tr>                          ← section 2
  ...
</w:tr>
```

Cols 3 and 4 hold one paragraph per col-2 paragraph, so an Action or Status sits
on the same visual line as the sub-item it belongs to. Paragraphs facing a section
title or a subsection label are empty.

The final Meetings row is the one exception: it carries no counter in col 1.

---

## Content rows — shared border rule

Every content row cell (except the Meetings row) has a bottom border only:

```xml
<w:tcBorders>
  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/>
</w:tcBorders>
```

---

## Col 1 — Row number (auto-list)

Uses a numbering style from `numbering.xml`. Verify the correct `numId` value by inspecting your unpacked template's `word/numbering.xml`.

```xml
<w:tc>
  <w:tcPr>
    <w:tcW w:w="[col 1 width]" w:type="dxa"/>
    <w:tcBorders>
      <w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/>
    </w:tcBorders>
  </w:tcPr>
  <w:p>
    <w:pPr>
      <w:pStyle w:val="[list style name]"/>
      <w:numPr>
        <w:ilvl w:val="0"/>
        <w:numId w:val="[numId from numbering.xml]"/>
      </w:numPr>
      <w:spacing w:line="240" w:lineRule="auto"/>
    </w:pPr>
  </w:p>
</w:tc>
```

---

## Col 2 — Content (list hierarchy)

All levels reference `numId` from `numbering.xml`. Do not redefine — reference only.

### Level 0 — Section title

The section's own number is painted by the col 1 counter, so this paragraph must
**suppress** its number rather than omit numbering altogether. `numId="0"` at
`ilvl="0"` is the suppression — it is deliberate here and is the one place in the
document where `numId="0"` is correct.

Omitting `<w:numPr>` entirely is a bug: the paragraph then falls back to its list
style's own numbering and the section title drifts out of the hierarchy.

```xml
<w:p>
  <w:pPr>
    <w:pStyle w:val="[list style name]"/>
    <w:numPr>
      <w:ilvl w:val="0"/>
      <w:numId w:val="0"/>
    </w:numPr>
    <w:spacing w:line="240" w:lineRule="auto"/>
  </w:pPr>
  <w:r>
    <w:t>Section title text</w:t>
  </w:r>
</w:p>
```

### Level 1 — Subsection label

Renders as "1.1", "1.2" … Italic, no bold. One per topic within the section.

```xml
<w:p>
  <w:pPr>
    <w:pStyle w:val="[sub-list style name]"/>
    <w:numPr>
      <w:ilvl w:val="1"/>
      <w:numId w:val="[numId]"/>
    </w:numPr>
    <w:spacing w:line="240" w:lineRule="auto"/>
  </w:pPr>
  <w:r><w:rPr><w:i/></w:rPr><w:t>Subsection label</w:t></w:r>
</w:p>
```

### Level 2 — Numbered sub-items

```xml
<w:p>
  <w:pPr>
    <w:pStyle w:val="[sub-list style name]"/>
    <w:numPr>
      <w:ilvl w:val="2"/>
      <w:numId w:val="[numId]"/>
    </w:numPr>
    <w:spacing w:after="240" w:line="240" w:lineRule="auto"/>
    <w:ind w:left="[value]" w:hanging="[value]"/>
  </w:pPr>
  <w:r><w:t>Sub-item text here.</w:t></w:r>
</w:p>
```

### Level 3 — Bullet sub-items

```xml
<w:p>
  <w:pPr>
    <w:pStyle w:val="[sub-list style name]"/>
    <w:numPr>
      <w:ilvl w:val="3"/>
      <w:numId w:val="[numId]"/>
    </w:numPr>
    <w:spacing w:after="240" w:line="240" w:lineRule="auto"/>
    <w:ind w:left="[value]" w:hanging="[value]"/>
  </w:pPr>
  <w:r><w:t>Bullet text here.</w:t></w:r>
</w:p>
```

---

## Col 3 — Action

**HARD RULE: Company or team names only. Never individual person names.**

Col 3 holds one paragraph per col-2 paragraph in the same row, so each Action
lands on the line of the sub-item it belongs to. Paragraphs facing the section
title, a subsection label, or a sub-item with no owner are empty.

```xml
<w:tc>
  <w:tcPr>
    <w:tcW w:w="[col 3 width]" w:type="dxa"/>
    <w:tcBorders>
      <w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/>
    </w:tcBorders>
  </w:tcPr>
  <w:p><w:pPr><w:spacing w:after="120"/></w:pPr></w:p>
  <w:p>
    <w:pPr>
      <w:spacing w:after="0"/>
      <w:jc w:val="center"/>
    </w:pPr>
    <w:r><w:t>[Organisation Name]</w:t></w:r>
  </w:p>
</w:tc>
```

---

## Col 4 — Status

Same structure as Col 3. Permitted values: `In Progress` / `Pending` / `No Action`. No other values.

---

## Meetings row (final table row)

No bottom border on any cell. Only col 2 has content — two bold paragraphs.

```xml
<w:tr>
  <w:trPr><w:trHeight w:val="61"/></w:trPr>
  <!-- Cols 1, 3, 4: empty paragraphs only -->
  <w:tc>
    <w:tcPr><w:tcW w:w="[col 2 width]" w:type="dxa"/></w:tcPr>
    <w:p>
      <w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>
      <w:r><w:t>MEETINGS</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>
      <w:r><w:t>The next meeting date is [Day name] [Month] [D], [Year].</w:t></w:r>
    </w:p>
  </w:tc>
</w:tr>
```
