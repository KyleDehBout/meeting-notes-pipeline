"""Deterministically repair a rendered .docx before falling back to an LLM retry.

Run between a failed validate.py and a re-render. Every repair here is mechanical:
it fixes a known renderer failure mode without deciding anything about content.
If a repair cannot be applied safely it is skipped and reported, never guessed at.

Usage:
    python repair.py <file.docx> [--log <path>]

Exit codes: 0 = file is now valid (or was already), 1 = still broken after repair.
"""
import re
import shutil
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
ET.register_namespace('w', W_NS)
LEADING_NUMBER_RE = re.compile(r'^\d+(\.\d+)*\.?\s+')
# Styles that leak in when content is pasted out of a chat UI into Word.
FOREIGN_STYLE_RE = re.compile(r'^font-claude|^claude-', re.I)


def w(tag):
    return f'{{{W_NS}}}{tag}'


def para_text(p):
    return ''.join(t.text or '' for t in p.findall(f'.//{w("t")}'))


def repair_typed_numbers(body, fixes):
    """'1.1.1 Foo' typed as literal text -> strip the number, keep the text.

    Word supplies the number from numPr. Only strips when the paragraph already
    has a numPr to supply it, so text never silently loses its numbering.
    """
    for p in body.iter(w('p')):
        runs = p.findall(f'.//{w("t")}')
        if not runs:
            continue
        text = para_text(p)
        m = LEADING_NUMBER_RE.match(text)
        if not m:
            continue
        if p.find(f'./{w("pPr")}/{w("numPr")}') is None:
            fixes.append(f"SKIP typed-number {text[:40]!r}: no numPr to supply the number")
            continue
        first = runs[0]
        stripped = (first.text or '')[m.end():] if len(first.text or '') >= m.end() else ''
        if not (first.text or '').startswith(m.group(0)):
            fixes.append(f"SKIP typed-number {text[:40]!r}: number spans multiple runs")
            continue
        first.text = stripped
        fixes.append(f"typed-number stripped: {text[:40]!r}")


def repair_foreign_styles(body, fallback, fixes):
    """Remap chat-UI styles pasted into Word onto the document's own list style."""
    if not fallback:
        return
    for p in body.iter(w('p')):
        ref = p.find(f'./{w("pPr")}/{w("pStyle")}')
        if ref is None:
            continue
        val = ref.get(w('val')) or ''
        if FOREIGN_STYLE_RE.match(val):
            ref.set(w('val'), fallback)
            fixes.append(f"foreign style {val!r} -> {fallback!r}: {para_text(p)[:40]!r}")


def repair_orphan_numbering(body, live_id, fixes):
    """numPr pointing at numId=0 everywhere = numbering never linked. Relink to a live list.

    Only fires when NO paragraph in the document has a live numId — i.e. wholesale
    failure. A numId=0 alongside working numbering is intentional suppression
    (both house styles use it for the bold section title) and is left alone.
    """
    suppressed, numbered = [], 0
    for p in body.iter(w('p')):
        numId = p.find(f'./{w("pPr")}/{w("numPr")}/{w("numId")}')
        if numId is None:
            continue
        if numId.get(w('val')) == '0':
            if para_text(p).strip():
                suppressed.append(numId)
        else:
            numbered += 1

    if numbered or not suppressed:
        return
    if not live_id:
        fixes.append("SKIP orphan-numbering: no live numId found in numbering.xml")
        return
    for numId in suppressed:
        numId.set(w('val'), live_id)
    fixes.append(f"orphan numbering relinked to numId={live_id} ({len(suppressed)} paragraphs)")


def live_num_id(parts):
    """Lowest numId declared in numbering.xml, used as the relink target."""
    xml = parts.get('word/numbering.xml')
    if not xml:
        return None
    ids = [int(n) for n in re.findall(r'<w:num w:numId="(\d+)"', xml.decode('utf-8', 'ignore'))]
    return str(min(ids)) if ids else None


def list_style(parts):
    """A list paragraph style declared in styles.xml, as the remap target."""
    xml = parts.get('word/styles.xml')
    if not xml:
        return None
    ids = re.findall(r'w:styleId="([^"]+)"', xml.decode('utf-8', 'ignore'))
    for want in ('1.1List', '11List', '1.0List', '10List', 'ListParagraph'):
        for sid in ids:
            if sid.replace(' ', '') == want:
                return sid
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: repair.py <file.docx> [--log <path>]")
        sys.exit(2)

    path = Path(sys.argv[1])
    log_path = None
    if '--log' in sys.argv:
        log_path = Path(sys.argv[sys.argv.index('--log') + 1])

    with zipfile.ZipFile(path) as z:
        parts = {n: z.read(n) for n in z.namelist()}

    root = ET.fromstring(parts['word/document.xml'])
    body = root.find(f'.//{w("body")}')

    fixes = []
    repair_typed_numbers(body, fixes)
    repair_foreign_styles(body, list_style(parts), fixes)
    repair_orphan_numbering(body, live_num_id(parts), fixes)

    applied = [f for f in fixes if not f.startswith('SKIP')]
    if applied:
        shutil.copy2(path, path.with_suffix('.pre-repair.docx'))
        parts['word/document.xml'] = ET.tostring(root, encoding='UTF-8', xml_declaration=True)
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as o:
            for name, blob in parts.items():
                o.writestr(name, blob)

    for f in fixes:
        print(f)
    if not fixes:
        print("no repairs needed")

    if log_path:
        stamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')
        line = f"{stamp}\t{path.name}\t{len(applied)} applied\t{'; '.join(fixes) or 'none'}\n"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, 'a') as fh:
            fh.write(line)

    sys.exit(0 if applied or not fixes else 1)


if __name__ == "__main__":
    main()
