#!/usr/bin/env python3
"""
setup_docx_renderer.py

Complete one-time setup for the DOCX renderer skill.

Given a branded .docx source file (a past meeting notes file or letterhead),
this script:
  1. Strips the body content while preserving headers, footers, styles,
     images, numbering, and sectPr — producing the blank template
  2. Unpacks the source to extract the exact XML formatting values
     (column widths, numIds, font specs, tab stops, spacing, colours)
  3. Generates fully-populated reference files for the docx-renderer skill

Usage:
    python setup_docx_renderer.py <source.docx> <project_name> <meeting_notes_dir>

Outputs:
    <meeting_notes_dir>/<project_name>_blank_template.docx
    <meeting_notes_dir>/skills/docx-renderer/references/title-and-attendees.md
    <meeting_notes_dir>/skills/docx-renderer/references/table-structure.md
    <meeting_notes_dir>/skills/docx-renderer/references/footer-and-special.md
"""

import sys
import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'


# ── XML helpers ───────────────────────────────────────────────────────────────

def wn(tag):
    return f'{{{W}}}{tag}'


def wa(el, name, default=None):
    """Get a w:-namespaced attribute."""
    if el is None:
        return default
    return el.get(wn(name), el.get(name, default))


def wf(el, *path):
    """Navigate a chain of w:-qualified child tags."""
    cur = el
    for tag in path:
        if cur is None:
            return None
        cur = cur.find(wn(tag))
    return cur


def rpr_values(rpr):
    """Extract common run properties from a <w:rPr> element."""
    if rpr is None:
        return {}
    fonts = rpr.find(wn('rFonts'))
    sz = rpr.find(wn('sz'))
    sz_cs = rpr.find(wn('szCs'))
    lang = rpr.find(wn('lang'))
    color = rpr.find(wn('color'))
    bold = rpr.find(wn('b'))
    return {
        'font': wa(fonts, 'ascii') if fonts is not None else None,
        'font_hansi': wa(fonts, 'hAnsi') if fonts is not None else None,
        'sz': wa(sz, 'val') if sz is not None else None,
        'sz_cs': wa(sz_cs, 'val') if sz_cs is not None else None,
        'lang': wa(lang, 'val') if lang is not None else None,
        'color': wa(color, 'val') if color is not None else None,
        'bold': bold is not None,
    }


def font_xml(rv, indent='      '):
    """Build <w:rFonts> + size + lang XML lines from rpr_values dict."""
    lines = []
    font = rv.get('font') or 'Times New Roman'
    sz = rv.get('sz') or '22'
    sz_cs = rv.get('sz_cs') or sz
    lang = rv.get('lang') or 'en-GB'
    lines.append(f'{indent}<w:rFonts w:ascii="{font}" w:hAnsi="{font}"/>')
    lines.append(f'{indent}<w:sz w:val="{sz}"/><w:szCs w:val="{sz_cs}"/>')
    lines.append(f'{indent}<w:lang w:val="{lang}"/>')
    return '\n'.join(lines)


# ── Blank template creation ───────────────────────────────────────────────────

def strip_body(doc_xml_bytes):
    content = doc_xml_bytes.decode('utf-8')
    body_close = content.rfind('</w:body>')
    if body_close == -1:
        raise ValueError("No </w:body> in document.xml")
    sect_start = content.rfind('<w:sectPr', 0, body_close)
    if sect_start == -1:
        raise ValueError("No <w:sectPr> in document.xml — cannot preserve header/footer references")
    sect_block = content[sect_start:body_close]
    body_open = content.find('<w:body>')
    if body_open == -1:
        body_open = content.find('<w:body ')
        body_tag_end = content.find('>', body_open) + 1
    else:
        body_tag_end = body_open + len('<w:body>')
    empty_para = '<w:p><w:pPr><w:rPr/></w:pPr></w:p>'
    return (content[:body_tag_end] + empty_para + sect_block + content[body_close:]).encode('utf-8')


def create_blank_template(src, dst):
    with zipfile.ZipFile(src, 'r') as zin:
        names = zin.namelist()
        if 'word/document.xml' not in names:
            raise ValueError("Source is not a valid .docx — missing word/document.xml")
        with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
            for name in names:
                data = zin.read(name)
                if name == 'word/document.xml':
                    data = strip_body(data)
                zout.writestr(name, data)
    # Verify
    with zipfile.ZipFile(dst) as z:
        bad = z.testzip()
        if bad:
            raise ValueError(f"Created template is corrupt: {bad}")


# ── Value extraction ──────────────────────────────────────────────────────────

def extract_values(src_path):
    v = {}
    log = []

    with zipfile.ZipFile(src_path) as z:
        doc_xml = z.read('word/document.xml')

    root = ET.fromstring(doc_xml)
    body = root.find(wn('body'))
    if body is None:
        raise ValueError("No <w:body> in document.xml")

    body_children = list(body)

    # ── sectPr ────────────────────────────────────────────────────────────────
    sect = body.find(wn('sectPr'))
    if sect is not None:
        pg_sz = sect.find(wn('pgSz'))
        pg_mar = sect.find(wn('pgMar'))
        v['page_w']      = wa(pg_sz,  'w',       '12240')
        v['page_h']      = wa(pg_sz,  'h',       '15840')
        v['mar_top']     = wa(pg_mar, 'top',     '2790')
        v['mar_right']   = wa(pg_mar, 'right',   '1440')
        v['mar_bottom']  = wa(pg_mar, 'bottom',  '1620')
        v['mar_left']    = wa(pg_mar, 'left',    '1418')
        v['mar_header']  = wa(pg_mar, 'header',  '706')
        v['mar_footer']  = wa(pg_mar, 'footer',  '1295')
        v['mar_gutter']  = wa(pg_mar, 'gutter',  '0')
        v['title_pg']    = sect.find(wn('titlePg')) is not None
        v['cols_space']  = wa(sect.find(wn('cols')), 'space', '709') if sect.find(wn('cols')) is not None else '709'
        log.append(f"✓ Page: {v['page_w']}×{v['page_h']} DXA, margins top={v['mar_top']} left={v['mar_left']}")
    else:
        v.update({'page_w':'12240','page_h':'15840','mar_top':'2790','mar_right':'1440',
                  'mar_bottom':'1620','mar_left':'1418','mar_header':'706','mar_footer':'1295',
                  'mar_gutter':'0','title_pg':True,'cols_space':'709'})
        log.append("⚠ sectPr not found — using letter-size defaults")

    # ── Identify body regions ─────────────────────────────────────────────────
    tbl_indices = [i for i, el in enumerate(body_children) if el.tag == wn('tbl')]
    first_tbl_idx = tbl_indices[0] if tbl_indices else len(body_children)
    pre_table  = [el for el in body_children[:first_tbl_idx] if el.tag == wn('p')]
    post_table = [el for el in body_children[first_tbl_idx+1:] if el.tag == wn('p')] if tbl_indices else []

    # ── Title block (centred bold paragraphs near top) ────────────────────────
    v['title_sz']   = '28'
    v['title_sz_cs']= '28'
    v['title_lang'] = 'en-GB'
    v['title_line'] = '240'

    for p in pre_table[:12]:
        pPr = p.find(wn('pPr'))
        if pPr is None:
            continue
        jc = pPr.find(wn('jc'))
        if jc is None or wa(jc, 'val') != 'center':
            continue
        rpr = pPr.find(wn('rPr'))
        rv = rpr_values(rpr)
        if rv.get('sz'):
            v['title_sz']    = rv['sz']
            v['title_sz_cs'] = rv.get('sz_cs') or rv['sz']
        if rv.get('lang'):
            v['title_lang'] = rv['lang']
        spacing = pPr.find(wn('spacing'))
        if spacing is not None:
            v['title_line'] = wa(spacing, 'line', '240')
        log.append(f"✓ Title block: sz={v['title_sz']}, lang={v['title_lang']}, line={v['title_line']}")
        break

    # ── Attendees (paragraphs with tab stops) ─────────────────────────────────
    v['att_sz']           = '22'
    v['att_sz_cs']        = '22'
    v['att_lang']         = 'en-GB'
    v['att_line']         = '276'
    v['att_tab_company']  = '2880'
    v['att_tab_position'] = '6480'
    v['att_font']         = 'Times New Roman'

    for p in pre_table:
        pPr = p.find(wn('pPr'))
        if pPr is None:
            continue
        tabs_el = pPr.find(wn('tabs'))
        if tabs_el is None:
            continue
        positions = [wa(t, 'pos') for t in tabs_el.findall(wn('tab')) if wa(t, 'pos')]
        if len(positions) < 2:
            continue
        v['att_tab_company']  = positions[1] if len(positions) > 1 else '2880'
        v['att_tab_position'] = positions[2] if len(positions) > 2 else '6480'
        rpr = pPr.find(wn('rPr'))
        rv = rpr_values(rpr)
        if rv.get('font'):  v['att_font']   = rv['font']
        if rv.get('sz'):    v['att_sz']     = rv['sz']
        if rv.get('sz_cs'): v['att_sz_cs']  = rv['sz_cs']
        if rv.get('lang'):  v['att_lang']   = rv['lang']
        spacing = pPr.find(wn('spacing'))
        if spacing is not None:
            v['att_line'] = wa(spacing, 'line', '276')
        log.append(f"✓ Attendees: font={v['att_font']}, sz={v['att_sz']}, tabs={positions}")
        break

    # ── Main table ────────────────────────────────────────────────────────────
    tables = body.findall(f'.//{wn("tbl")}')
    main_tbl = None
    if tables:
        def tbl_w(tbl):
            el = tbl.find(f'.//{wn("tblW")}')
            try: return int(wa(el, 'w', '0'))
            except: return 0
        main_tbl = max(tables, key=tbl_w)

    # Table defaults (LP2-style, 4 cols)
    v['tbl_total_w']        = '9715'
    v['col_widths']         = ['490', '5696', '2050', '1479']
    v['tbl_look_val']       = '04A0'
    v['tbl_look_first_row'] = '1'
    v['tbl_look_last_row']  = '0'
    v['tbl_look_first_col'] = '1'
    v['tbl_look_last_col']  = '0'
    v['tbl_look_no_hband']  = '0'
    v['tbl_look_no_vband']  = '1'
    v['header_row_h']       = '116'
    v['meetings_row_h']     = '61'
    v['num_id']             = '5'
    v['col1_style']         = '10List'
    v['col2_style_l0']      = '10List'
    v['col2_style_l2']      = '11List'
    v['col2_style_l3']      = '11List'
    v['l2_left']  = '1292'; v['l2_hanging']  = '630'
    v['l3_left']  = '1744'; v['l3_hanging']  = '270'
    v['tbl_font'] = 'Times New Roman'
    v['tbl_sz']   = '22'
    v['tbl_lang'] = 'en-GB'

    if main_tbl is not None:
        tbl_pr = main_tbl.find(wn('tblPr'))
        tbl_w_el = wf(tbl_pr, 'tblW') if tbl_pr else None
        tbl_look  = wf(tbl_pr, 'tblLook') if tbl_pr else None

        if tbl_w_el is not None:
            v['tbl_total_w'] = wa(tbl_w_el, 'w', '9715')

        if tbl_look is not None:
            v['tbl_look_val']       = wa(tbl_look, 'val',         '04A0')
            v['tbl_look_first_row'] = wa(tbl_look, 'firstRow',    '1')
            v['tbl_look_last_row']  = wa(tbl_look, 'lastRow',     '0')
            v['tbl_look_first_col'] = wa(tbl_look, 'firstColumn', '1')
            v['tbl_look_last_col']  = wa(tbl_look, 'lastColumn',  '0')
            v['tbl_look_no_hband']  = wa(tbl_look, 'noHBand',     '0')
            v['tbl_look_no_vband']  = wa(tbl_look, 'noVBand',     '1')

        grid = main_tbl.find(wn('tblGrid'))
        if grid is not None:
            widths = [wa(c, 'w', '0') for c in grid.findall(wn('gridCol'))]
            if widths:
                v['col_widths'] = widths
        log.append(f"✓ Table: total={v['tbl_total_w']}, cols={v['col_widths']}")

        rows = main_tbl.findall(wn('tr'))
        if rows:
            h = wf(rows[0], 'trPr', 'trHeight')
            if h is not None: v['header_row_h'] = wa(h, 'val', '116')
            m = wf(rows[-1], 'trPr', 'trHeight')
            if m is not None: v['meetings_row_h'] = wa(m, 'val', '61')

            # Extract from first data row
            if len(rows) > 1:
                data_row = rows[1]
                cells = data_row.findall(wn('tc'))

                # Col 1: numId and style
                if cells:
                    num_id_el = cells[0].find(f'.//{wn("numId")}')
                    if num_id_el is not None:
                        v['num_id'] = wa(num_id_el, 'val', '5')
                    p_style = cells[0].find(f'.//{wn("pStyle")}')
                    if p_style is not None:
                        v['col1_style'] = wa(p_style, 'val', '10List')

                # Col 2: level styles and indentation — scan all data rows
                for row in rows[1:min(len(rows), 6)]:
                    rc = row.findall(wn('tc'))
                    if len(rc) < 2:
                        continue
                    for p in rc[1].findall(wn('p')):
                        ilvl_el = p.find(f'.//{wn("ilvl")}')
                        ps_el   = p.find(f'.//{wn("pStyle")}')
                        ind_el  = p.find(f'.//{wn("ind")}')
                        if ilvl_el is None:
                            continue
                        lvl = wa(ilvl_el, 'val', '')
                        sn  = wa(ps_el, 'val', '') if ps_el is not None else ''
                        if lvl == '0' and sn: v['col2_style_l0'] = sn
                        if lvl == '2':
                            if sn: v['col2_style_l2'] = sn
                            if ind_el is not None:
                                v['l2_left']    = wa(ind_el, 'left',    '1292')
                                v['l2_hanging'] = wa(ind_el, 'hanging', '630')
                        if lvl == '3':
                            if sn: v['col2_style_l3'] = sn
                            if ind_el is not None:
                                v['l3_left']    = wa(ind_el, 'left',    '1744')
                                v['l3_hanging'] = wa(ind_el, 'hanging', '270')

                # Font from any cell rPr
                for row in rows[:3]:
                    for tc in row.findall(wn('tc')):
                        rpr = tc.find(f'.//{wn("rPr")}')
                        rv = rpr_values(rpr)
                        if rv.get('font'):
                            v['tbl_font'] = rv['font']
                            v['tbl_sz']   = rv.get('sz') or '22'
                            v['tbl_lang'] = rv.get('lang') or 'en-GB'
                            break
                    else:
                        continue
                    break

        log.append(f"✓ numId={v['num_id']}, col1={v['col1_style']}, col2_l0={v['col2_style_l0']}")
        log.append(f"✓ l2 indent: left={v['l2_left']} hanging={v['l2_hanging']}")
        log.append(f"✓ l3 indent: left={v['l3_left']} hanging={v['l3_hanging']}")
    else:
        log.append("⚠ No table found — using LP2-style defaults")

    # ── Footer paragraph ("Prepared by:") ────────────────────────────────────
    v['footer_sz']             = '22'
    v['footer_sz_cs']          = '22'
    v['footer_lang']           = 'en-GB'
    v['footer_font']           = 'Times New Roman'
    v['footer_spacing_before'] = '240'
    v['org_name']              = 'IBEC'
    v['org_suffix']            = ' Limited'
    v['org_color']             = '243E6C'

    for p in post_table:
        runs = p.findall(wn('r'))
        full_text = ''.join((r.find(wn('t')).text or '') for r in runs
                             if r.find(wn('t')) is not None)
        if 'prepared by' not in full_text.lower():
            continue
        pPr = p.find(wn('pPr'))
        spacing = wf(pPr, 'spacing') if pPr else None
        if spacing is not None:
            v['footer_spacing_before'] = wa(spacing, 'before', '240')
        for r in runs:
            rpr = r.find(wn('rPr'))
            rv = rpr_values(rpr)
            t_el = r.find(wn('t'))
            text_raw = (t_el.text or '') if t_el is not None else ''
            text = text_raw.strip()
            if rv.get('font'):
                v['footer_font']    = rv['font']
                v['footer_sz']      = rv.get('sz') or '22'
                v['footer_sz_cs']   = rv.get('sz_cs') or v['footer_sz']
                v['footer_lang']    = rv.get('lang') or 'en-GB'
            if rv.get('bold') and rv.get('color') and rv['color'].lower() not in ('auto','000000','ffffff'):
                v['org_color'] = rv['color']
                if text:
                    v['org_name'] = text
            elif not rv.get('bold') and text and 'Prepared' not in text and text != v['org_name']:
                v['org_suffix'] = text_raw  # preserve leading space, e.g. " Limited"
        log.append(f"✓ Footer: org={v['org_name']}{v['org_suffix']}, color=#{v['org_color']}, sz={v['footer_sz']}")
        break

    v['_log'] = log
    return v


# ── Reference file generation ─────────────────────────────────────────────────

def gen_title_and_attendees(v, project_name):
    cw = v['col_widths']
    col1_w = cw[0] if cw else '490'

    t_font  = v.get('tbl_font', 'Times New Roman')
    t_sz    = v.get('tbl_sz', '22')
    t_lang  = v.get('tbl_lang', 'en-GB')
    a_font  = v.get('att_font', 'Times New Roman')
    a_sz    = v.get('att_sz', '22')
    a_sz_cs = v.get('att_sz_cs', a_sz)
    a_lang  = v.get('att_lang', 'en-GB')
    a_line  = v.get('att_line', '276')

    return f"""# Title Block and Attendees Reference

## Contents
- Page setup (sectPr)
- Title block paragraphs
- Attendees label
- Attendee rows

---

## Page setup

Copy `<w:sectPr>` verbatim from the unpacked template. Do not recalculate.

```xml
<w:pgSz w:w="{v['page_w']}" w:h="{v['page_h']}"/>
<w:pgMar w:top="{v['mar_top']}" w:right="{v['mar_right']}" w:bottom="{v['mar_bottom']}" w:left="{v['mar_left']}"
         w:header="{v['mar_header']}" w:footer="{v['mar_footer']}" w:gutter="{v['mar_gutter']}"/>
<w:cols w:space="{v['cols_space']}"/>
{('<w:titlePg/>') if v.get('title_pg') else '<!-- no titlePg in source -->'}
```

---

## Title block

Four paragraphs in order: project name → "Held on" → date → time.
All four: centred, bold, no spacing after, line spacing {v['title_line']} auto.

```xml
<w:p>
  <w:pPr>
    <w:spacing w:after="0" w:line="{v['title_line']}" w:lineRule="auto"/>
    <w:jc w:val="center"/>
    <w:rPr>
      <w:b/><w:bCs/>
      <w:sz w:val="{v['title_sz']}"/><w:szCs w:val="{v['title_sz_cs']}"/>
      <w:lang w:val="{v['title_lang']}"/>
    </w:rPr>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:b/><w:bCs/>
      <w:sz w:val="{v['title_sz']}"/><w:szCs w:val="{v['title_sz_cs']}"/>
      <w:lang w:val="{v['title_lang']}"/>
    </w:rPr>
    <w:t>{project_name} - Project Meeting</w:t>
  </w:r>
</w:p>
```

Repeat for: `Held on` / `Thursday June 18, 2026` / `3:00PM`

Date format: `[Day name] [Month] [D], [Year]` — e.g. "Thursday June 18, 2026"

The opening empty paragraph uses the same `<w:rPr>` with no `<w:r>` child.

---

## Attendees label

{a_font} {int(a_sz)//2}pt, bold, line spacing {a_line} auto, no spacing after.

```xml
<w:p>
  <w:pPr>
    <w:spacing w:after="0" w:line="{a_line}" w:lineRule="auto"/>
    <w:rPr>
      <w:rFonts w:ascii="{a_font}" w:hAnsi="{a_font}"/>
      <w:b/><w:bCs/>
      <w:sz w:val="{a_sz}"/><w:szCs w:val="{a_sz_cs}"/>
      <w:lang w:val="{a_lang}"/>
    </w:rPr>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="{a_font}" w:hAnsi="{a_font}"/>
      <w:b/><w:bCs/>
      <w:sz w:val="{a_sz}"/><w:szCs w:val="{a_sz_cs}"/>
      <w:lang w:val="{a_lang}"/>
    </w:rPr>
    <w:t>Attendees:</w:t>
  </w:r>
</w:p>
```

---

## Attendee rows

One paragraph per person. Tab stops: Name (0) / Company ({v['att_tab_company']} DXA) / Position ({v['att_tab_position']} DXA).

```xml
<w:p>
  <w:pPr>
    <w:tabs>
      <w:tab w:val="left" w:pos="0"/>
      <w:tab w:val="left" w:pos="{v['att_tab_company']}"/>
      <w:tab w:val="left" w:pos="{v['att_tab_position']}"/>
    </w:tabs>
    <w:spacing w:after="0" w:line="{a_line}" w:lineRule="auto"/>
    <w:rPr>
      <w:rFonts w:ascii="{a_font}" w:hAnsi="{a_font}"/>
      <w:sz w:val="{a_sz}"/><w:szCs w:val="{a_sz_cs}"/>
      <w:lang w:val="{a_lang}"/>
    </w:rPr>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="{a_font}" w:hAnsi="{a_font}"/>
      <w:sz w:val="{a_sz}"/><w:szCs w:val="{a_sz_cs}"/>
      <w:lang w:val="{a_lang}"/>
    </w:rPr>
    <w:t>Jane Smith</w:t>
    <w:tab/><w:t>Organisation Name</w:t>
    <w:tab/><w:t>Project Manager</w:t>
  </w:r>
</w:p>
```

Repeat for each attendee. Follow with two empty paragraphs before the table.
"""


def gen_table_structure(v, project_name):
    cw = v['col_widths']
    while len(cw) < 4:
        cw.append('0')

    t_font = v.get('tbl_font', 'Times New Roman')
    t_sz   = v.get('tbl_sz', '22')
    t_lang = v.get('tbl_lang', 'en-GB')

    rpr_block = f"""      <w:rFonts w:ascii="{t_font}" w:hAnsi="{t_font}"/>
      <w:b/><w:bCs/>
      <w:sz w:val="{t_sz}"/><w:szCs w:val="{t_sz}"/>
      <w:lang w:val="{t_lang}"/>"""

    rpr_plain = f"""      <w:rFonts w:ascii="{t_font}" w:hAnsi="{t_font}"/>
      <w:sz w:val="{t_sz}"/><w:szCs w:val="{t_sz}"/>
      <w:lang w:val="{t_lang}"/>"""

    return f"""# Main Table Structure Reference

## Contents
- Table properties
- Header row
- Content row — col 1 (row number)
- Content row — col 2 (discussion content, list levels)
- Content row — col 3 (action)
- Content row — col 4 (status)
- Meetings row (final row)

---

## Table properties

Total width {v['tbl_total_w']} DXA. Column widths must sum to exactly {v['tbl_total_w']}.

```xml
<w:tbl>
  <w:tblPr>
    <w:tblStyle w:val="TableGrid"/>
    <w:tblW w:w="{v['tbl_total_w']}" w:type="dxa"/>
    <w:tblLook w:val="{v['tbl_look_val']}" w:firstRow="{v['tbl_look_first_row']}" w:lastRow="{v['tbl_look_last_row']}"
               w:firstColumn="{v['tbl_look_first_col']}" w:lastColumn="{v['tbl_look_last_col']}"
               w:noHBand="{v['tbl_look_no_hband']}" w:noVBand="{v['tbl_look_no_vband']}"/>
  </w:tblPr>
  <w:tblGrid>
    <w:gridCol w:w="{cw[0]}"/>
    <w:gridCol w:w="{cw[1]}"/>
    <w:gridCol w:w="{cw[2]}"/>
    <w:gridCol w:w="{cw[3]}"/>
  </w:tblGrid>
  <!-- rows go here -->
</w:tbl>
```

| Col | Width DXA | Role | Alignment |
|-----|-----------|------|-----------|
| 1 | {cw[0]} | Auto row number | Centre |
| 2 | {cw[1]} | Discussion content | Left |
| 3 | {cw[2]} | Action (company name only) | Centre |
| 4 | {cw[3]} | Status | Centre |

---

## Header row

Row height {v['header_row_h']} DXA. Col 1 is empty; cols 2–4 have bold centred text.

```xml
<w:tr>
  <w:trPr><w:trHeight w:val="{v['header_row_h']}"/></w:trPr>
  <w:tc>
    <w:tcPr><w:tcW w:w="{cw[0]}" w:type="dxa"/></w:tcPr>
    <w:p><w:pPr><w:spacing w:after="0"/><w:jc w:val="center"/></w:pPr></w:p>
  </w:tc>
  <w:tc>
    <w:tcPr><w:tcW w:w="{cw[1]}" w:type="dxa"/></w:tcPr>
    <w:p>
      <w:pPr>
        <w:spacing w:after="0"/>
        <w:jc w:val="center"/>
        <w:rPr>
{rpr_block}
        </w:rPr>
      </w:pPr>
      <w:r>
        <w:rPr>
{rpr_block}
        </w:rPr>
        <w:t>{project_name}</w:t>
      </w:r>
    </w:p>
  </w:tc>
  <!-- Repeat pattern for Action and Status columns with "Action" and "Status" text -->
</w:tr>
```

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

Renders automatically via numId="{v['num_id']}" — the cell paragraph is empty.

```xml
<w:tc>
  <w:tcPr>
    <w:tcW w:w="{cw[0]}" w:type="dxa"/>
    <w:tcBorders>
      <w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/>
    </w:tcBorders>
  </w:tcPr>
  <w:p>
    <w:pPr>
      <w:pStyle w:val="{v['col1_style']}"/>
      <w:numPr>
        <w:ilvl w:val="0"/>
        <w:numId w:val="{v['num_id']}"/>
      </w:numPr>
      <w:spacing w:line="240" w:lineRule="auto"/>
    </w:pPr>
  </w:p>
</w:tc>
```

---

## Col 2 — Content (list hierarchy)

All levels use numId="{v['num_id']}" from `numbering.xml`. Do not redefine — reference only.

### Level 0 — Topic heading (`{v['col2_style_l0']}`, ilvl=0)

```xml
<w:p>
  <w:pPr>
    <w:pStyle w:val="{v['col2_style_l0']}"/>
    <w:spacing w:line="240" w:lineRule="auto"/>
    <w:rPr><w:szCs w:val="{t_sz}"/><w:lang w:val="{t_lang}"/></w:rPr>
  </w:pPr>
  <w:r>
    <w:rPr><w:szCs w:val="{t_sz}"/><w:lang w:val="{t_lang}"/></w:rPr>
    <w:t>Topic heading text</w:t>
  </w:r>
</w:p>
```

### Level 2 — Numbered sub-items (`{v['col2_style_l2']}`, ilvl=2)

Indent: left {v['l2_left']}, hanging {v['l2_hanging']}.

```xml
<w:p>
  <w:pPr>
    <w:pStyle w:val="{v['col2_style_l2']}"/>
    <w:numPr>
      <w:ilvl w:val="2"/>
      <w:numId w:val="{v['num_id']}"/>
    </w:numPr>
    <w:spacing w:after="240" w:line="240" w:lineRule="auto"/>
    <w:ind w:left="{v['l2_left']}" w:hanging="{v['l2_hanging']}"/>
    <w:rPr><w:bCs w:val="0"/></w:rPr>
  </w:pPr>
  <w:r>
    <w:rPr><w:lang w:val="{t_lang}"/></w:rPr>
    <w:t>Sub-item text here.</w:t>
  </w:r>
</w:p>
```

### Level 3 — Bullet sub-items (`{v['col2_style_l3']}`, ilvl=3)

Indent: left {v['l3_left']}, hanging {v['l3_hanging']}.

```xml
<w:p>
  <w:pPr>
    <w:pStyle w:val="{v['col2_style_l3']}"/>
    <w:numPr>
      <w:ilvl w:val="3"/>
      <w:numId w:val="{v['num_id']}"/>
    </w:numPr>
    <w:spacing w:after="240" w:line="240" w:lineRule="auto"/>
    <w:ind w:left="{v['l3_left']}" w:hanging="{v['l3_hanging']}"/>
    <w:rPr><w:bCs w:val="0"/></w:rPr>
  </w:pPr>
  <w:r>
    <w:rPr><w:lang w:val="{t_lang}"/></w:rPr>
    <w:t>Bullet text here.</w:t>
  </w:r>
</w:p>
```

---

## Col 3 — Action

**HARD RULE: Company or team names only. Never individual person names.**

```xml
<w:tc>
  <w:tcPr>
    <w:tcW w:w="{cw[2]}" w:type="dxa"/>
    <w:tcBorders>
      <w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/>
    </w:tcBorders>
  </w:tcPr>
  <w:p>
    <w:pPr>
      <w:spacing w:after="120"/>
      <w:rPr>
{rpr_plain}
      </w:rPr>
    </w:pPr>
  </w:p>
  <w:p>
    <w:pPr>
      <w:spacing w:after="0"/>
      <w:jc w:val="center"/>
      <w:rPr>
{rpr_plain}
      </w:rPr>
    </w:pPr>
    <w:r>
      <w:rPr>
{rpr_plain}
      </w:rPr>
      <w:t>IBEC</w:t>
    </w:r>
  </w:p>
</w:tc>
```

---

## Col 4 — Status

Same structure as Col 3. Permitted values: `In Progress` / `Pending` / `Completed`. No other values.

---

## Meetings row (final table row)

Row height {v['meetings_row_h']} DXA. **No bottom border on any cell.** Only col 2 has content.

Cols 1, 3, 4: `<w:p><w:pPr><w:spacing w:after="0"/></w:pPr></w:p>`

Col 2:

```xml
<w:p>
  <w:pPr>
    <w:spacing w:after="0" w:line="240" w:lineRule="auto"/>
    <w:rPr>
{rpr_block}
    </w:rPr>
  </w:pPr>
  <w:r>
    <w:rPr>
{rpr_block}
    </w:rPr>
    <w:t>MEETINGS</w:t>
  </w:r>
</w:p>
<w:p>
  <w:pPr>
    <w:spacing w:after="0" w:line="240" w:lineRule="auto"/>
    <w:rPr>
{rpr_block}
    </w:rPr>
  </w:pPr>
  <w:r>
    <w:rPr>
{rpr_block}
    </w:rPr>
    <w:t>The next meeting date is Thursday June 25, 2026.</w:t>
  </w:r>
</w:p>
```
"""


def gen_footer_and_special(v):
    f_font   = v.get('footer_font', 'Times New Roman')
    f_sz     = v.get('footer_sz', '22')
    f_sz_cs  = v.get('footer_sz_cs', f_sz)
    f_lang   = v.get('footer_lang', 'en-GB')
    f_before = v.get('footer_spacing_before', '240')
    org      = v.get('org_name', 'IBEC')
    suffix   = v.get('org_suffix', ' Limited')
    color    = v.get('org_color', '243E6C')

    return f"""# Footer and Special Formatting Reference

## Contents
- Footer paragraph
- Superscript ordinal dates
- Special character escaping
- Common XML pitfalls

---

## Footer paragraph

Placed after `</w:tbl>`, before `<w:sectPr>`. Spacing before {f_before}.

"{org}" is bold, colour `#{color}`. "{suffix.strip()}" is regular weight.
Requires `xml:space="preserve"` on runs with leading/trailing spaces.

```xml
<w:p>
  <w:pPr>
    <w:spacing w:before="{f_before}"/>
    <w:rPr>
      <w:rFonts w:ascii="{f_font}" w:hAnsi="{f_font}"/>
      <w:sz w:val="{f_sz}"/><w:szCs w:val="{f_sz_cs}"/>
      <w:lang w:val="{f_lang}"/>
    </w:rPr>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="{f_font}" w:hAnsi="{f_font}"/>
      <w:sz w:val="{f_sz}"/><w:szCs w:val="{f_sz_cs}"/>
      <w:lang w:val="{f_lang}"/>
    </w:rPr>
    <w:t xml:space="preserve">Prepared by: </w:t>
  </w:r>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="{f_font}" w:hAnsi="{f_font}"/>
      <w:b/><w:bCs/>
      <w:color w:val="{color}"/>
      <w:sz w:val="{f_sz}"/><w:szCs w:val="{f_sz_cs}"/>
      <w:lang w:val="{f_lang}"/>
    </w:rPr>
    <w:t>{org}</w:t>
  </w:r>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="{f_font}" w:hAnsi="{f_font}"/>
      <w:sz w:val="{f_sz}"/><w:szCs w:val="{f_sz_cs}"/>
      <w:lang w:val="{f_lang}"/>
    </w:rPr>
    <w:t xml:space="preserve">{suffix}</w:t>
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
| New numbering definitions | Never — reference existing numId="{v['num_id']}" from `numbering.xml` |
| Modifying header/footer files | Never — leave all `header*.xml`, `footer*.xml`, `word/media/` untouched |
| Using npm `docx` library | Never — template clone + XML edit only |
| Person names in Action column | Never — companies/teams only |
| Status values outside the permitted set | Never — `In Progress`, `Pending`, `Completed` only |
"""


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) != 4:
        print("Usage: setup_docx_renderer.py <source.docx> <project_name> <meeting_notes_dir>")
        sys.exit(1)

    src, project_name, mn_dir = sys.argv[1], sys.argv[2], sys.argv[3]

    if not os.path.isfile(src):
        print(f"ERROR: source file not found: {src}")
        sys.exit(1)

    mn = Path(mn_dir)
    refs_dir = mn / 'skills' / 'docx-renderer' / 'references'
    refs_dir.mkdir(parents=True, exist_ok=True)

    # 1. Blank template
    blank_dst = mn / f'{project_name}_blank_template.docx'
    print(f"Creating blank template...")
    try:
        create_blank_template(src, str(blank_dst))
        print(f"  OK: {blank_dst}")
    except Exception as e:
        print(f"  ERROR: {e}")
        sys.exit(1)

    # 2. Extract values
    print(f"Extracting template values...")
    try:
        vals = extract_values(src)
        for note in vals.get('_log', []):
            print(f"  {note}")
    except Exception as e:
        print(f"  ERROR during extraction: {e}")
        sys.exit(1)

    # 3. Generate reference files
    print(f"Generating reference files...")
    files = {
        'title-and-attendees.md': gen_title_and_attendees(vals, project_name),
        'table-structure.md':     gen_table_structure(vals, project_name),
        'footer-and-special.md':  gen_footer_and_special(vals),
    }
    for fname, content in files.items():
        path = refs_dir / fname
        path.write_text(content, encoding='utf-8')
        print(f"  OK: {path}")

    print(f"\nSetup complete.")
    print(f"  Blank template: {blank_dst}")
    print(f"  Reference files: {refs_dir}/")


if __name__ == '__main__':
    main()
