#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
LIB_DIR="$ROOT_DIR/vp56-community-lib"
BUNDLE_DIR="$LIB_DIR/upstream/bundle"
ARCHIVE="$LIB_DIR/upstream/vp56-community-rfc-bundle.tar.gz"

mkdir -p "$BUNDLE_DIR"
rm -f "$ARCHIVE"

cp "$LIB_DIR/include/vp56_community.h" "$BUNDLE_DIR/"
cp "$LIB_DIR/src/vp56_community.c" "$BUNDLE_DIR/"
cp "$LIB_DIR/tests/test_vp56_community.c" "$BUNDLE_DIR/"
cp "$LIB_DIR/README.md" "$BUNDLE_DIR/"
cp "$LIB_DIR/upstream/FFMPEG_RFC_SUBMISSION.md" "$BUNDLE_DIR/"

tar -czf "$ARCHIVE" -C "$BUNDLE_DIR" .
echo "Created RFC bundle: $ARCHIVE"
