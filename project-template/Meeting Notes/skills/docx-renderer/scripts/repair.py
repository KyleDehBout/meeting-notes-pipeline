"""Deterministically repair a rendered .docx before falling back to an LLM retry.

Run between a failed validate.py and a re-render. Every repair here is mechanical:
it fixes a known renderer failure mode without deciding anything about content.
If a repair cannot be applied safely it is skipped and reported, never guessed at.

Usage:
    python3 repair.py <file.docx> [--restyle] [--log <path>]

    --restyle   Also remap chat-UI paragraph styles (font-claude-*, claude-*) onto the
                document's own list style. OFF by default: a document can carry those
                styles legitimately, and remapping them changes formatting nobody asked
                to change. Turn it on only when that is the failure you are repairing.

Exit codes: 0 = validate.py now passes, 1 = still invalid, 2 = bad usage / unreadable file.

The exit code reflects a real validate.py run, not merely whether a repair was applied.
"""
import re
import shutil
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
ET.register_namespace('w', W_NS)

# A typed list number is hierarchical ("1.1", "1.2.3") or a single number with a
# trailing dot ("1."). A bare leading integer is NOT one: "2025 budget approved",
# "48 hours notice" and "3 units delivered" are ordinary sentences, and stripping
# their first token silently deletes content from an issued document.
LEADING_NUMBER_RE = re.compile(r'^(\d+(?:\.\d+)+\.?|\d+\.)\s+')

# Styles that leak in when content is pasted out of a chat UI into Word.
FOREIGN_STYLE_RE = re.compile(r'^font-claude|^claude-', re.I)

# The root element's opening tag, captured verbatim so every namespace declaration
# survives the round-trip (see reserialise()).
ROOT_TAG_RE = re.compile(rb'<(?:[A-Za-z0-9_.-]+:)?document\b[^>]*>')


XMLNS_RE = re.compile(rb'xmlns:([A-Za-z0-9_.-]+)="([^"]*)"')


def register_source_namespaces(original_xml):
    """Teach ElementTree every prefix the source declares, before parsing.

    Without this, ET invents ns1:/ns2:/ns3: for prefixes it does not know (w14, wp14,
    the mc:* family). Those invented prefixes are declared on the root tag ET
    generates — which reserialise() then replaces with the original — leaving them
    unbound. Registering up front keeps the document's own prefixes end to end.
    """
    tag = ROOT_TAG_RE.search(original_xml)
    if not tag:
        return
    for prefix, uri in XMLNS_RE.findall(tag.group(0)):
        try:
            ET.register_namespace(prefix.decode('ascii'), uri.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            continue


def w(tag):
    return f'{{{W_NS}}}{tag}'


def para_text(p):
    return ''.join(t.text or '' for t in p.findall(f'.//{w("t")}'))


def numbering_depth(p):
    """ilvl of the paragraph's numPr, or None when it has no numbering."""
    ilvl = p.find(f'./{w("pPr")}/{w("numPr")}/{w("ilvl")}')
    if ilvl is None:
        return None
    try:
        return int(ilvl.get(w('val')))
    except (TypeError, ValueError):
        return None


def repair_typed_numbers(body, fixes):
    """'1.1.1 Foo' typed as literal text -> strip the number, keep the text.

    Word supplies the number from numPr. Three guards, all of which must pass:
      1. the text opens with a hierarchical number, not a bare integer
      2. the paragraph has a numPr to supply the number instead
      3. the typed depth matches the paragraph's ilvl, so we only remove a number
         Word is about to reprint identically
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

        depth = numbering_depth(p)
        segments = len(m.group(1).rstrip('.').split('.'))
        if depth is None:
            fixes.append(f"SKIP typed-number {text[:40]!r}: numPr has no readable ilvl")
            continue
        if segments != depth + 1:
            fixes.append(
                f"SKIP typed-number {text[:40]!r}: typed {segments} level(s) but ilvl={depth} "
                f"expects {depth + 1} — not a duplicate of Word's number"
            )
            continue

        first = runs[0]
        if not (first.text or '').startswith(m.group(0)):
            fixes.append(f"SKIP typed-number {text[:40]!r}: number spans multiple runs")
            continue
        first.text = (first.text or '')[m.end():]
        fixes.append(f"typed-number stripped: {text[:40]!r}")


def repair_foreign_styles(body, fallback, fixes):
    """Remap chat-UI styles pasted into Word onto the document's own list style."""
    if not fallback:
        fixes.append("SKIP foreign-styles: no list style found in styles.xml")
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


def reserialise(root, original_xml):
    """Serialise the tree, restoring the root tag exactly as the source declared it.

    ET.tostring only re-emits namespaces it can see in use, which silently drops the
    30-odd declarations a real Word document carries. The prefixes listed in
    mc:Ignorable then reference undeclared namespaces: still well-formed XML, still
    accepted by validate.py, and unreadable in Word. Splicing the original opening
    tag back over the serialised one preserves every declaration and mc:Ignorable.
    """
    out = ET.tostring(root, encoding='UTF-8', xml_declaration=True)
    orig_tag = ROOT_TAG_RE.search(original_xml)
    new_tag = ROOT_TAG_RE.search(out)
    if not orig_tag or not new_tag:
        raise ValueError("could not locate the document root tag — refusing to rewrite")
    return out[:new_tag.start()] + orig_tag.group(0) + out[new_tag.end():]


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


def run_validator(path):
    """Re-run validate.py so the exit code means what the docstring says it means.

    Returns (code, detail). code 0 = valid. If the validator is missing we cannot
    claim the file is valid, so this reports that rather than assuming success.
    """
    validator = Path(__file__).resolve().parent / 'validate.py'
    if not validator.is_file():
        return None, f"validate.py not found beside repair.py ({validator})"
    try:
        p = subprocess.run([sys.executable, str(validator), str(path)],
                           capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return None, f"could not run validate.py: {e}"
    return p.returncode, (p.stdout + p.stderr).strip()


def main():
    argv = sys.argv[1:]
    restyle = '--restyle' in argv
    argv = [a for a in argv if a != '--restyle']

    log_path = None
    if '--log' in argv:
        i = argv.index('--log')
        if i + 1 >= len(argv):
            print("ERROR: --log needs a path")
            sys.exit(2)
        log_path = Path(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]

    if len(argv) != 1:
        print("Usage: repair.py <file.docx> [--restyle] [--log <path>]")
        sys.exit(2)

    path = Path(argv[0])
    if not path.is_file():
        print(f"ERROR: file not found: {path}")
        sys.exit(2)

    try:
        with zipfile.ZipFile(path) as z:
            parts = {n: z.read(n) for n in z.namelist()}
    except (zipfile.BadZipFile, OSError) as e:
        print(f"ERROR: cannot read {path.name} as a .docx: {e}")
        sys.exit(2)

    if 'word/document.xml' not in parts:
        print(f"ERROR: {path.name} has no word/document.xml — not a Word document")
        sys.exit(2)

    original_xml = parts['word/document.xml']
    register_source_namespaces(original_xml)
    try:
        root = ET.fromstring(original_xml)
    except ET.ParseError as e:
        print(f"ERROR: word/document.xml is not valid XML: {e}")
        sys.exit(2)

    body = root.find(f'.//{w("body")}')
    if body is None:
        print(f"ERROR: {path.name} has no <w:body> — nothing to repair")
        sys.exit(2)

    fixes = []
    repair_typed_numbers(body, fixes)
    if restyle:
        repair_foreign_styles(body, list_style(parts), fixes)
    repair_orphan_numbering(body, live_num_id(parts), fixes)

    applied = [f for f in fixes if not f.startswith('SKIP')]
    if applied:
        try:
            rewritten = reserialise(root, original_xml)
        except ValueError as e:
            print(f"ERROR: {e}")
            sys.exit(2)
        shutil.copy2(path, path.with_suffix('.pre-repair.docx'))
        parts['word/document.xml'] = rewritten
        try:
            with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as o:
                for name, blob in parts.items():
                    o.writestr(name, blob)
        except OSError as e:
            print(f"ERROR: could not write {path.name}: {e}")
            sys.exit(2)

    # Bounded output: the full list goes to --log, never to the caller's context.
    CAP = 5
    if not fixes:
        print("no repairs needed")
    else:
        for f in fixes[:CAP]:
            print(f)
        if len(fixes) > CAP:
            print(f"... and {len(fixes) - CAP} more ({len(applied)} applied in total)"
                  + (f" — full list in {log_path}" if log_path else ""))

    code, detail = run_validator(path)
    if code is None:
        print(f"WARNING: {detail}")
        print("Cannot confirm the file is valid — run validate.py yourself before using it.")
    elif code == 0:
        print("validate.py: OK")
    else:
        print(f"validate.py: still invalid — {detail.splitlines()[0] if detail else 'no detail'}")

    if log_path:
        stamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')
        line = f"{stamp}\t{path.name}\t{len(applied)} applied\t{'; '.join(fixes) or 'none'}\n"
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, 'a') as fh:
                fh.write(line)
        except OSError as e:
            print(f"WARNING: could not write log {log_path}: {e}")

    sys.exit(0 if code == 0 else 1)


if __name__ == "__main__":
    main()
