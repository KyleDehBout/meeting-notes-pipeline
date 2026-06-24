"""Validate a .docx file: checks zip integrity, document.xml presence, and XML parse."""
import sys
import zipfile
import xml.etree.ElementTree as ET


REQUIRED_FILES = ['word/document.xml', '[Content_Types].xml']
W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'


def main():
    if len(sys.argv) != 2:
        print("Usage: validate.py <file.docx>")
        sys.exit(1)

    path = sys.argv[1]

    try:
        with zipfile.ZipFile(path, 'r') as z:
            # Check zip integrity
            bad = z.testzip()
            if bad:
                print(f"FAIL: corrupt zip entry: {bad}")
                sys.exit(1)

            names = z.namelist()

            # Check required files exist
            for req in REQUIRED_FILES:
                if req not in names:
                    print(f"FAIL: missing required file: {req}")
                    sys.exit(1)

            # Parse document.xml as XML
            try:
                doc_xml = z.read('word/document.xml')
                root = ET.fromstring(doc_xml)
            except ET.ParseError as e:
                print(f"FAIL: document.xml is not valid XML: {e}")
                sys.exit(1)

            # Check <w:body> is present
            body = root.find(f'.//{{{W_NS}}}body')
            if body is None:
                print("FAIL: <w:body> not found in document.xml")
                sys.exit(1)

            # Check <w:sectPr> is present (required for headers/footers)
            sect = body.find(f'{{{W_NS}}}sectPr')
            if sect is None:
                print("FAIL: <w:sectPr> not found in <w:body> — header/footer references will be lost")
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
