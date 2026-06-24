"""Repack an unpacked .docx directory back into a .docx file."""
import sys
import zipfile
import os


def main():
    if len(sys.argv) != 3:
        print("Usage: repack.py <source_dir> <output.docx>")
        sys.exit(1)

    src_dir, dst = sys.argv[1], sys.argv[2]

    if not os.path.isdir(src_dir):
        print(f"ERROR: directory not found: {src_dir}")
        sys.exit(1)

    try:
        with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
            for root, _, files in os.walk(src_dir):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    arcname = os.path.relpath(fpath, src_dir)
                    zout.write(fpath, arcname)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print(f"OK: repacked to {dst}")


if __name__ == "__main__":
    main()
