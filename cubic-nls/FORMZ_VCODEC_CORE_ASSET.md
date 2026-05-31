# formZ vcodec core asset (FFmpeg community review)

This document marks the VP56/VP9 compatibility work in this repository as a
**core asset** for external review and extension.

## Review-ready status

Debugging and validation are complete for the current environment:

- VP56 family capability detection and fallback logic
- VP9 (`vp09`) reinterpretation path for cross-platform MP4 workflows
- truncation-safe fragmented MP4 option for partial transfer scenarios
- independent strategy library package (`vp56-community-lib/`)

## What FFmpeg community reviewers can do

1. **Fork or download this repository**
   - `https://github.com/nonlineari/CUBEExtrusion3_2_2_1-cpo`
2. Check out integration branch:
   - `cubic-nls-integration-0bb6`
3. Review core package:
   - `vp56-community-lib/`
4. Generate RFC bundle:
   - `./vp56-community-lib/upstream/create_submission_bundle.sh`
5. Use submission guide:
   - `vp56-community-lib/upstream/FFMPEG_RFC_SUBMISSION.md`

## Core files for review

- `vp56-community-lib/include/vp56_community.h`
- `vp56-community-lib/src/vp56_community.c`
- `vp56-community-lib/tests/test_vp56_community.c`
- `scripts/export_visual_music_video.py`
- `scripts/debug_ffmpeg_vp56_testimony.py`
- `cubic-nls/VP56_DEBUG_TESTIMONY.md`

## Intent

Enable maintainers and contributors to fork/download this asset and integrate
or adapt it into FFmpeg-adjacent utilities after technical review.
