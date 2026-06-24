"""
Create a blank .docx template by stripping body content from a branded source file.

The source file's headers, footers, media, styles, and sectPr are preserved.
Only the <w:body> content paragraphs are removed — the sectPr (which holds
header/footer relationships) is kept so branding carries through every render.

Usage:
    python create_blank_template.py <source.docx> <output_blank_template.docx>
"""
import sys
import zipfile
import os


def strip_body_content(doc_xml_bytes):
    content = doc_xml_bytes.decode('utf-8')

    body_close = content.rfind('</w:body>')
    if body_close == -1:
        raise ValueError("No </w:body> found in document.xml")

    sect_start = content.rfind('<w:sectPr', 0, body_close)
    if sect_start == -1:
        raise ValueError("No <w:sectPr found — cannot preserve header/footer references")

    sect_block = content[sect_start:body_close]

    body_open = content.find('<w:body>')
    if body_open == -1:
        body_open = content.find('<w:body ')
        if body_open == -1:
            raise ValueError("No <w:body found in document.xml")
        body_tag_end = content.find('>', body_open) + 1
    else:
        body_tag_end = body_open + len('<w:body>')

    # Word requires at least one paragraph before sectPr
    empty_para = '<w:p><w:pPr><w:rPr/></w:pPr></w:p>'

    new_content = (
        content[:body_tag_end] +
        empty_para +
        sect_block +
        content[body_close:]
    )

    return new_content.encode('utf-8')


def main():
    if len(sys.argv) != 3:
        print("Usage: create_blank_template.py <source.docx> <output_blank.docx>")
        sys.exit(1)

    src, dst = sys.argv[1], sys.argv[2]

    if not os.path.isfile(src):
        print(f"ERROR: source file not found: {src}")
        sys.exit(1)

    try:
        with zipfile.ZipFile(src, 'r') as zin:
            names = zin.namelist()
            if 'word/document.xml' not in names:
                print("ERROR: source file does not contain word/document.xml — is it a valid .docx?")
                sys.exit(1)

            with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
                for name in names:
                    data = zin.read(name)
                    if name == 'word/document.xml':
                        data = strip_body_content(data)
                    zout.writestr(name, data)

    except zipfile.BadZipFile:
        print(f"ERROR: source file is not a valid zip/docx: {src}")
        sys.exit(1)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # Verify output
    try:
        with zipfile.ZipFile(dst) as z:
            bad = z.testzip()
            if bad:
                print(f"FAIL: output file is corrupt: {bad}")
                sys.exit(1)
    except Exception as e:
        print(f"FAIL: could not verify output: {e}")
        sys.exit(1)

    print(f"OK: blank template created at {dst} ({len(names)} files preserved)")


if __name__ == "__main__":
    main()
