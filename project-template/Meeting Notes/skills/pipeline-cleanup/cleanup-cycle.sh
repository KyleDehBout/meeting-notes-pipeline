#!/bin/bash
# Clears the meeting-notes pipeline folders after a /learn cycle.
#
# Usage: cleanup-cycle.sh "<archived filename>" [--archive <dir>] [--dry-run]
#
#   <archived filename>  Bare filename of the set of notes just moved into the
#                        issued archive, e.g. "Acme - Meeting Notes #15.docx".
#   --archive <dir>      Issued archive directory. Defaults to <Meeting Notes>/Archive.
#                        Pass the "Issued archive" path from CLAUDE.md if it differs.
#   --dry-run            Print what would be deleted and delete nothing.
#
# Refuses to delete anything unless the named file is already present and
# non-empty in the issued archive. The archive is the only surviving copy of
# each cycle, so it is verified first and never touched by this script.
#
# Project paths are derived from this script's own location — it lives at
# <project>/<Meeting Notes>/skills/pipeline-cleanup/ — so it needs no editing
# per project and works whatever the Meeting Notes folder is called.
#
# Exit codes: 0 = cleared (or dry run), 1 = archive not confirmed, 2 = bad usage.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
NOTES="$(cd -- "$SCRIPT_DIR/../.." && pwd)"   # skills/pipeline-cleanup -> Meeting Notes
ROOT="$(dirname -- "$NOTES")"                  # project root

ARCHIVE="$NOTES/Archive"
DRY_RUN=0
ARCHIVED=""

while [ $# -gt 0 ]; do
  case "$1" in
    --archive)
      [ $# -ge 2 ] || { echo "ERROR: --archive needs a directory" >&2; exit 2; }
      ARCHIVE="$2"; shift 2 ;;
    --dry-run)
      DRY_RUN=1; shift ;;
    -*)
      echo "ERROR: unknown option '$1'" >&2; exit 2 ;;
    *)
      [ -z "$ARCHIVED" ] || { echo "ERROR: pass exactly one filename" >&2; exit 2; }
      ARCHIVED="$1"; shift ;;
  esac
done

if [ -z "$ARCHIVED" ]; then
  echo "ERROR: pass the archived filename, e.g. 'Acme - Meeting Notes #15.docx'" >&2
  exit 2
fi

# Guard 1: reject anything that tries to escape the archive folder.
case "$ARCHIVED" in
  */*|..*) echo "ERROR: expected a bare filename, got '$ARCHIVED'" >&2; exit 2 ;;
esac

# Guard 2: the archived file must exist and be non-empty before we delete sources.
if [ ! -s "$ARCHIVE/$ARCHIVED" ]; then
  echo "ERROR: '$ARCHIVED' is not present (or is empty) in:" >&2
  echo "       $ARCHIVE" >&2
  echo "       Nothing deleted — the archive move must succeed first." >&2
  exit 1
fi

echo "Project : $ROOT"
echo "Archive confirmed: $ARCHIVED ($(wc -c <"$ARCHIVE/$ARCHIVED" | tr -d ' ') bytes)"
[ "$DRY_RUN" -eq 1 ] && echo "DRY RUN — nothing will be deleted"
echo

deleted=0
for folder in intake output transcripts; do
  target="$NOTES/$folder"
  [ -d "$target" ] || continue
  # Regular files only, one level deep, skipping dotfiles (.DS_Store, .gitkeep).
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    if [ "$DRY_RUN" -eq 1 ]; then
      echo "  would delete  $folder/$(basename "$f")"
    else
      echo "  deleted  $folder/$(basename "$f")"
      rm -f -- "$f"
    fi
    deleted=$((deleted + 1))
  done < <(find "$target" -maxdepth 1 -type f ! -name '.*' -print)
done

# The review form lives in the project root and is regenerated every cycle.
if [ -f "$ROOT/qa-session.html" ]; then
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  would delete  qa-session.html"
  else
    echo "  deleted  qa-session.html"
    rm -f -- "$ROOT/qa-session.html"
  fi
  deleted=$((deleted + 1))
fi

echo
if [ "$DRY_RUN" -eq 1 ]; then
  echo "$deleted file(s) would be cleared. Nothing was deleted."
else
  echo "Cleared $deleted file(s). Folders left in place; archive untouched."
fi
