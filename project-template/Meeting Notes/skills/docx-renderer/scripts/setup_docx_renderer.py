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
  3. Renders the docx-renderer reference files from skills/docx-renderer/templates/,
     substituting the extracted values into the curated prose

This runs ONCE per project. On every later run it finds references/.rendered.json
and exits without touching anything, so hand-edits to the reference files survive.
Pass --force to re-derive everything from a different .docx.

Usage:
    python3 setup_docx_renderer.py <source.docx> <project_name> <meeting_notes_dir> [--force]

Outputs:
    <meeting_notes_dir>/<project_name>_blank_template.docx
    <meeting_notes_dir>/skills/docx-renderer/references/title-and-attendees.md
    <meeting_notes_dir>/skills/docx-renderer/references/table-structure.md
    <meeting_notes_dir>/skills/docx-renderer/references/footer-and-special.md
    <meeting_notes_dir>/skills/docx-renderer/references/.rendered.json
"""

import sys
import os
import re
import json
import datetime
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

# Neutral fallback for the "Prepared by" brand colour. Overwritten by extraction
# from the uploaded branded template; a real brand hex must never be the default.
FALLBACK_ORG_COLOR = '000000'


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
    # Fallbacks only. The loop below overwrites all three from the uploaded
    # branded template's "Prepared by" paragraph. Never put a real client's brand
    # colour here — if extraction fails, a neutral value must surface the problem
    # rather than quietly stamping another client's navy on the document.
    v['org_name']              = 'IBEC'
    v['org_suffix']            = ' Limited'
    v['org_color']             = FALLBACK_ORG_COLOR
    v['org_color_extracted']   = False

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
                v['org_color_extracted'] = True
                if text:
                    v['org_name'] = text
            elif not rv.get('bold') and text and 'Prepared' not in text and text != v['org_name']:
                v['org_suffix'] = text_raw  # preserve leading space, e.g. " Limited"
        log.append(f"✓ Footer: org={v['org_name']}{v['org_suffix']}, color=#{v['org_color']}, sz={v['footer_sz']}")
        if not v.get('org_color_extracted'):
            log.append("⚠ Footer brand colour was NOT extracted from the template — "
                       f"falling back to #{FALLBACK_ORG_COLOR}. Check the source .docx has a "
                       "\"Prepared by\" paragraph, or set the colour by hand.")
        break

    v['_log'] = log
    return v


# ── Reference file rendering ──────────────────────────────────────────────────

TEMPLATE_NAMES = [
    'title-and-attendees.md',
    'table-structure.md',
    'footer-and-special.md',
]

TOKEN_RE = re.compile(r'\{\{([a-z0-9_]+)\}\}')

# Values extracted from the source .docx are parsed XML — "&amp;" has already become
# "&". Re-emitting them into the XML examples in the reference files needs them escaped
# again, or the pattern the renderer copies is malformed. Tokens used inside ```xml
# blocks are the _xml variants; the bare token stays readable for prose.
XML_TEXT_TOKENS = ['project_name', 'org_name', 'org_suffix',
                   'att_font', 'tbl_font', 'footer_font']

DEFAULT_DATE_FORMAT = 'Thursday June 18, 2026'


def xml_escape(text):
    """Escape for both XML text nodes and double-quoted attribute values."""
    return (str(text).replace('&', '&amp;')
                     .replace('<', '&lt;')
                     .replace('>', '&gt;')
                     .replace('"', '&quot;'))


def build_tokens(v, project_name, src_path, date_format=None):
    """Flatten extracted values into the flat {{token}} vocabulary the templates use."""
    cw = v.get('col_widths') or ['490', '5696', '2050', '1479']
    while len(cw) < 4:
        cw.append('0')

    tokens = {k: str(val) for k, val in v.items()
              if not k.startswith('_') and not isinstance(val, (list, dict, bool))}

    tokens.update({
        'project_name':  project_name,
        'source_docx':   os.path.basename(src_path),
        'rendered_on':   datetime.date.today().isoformat(),
        'col1_w':        cw[0],
        'col2_w':        cw[1],
        'col3_w':        cw[2],
        'col4_w':        cw[3],
        'title_pg_tag':  '<w:titlePg/>' if v.get('title_pg') else '',
        'date_format':   date_format or DEFAULT_DATE_FORMAT,
    })

    # XML-safe twins for every token that appears inside an ```xml block.
    for key in XML_TEXT_TOKENS:
        tokens[key + '_xml'] = xml_escape(tokens.get(key, ''))

    if v.get('org_color_extracted'):
        tokens['org_color_warning'] = (
            f"Brand colour `#{v['org_color']}` was read from the template's "
            '"Prepared by" paragraph.'
        )
    else:
        tokens['org_color_warning'] = (
            f"> **Warning:** the brand colour was NOT found in the source template — "
            f"`#{v.get('org_color', FALLBACK_ORG_COLOR)}` is a neutral fallback. "
            'Set it by hand, or re-run setup against a .docx that has a "Prepared by" paragraph.'
        )

    return tokens


def render_template(text, tokens, template_name):
    """Substitute {{token}} placeholders. Unknown tokens are a hard error."""
    unknown = sorted({m.group(1) for m in TOKEN_RE.finditer(text)} - set(tokens))
    if unknown:
        raise ValueError(
            f"{template_name}: template uses unknown token(s): {', '.join(unknown)}. "
            "Add them to build_tokens() or fix the template."
        )
    rendered = TOKEN_RE.sub(lambda m: tokens[m.group(1)], text)
    leftover = TOKEN_RE.search(rendered)
    if leftover:
        raise ValueError(f"{template_name}: unresolved token {leftover.group(0)} after render")
    return rendered


# ── Main ──────────────────────────────────────────────────────────────────────

USAGE = (
    "Usage: setup_docx_renderer.py <source.docx> <project_name> <meeting_notes_dir>\n"
    "                              [--force] [--date-format \"<example date>\"]\n"
    "\n"
    "Renders the docx-renderer reference files and blank template from a branded .docx.\n"
    "Runs once: a later run is a no-op unless --force is given.\n"
    "\n"
    "  --date-format  The project's header date convention, written as a literal example\n"
    "                 (e.g. \"Monday 22 June 2026\"). Must match the date rule in the style\n"
    "                 skill's typography.md. Defaults to \"" + DEFAULT_DATE_FORMAT + "\"."
)


def main():
    argv = sys.argv[1:]
    force = '--force' in argv

    date_format = None
    if '--date-format' in argv:
        i = argv.index('--date-format')
        if i + 1 >= len(argv):
            print("ERROR: --date-format needs a value")
            sys.exit(1)
        date_format = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]

    args = [a for a in argv if a != '--force']

    if len(args) != 3:
        print(USAGE)
        sys.exit(1)

    src, project_name, mn_dir = args

    if not os.path.isfile(src):
        print(f"ERROR: source file not found: {src}")
        sys.exit(1)

    mn = Path(mn_dir)
    skill_dir = mn / 'skills' / 'docx-renderer'
    refs_dir = skill_dir / 'references'
    tpl_dir = skill_dir / 'templates'
    marker = refs_dir / '.rendered.json'

    if not tpl_dir.is_dir():
        print(f"ERROR: template directory not found: {tpl_dir}")
        sys.exit(1)

    refs_dir.mkdir(parents=True, exist_ok=True)

    # Already set up? Leave everything alone unless --force.
    if marker.is_file() and not force:
        try:
            prev = json.loads(marker.read_text(encoding='utf-8'))
        except Exception:
            prev = {}
        print("Setup has already run for this project — nothing was changed.")
        print(f"  Rendered on : {prev.get('rendered_on', 'unknown')}")
        print(f"  From source : {prev.get('source_docx', 'unknown')}")
        print("")
        print("  To change a value, edit the file in references/ directly.")
        print("  To re-derive everything from a different .docx, re-run with --force.")
        sys.exit(0)

    # No marker means setup has never completed here, so the reference files present
    # are the shipped placeholders and MUST be replaced. The marker — not the presence
    # of a file — is what makes a later run a no-op.
    replaced_blank = (mn / f'{project_name}_blank_template.docx').is_file()

    # 1. Blank template
    blank_dst = mn / f'{project_name}_blank_template.docx'
    print("Creating blank template...")
    try:
        create_blank_template(src, str(blank_dst))
        print(f"  OK: {blank_dst}" + ("  (replaced existing)" if replaced_blank else ""))
    except Exception as e:
        print(f"  ERROR: {e}")
        sys.exit(1)

    # 2. Extract values
    print("Extracting template values...")
    try:
        vals = extract_values(src)
        for note in vals.get('_log', []):
            print(f"  {note}")
    except Exception as e:
        print(f"  ERROR during extraction: {e}")
        sys.exit(1)

    tokens = build_tokens(vals, project_name, src, date_format)

    # 3. Render reference files from templates
    print("Rendering reference files...")
    rendered = []
    for fname in TEMPLATE_NAMES:
        tpl_path = tpl_dir / fname
        out_path = refs_dir / fname

        if not tpl_path.is_file():
            print(f"  ERROR: template not found: {tpl_path}")
            sys.exit(1)

        try:
            content = render_template(tpl_path.read_text(encoding='utf-8'), tokens, fname)
        except ValueError as e:
            print(f"  ERROR: {e}")
            sys.exit(1)

        out_path.write_text(content, encoding='utf-8')
        print(f"  OK: {out_path}")
        rendered.append(fname)

    # 4. Marker — makes the next run a no-op
    marker.write_text(json.dumps({
        'project_name': project_name,
        'source_docx':  os.path.basename(src),
        'rendered_on':  datetime.date.today().isoformat(),
        'date_format':  tokens['date_format'],
        'rendered':     rendered,
    }, indent=2) + '\n', encoding='utf-8')

    print("\nSetup complete.")
    print(f"  Blank template : {blank_dst}")
    print(f"  Reference files: {refs_dir}/")
    print("\n  These files are now yours. Setup will not rewrite them.")
    print("  Edit them directly to change anything, or re-run with --force to re-derive.")


if __name__ == '__main__':
    main()
