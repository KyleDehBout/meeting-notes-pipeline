"""Validate a .docx file: zip integrity, document.xml presence, XML parse, and numbering.

Numbering check rationale
-------------------------
`numId="0"` on a paragraph that has text is NOT an error on its own. It is how Word
suppresses numbering on a paragraph that still carries a list style, and both project
house styles rely on that for the bold section title (OIS sets numId="0" explicitly,
LP2 omits numPr entirely). Flagging it rejected every valid OIS document.

What is a real failure is numbering that never got linked at all — the renderer emitted
numPr everywhere but no paragraph points at a live list. That is checked document-wide.
A leading typed number ("1.1.1 ...") is always a failure: the renderer faked numbering
as literal text instead of using numPr/numId.
"""
import re
import sys
import zipfile
import xml.etree.ElementTree as ET


REQUIRED_FILES = ['word/document.xml', '[Content_Types].xml']
W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
LEADING_NUMBER_RE = re.compile(r'^\d+(\.\d+)*\.?\s')


def w(tag):
    return f'{{{W_NS}}}{tag}'


def main():
    if len(sys.argv) != 2:
        print("Usage: validate.py <file.docx>")
        sys.exit(1)

    path = sys.argv[1]

    try:
        with zipfile.ZipFile(path, 'r') as z:
            bad = z.testzip()
            if bad:
                print(f"FAIL: corrupt zip entry: {bad}")
                sys.exit(1)

            names = z.namelist()
            for req in REQUIRED_FILES:
                if req not in names:
                    print(f"FAIL: missing required file: {req}")
                    sys.exit(1)

            try:
                root = ET.fromstring(z.read('word/document.xml'))
            except ET.ParseError as e:
                print(f"FAIL: document.xml is not valid XML: {e}")
                sys.exit(1)

            body = root.find(f'.//{w("body")}')
            if body is None:
                print("FAIL: <w:body> not found in document.xml")
                sys.exit(1)

            if body.find(w('sectPr')) is None:
                print("FAIL: <w:sectPr> not found in <w:body> — header/footer references will be lost")
                sys.exit(1)

            numbered = 0
            suppressed = 0

            for p in body.iter(w('p')):
                text = ''.join(t.text or '' for t in p.findall(f'.//{w("t")}'))

                if LEADING_NUMBER_RE.match(text):
                    print(f"FAIL: paragraph text starts with a typed number instead of "
                          f"relying on numId/ilvl: {text[:60]!r}")
                    sys.exit(1)

                numId = p.find(f'./{w("pPr")}/{w("numPr")}/{w("numId")}')
                if numId is None:
                    continue
                if numId.get(w('val')) == '0':
                    if text.strip():
                        suppressed += 1
                else:
                    numbered += 1

            # Wholesale failure: numPr was emitted but nothing points at a live list.
            if suppressed and not numbered:
                print(f"FAIL: {suppressed} paragraph(s) carry numPr but no paragraph in the "
                      f"document is linked to an active list — numbering was never wired up")
                sys.exit(1)

            # Structural check: one numbered row per section, not per sub-item.
            #
            # The house format puts a whole section in ONE table row: column 1 carries
            # the section counter (a live numId at ilvl 0) and column 2 opens with the
            # section title, which suppresses its own number with numId="0" at ilvl 0.
            # Sub-items live in that same row at ilvl 1+.
            #
            # A renderer that emits one row per sub-item advances the section counter on
            # every row, so headings lose their number and sub-items render with a zero
            # in the middle ("3.0.1"). That shows up here as counter rows with no section
            # title behind them.
            orphans = []
            for tr in body.iter(w('tr')):
                cells = tr.findall(w('tc'))
                if len(cells) < 2:
                    continue

                has_counter = any(
                    num.get(w('val')) != '0'
                    and (lvl is None or lvl.get(w('val')) == '0')
                    for p in cells[0].findall(w('p'))
                    for num in [p.find(f'./{w("pPr")}/{w("numPr")}/{w("numId")}')]
                    if num is not None
                    for lvl in [p.find(f'./{w("pPr")}/{w("numPr")}/{w("ilvl")}')]
                )
                if not has_counter:
                    continue

                title = None
                for p in cells[1].findall(w('p')):
                    num = p.find(f'./{w("pPr")}/{w("numPr")}/{w("numId")}')
                    lvl = p.find(f'./{w("pPr")}/{w("numPr")}/{w("ilvl")}')
                    if num is None or num.get(w('val')) != '0':
                        continue
                    if lvl is not None and lvl.get(w('val')) != '0':
                        continue
                    text = ''.join(t.text or '' for t in p.findall(f'.//{w("t")}')).strip()
                    if text:
                        title = text
                        break
                if title is None:
                    first = ''.join(
                        t.text or '' for t in cells[1].findall(f'.//{w("t")}')).strip()
                    orphans.append(first[:50] or '(empty)')

            if orphans:
                print(f"FAIL: {len(orphans)} table row(s) advance the section counter but "
                      f"contain no section title — the renderer is emitting one row per "
                      f"sub-item instead of one row per section. First offenders: "
                      f"{orphans[:3]}")
                sys.exit(1)

    except zipfile.BadZipFile as e:
        print(f"FAIL: not a valid zip/docx: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"FAIL: file not found: {path}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    print("OK")


if __name__ == "__main__":
    main()
