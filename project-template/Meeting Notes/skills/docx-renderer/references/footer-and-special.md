# Footer and Special Formatting Reference

## Contents
- Footer paragraph
- Superscript ordinal dates
- Special character escaping
- Common XML pitfalls

---

## Footer paragraph

Placed after `</w:tbl>`, before `<w:sectPr>`. Spacing before 240.

Adjust organisation name, bold/colour styling to match your branded template.

```xml
<w:p>
  <w:pPr>
    <w:spacing w:before="240"/>
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
    <w:t xml:space="preserve">Prepared by: </w:t>
  </w:r>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>
      <w:b/><w:bCs/>
      <w:color w:val="[brand colour hex, no #]"/>
      <w:sz w:val="22"/><w:szCs w:val="22"/>
      <w:lang w:val="en-GB"/>
    </w:rPr>
    <w:t>[ORGANISATION]</w:t>
  </w:r>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>
      <w:sz w:val="22"/><w:szCs w:val="22"/>
      <w:lang w:val="en-GB"/>
    </w:rPr>
    <w:t xml:space="preserve"> Limited</w:t>
  </w:r>
</w:p>
```

---

## Superscript ordinal dates

When a date includes an ordinal suffix (1st, 2nd, 19th, etc.), split into three runs:

```xml
<w:r>
  <w:rPr><w:lang w:val="en-US"/></w:rPr>
  <w:t xml:space="preserve">June 19</w:t>
</w:r>
<w:r>
  <w:rPr>
    <w:vertAlign w:val="superscript"/>
    <w:lang w:val="en-US"/>
  </w:rPr>
  <w:t>th</w:t>
</w:r>
<w:r>
  <w:rPr><w:lang w:val="en-US"/></w:rPr>
  <w:t xml:space="preserve"> 2026</w:t>
</w:r>
```

---

## Special character escaping

| Character | XML entity | Example |
|-----------|------------|---------|
| `&` | `&amp;` | `Survey &amp; Topographical Data` |
| `'` (apostrophe) | `&#x2019;` | `it&#x2019;s` |
| `"` (open quote) | `&#x201C;` | `&#x201C;quoted&#x201D;` |
| `"` (close quote) | `&#x201D;` | see above |

Raw `&` in `<w:t>` content will corrupt the XML. Always escape.

---

## Common XML pitfalls

| Pitfall | Fix |
|---------|-----|
| Leading/trailing space stripped | Add `xml:space="preserve"` to `<w:t>` |
| Raw `&` in text | Replace with `&amp;` |
| New numbering definitions | Never — reference existing `numId` from `numbering.xml` |
| Modifying header/footer files | Never — leave all `header*.xml`, `footer*.xml`, `word/media/` untouched |
| Using npm `docx` library | Never — template clone + XML edit only |
| Person names in Action column | Never — companies/teams only |
| Status values outside the permitted set | Never — `In Progress`, `Pending`, `Completed` only |
