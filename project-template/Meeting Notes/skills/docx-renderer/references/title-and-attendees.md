# Title Block and Attendees Reference

> **Note:** The XML values below (font sizes, spacing, margins) are extracted from this
> project's blank template during setup. Verify against your unpacked template's
> `word/document.xml` if output formatting looks wrong.

## Contents
- Page setup (sectPr)
- Title block paragraphs
- Attendees label
- Attendee rows

---

## Page setup

Copy `<w:sectPr>` verbatim from the unpacked template. Do not recalculate these values — they are specific to your branded template file.

[TO BE FILLED IN — extracted by setup from your uploaded branded .docx]

Example structure (values will differ):
```xml
<w:pgSz w:w="12240" w:h="15840"/>
<w:pgMar w:top="[value]" w:right="[value]" w:bottom="[value]" w:left="[value]"
         w:header="[value]" w:footer="[value]" w:gutter="0"/>
<w:titlePg/>
```

---

## Title block

Four paragraphs in order: project name → "Held on" → date → time.

All four are centred, bold, typically 14pt, no spacing after, line spacing 240 auto.

```xml
<w:p>
  <w:pPr>
    <w:spacing w:after="0" w:line="240" w:lineRule="auto"/>
    <w:jc w:val="center"/>
    <w:rPr>
      <w:b/><w:bCs/>
      <w:sz w:val="28"/><w:szCs w:val="28"/>
      <w:lang w:val="en-GB"/>
    </w:rPr>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:b/><w:bCs/>
      <w:sz w:val="28"/><w:szCs w:val="28"/>
      <w:lang w:val="en-GB"/>
    </w:rPr>
    <w:t>[PROJECT NAME] - Project Meeting</w:t>
  </w:r>
</w:p>
```

Repeat for: `Held on` / `[Day name] [Month] [D], [Year]` / `[Time]`

Date format: `Thursday June 18, 2026` — no superscript ordinal suffix in the title block.

The opening empty paragraph (before the title block) uses the same `<w:rPr>` with no `<w:r>` child.

---

## Attendees label

Times New Roman 11pt, bold, line spacing 276 auto, no spacing after.

```xml
<w:p>
  <w:pPr>
    <w:spacing w:after="0" w:line="276" w:lineRule="auto"/>
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
    <w:t>Attendees:</w:t>
  </w:r>
</w:p>
```

---

## Attendee rows

One paragraph per person. Three tab stops: Name / Company / Position.
Tab stop positions should match your template — verify against the unpacked XML.

```xml
<w:p>
  <w:pPr>
    <w:tabs>
      <w:tab w:val="left" w:pos="0"/>
      <w:tab w:val="left" w:pos="[company tab position in DXA]"/>
      <w:tab w:val="left" w:pos="[position tab position in DXA]"/>
    </w:tabs>
    <w:spacing w:after="0" w:line="276" w:lineRule="auto"/>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>
      <w:sz w:val="22"/><w:szCs w:val="22"/>
      <w:lang w:val="en-GB"/>
    </w:rPr>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>
      <w:sz w:val="22"/><w:szCs w:val="22"/>
      <w:lang w:val="en-GB"/>
    </w:rPr>
    <w:t>Jane Smith</w:t>
    <w:tab/><w:t>Organisation Name</w:t>
    <w:tab/><w:t>Project Manager</w:t>
  </w:r>
</w:p>
```

Repeat for each attendee. Follow with two empty paragraphs before the table.
