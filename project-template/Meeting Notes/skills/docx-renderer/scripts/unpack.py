"""Unpack a .docx file into a target directory."""
import sys
import zipfile
import os


def main():
    if len(sys.argv) != 3:
        print("Usage: unpack.py <input.docx> <output_dir>")
        sys.exit(1)

    src, dst = sys.argv[1], sys.argv[2]

    if not os.path.isfile(src):
        print(f"ERROR: file not found: {src}")
        sys.exit(1)

    try:
        with zipfile.ZipFile(src, 'r') as z:
            bad = z.testzip()
            if bad:
                print(f"ERROR: corrupt zip entry: {bad}")
                sys.exit(1)
            z.extractall(dst)
    except zipfile.BadZipFile as e:
        print(f"ERROR: not a valid zip/docx: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print(f"OK: unpacked to {dst}")


if __name__ == "__main__":
    main()
