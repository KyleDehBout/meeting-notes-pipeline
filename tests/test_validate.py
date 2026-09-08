"""Golden-fixture tests for the docx-renderer validator.

The fixtures are real issued One Ironshore documents. They define the house
format: the validator must accept them and reject output that departs from it.

Run:  python3 tests/test_validate.py
Override the fixture location with OIS_MEETING_NOTES if the project moves.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
VALIDATE = os.path.join(
    HERE, os.pardir, 'project-template', 'Meeting Notes',
    'skills', 'docx-renderer', 'scripts', 'validate.py')

NOTES = os.environ.get(
    'OIS_MEETING_NOTES',
    '/Users/kylefreeman/Desktop/IBEC AI-BRAIN/IBEC LTD/One Ironshore/Meeting Notes')
ARCHIVE = os.path.join(NOTES, 'Archive')
OUTPUT = os.path.join(NOTES, 'output')

GOLDEN = [
    'One Ironshore - Site Meeting Notes #13.docx',
    'One Ironshore - Site Meeting Notes #14.docx',
]
BAD_OUTPUT = 'OIS-Meeting-Notes-2026-09-03.docx'

failures = []


def run(path):
    p = subprocess.run([sys.executable, VALIDATE, path],
                       capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def check(name, condition, detail=''):
    if condition:
        print('  pass  %s' % name)
    else:
        print('  FAIL  %s\n        %s' % (name, detail))
        failures.append(name)


def test_accepts_issued_documents():
    """Every issued document is by definition valid house format."""
    for fname in GOLDEN:
        path = os.path.join(ARCHIVE, fname)
        code, out = run(path)
        check('accepts %s' % fname, code == 0, out)


def test_rejects_row_per_item_output():
    """The 2026-09-03 output puts every sub-item on its own numbered row,
    so its section counter fires 25 times with no section heading behind it."""
    path = os.path.join(OUTPUT, BAD_OUTPUT)
    code, out = run(path)
    check('rejects %s' % BAD_OUTPUT, code != 0,
          'expected non-zero exit, got 0')


def test_rejects_literal_typed_numbering():
    """Regression: a typed '1.1 ' prefix must still be caught."""
    src = os.path.join(ARCHIVE, GOLDEN[-1])
    tmp = tempfile.mkdtemp()
    try:
        dst = os.path.join(tmp, 'typed-number.docx')
        with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, 'w') as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == 'word/document.xml':
                    data = data.replace(
                        b'<w:t>Design</w:t>', b'<w:t>1.1 Design</w:t>', 1)
                zout.writestr(item, data)
        code, out = run(dst)
        check('rejects literal typed numbering', code != 0,
              'expected non-zero exit, got 0')
    finally:
        shutil.rmtree(tmp)


if __name__ == '__main__':
    print('validator: %s' % os.path.normpath(VALIDATE))
    print('fixtures : %s\n' % NOTES)
    test_accepts_issued_documents()
    test_rejects_row_per_item_output()
    test_rejects_literal_typed_numbering()
    print('\n%d failure(s)' % len(failures))
    sys.exit(1 if failures else 0)
