#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./prepare_ffmpeg_rfc_cover.sh <commit-ish> [out-dir]
#
# Example:
#   ./prepare_ffmpeg_rfc_cover.sh HEAD ./rfc-out
#   git send-email --to=ffmpeg-devel@ffmpeg.org ./rfc-out/0000-*.patch ./rfc-out/0001-*.patch

COMMITISH="${1:-HEAD}"
OUT_DIR="${2:-./rfc-out}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_PATH="$SCRIPT_DIR/FFMPEG_RFC_0_1_COVERLETTER.txt"

if [[ ! -f "$TEMPLATE_PATH" ]]; then
  echo "Template not found: $TEMPLATE_PATH" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"
git format-patch --cover-letter --subject-prefix="RFC PATCH" -1 "$COMMITISH" -o "$OUT_DIR"

COVER_PATCH="$(ls -1 "$OUT_DIR"/0000-*.patch | head -n1)"
if [[ -z "$COVER_PATCH" ]]; then
  echo "Unable to find generated cover letter patch in $OUT_DIR" >&2
  exit 1
fi

python3 - "$COVER_PATCH" "$TEMPLATE_PATH" <<'PY'
import pathlib
import re
import sys

cover_path = pathlib.Path(sys.argv[1])
template_path = pathlib.Path(sys.argv[2])

template = template_path.read_text(encoding="utf-8")
cover = cover_path.read_text(encoding="utf-8")

lines = template.splitlines()
if not lines or not lines[0].startswith("SUBJECT: "):
    raise SystemExit("Template first line must start with 'SUBJECT: '")

subject = lines[0].split("SUBJECT: ", 1)[1].strip()
body = "\n".join(lines[2:]).strip()

cover = re.sub(r"(\[RFC PATCH 0/1\] )\*\*\* SUBJECT HERE \*\*\*", r"\1" + subject, cover)
cover = cover.replace("*** BLURB HERE ***", body)

cover_path.write_text(cover, encoding="utf-8")
PY

echo "Prepared RFC cover letter: $COVER_PATCH"
echo "Next step:"
echo "  git send-email --to=ffmpeg-devel@ffmpeg.org \"$COVER_PATCH\" \"$OUT_DIR\"/0001-*.patch"
