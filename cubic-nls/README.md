# cubic-nls

cubic-nls is the consolidated integration project built from four draft branches in
`nonlineari/CUBEExtrusion3_2_2_1-cpo`.

## Integrated components

- `agentic-nls-blockcode/`: prompt-to-block visual system with geometric master rendering
- `scripts/build_visual_language.py`: visual language animation generator
- `midi_to_metadata.py`: MIDI to metadata conversion CLI
- `analysis/BrushDynamics.java` and `analysis/brush_dynamics.lua`: brush dynamics analysis
- `vp56-community-lib/`: independent VP56-family compatibility strategy library

## Visual music workflow (Agentic NLS)

1. Open `agentic-nls-blockcode/index.html`
2. Paste a visual-music prompt, for example:

   `Complete a build using a folding neural network left 2 right system inside a 3 dimensional circular 6sided folding cube with red, white and blue in black background (0) and visual music rhythm layers.`

3. Click **Generate Blocks**
4. Click **Run Workflow**
5. Inspect:
   - geometric render on the canvas
   - generated sequence
   - status log (renderer mode and rule summary)


## MP4 export with FFmpeg (H.264 + VP56 bridge option)

Use the new exporter:

`scripts/export_visual_music_video.py`

Examples:

- 5-second MP4 (direct H.264):

  `python3 scripts/export_visual_music_video.py --duration 5 --mode h264`

- 10-second MP4 (auto mode; uses VP56 bridge when available, otherwise falls back to H.264):

  `python3 scripts/export_visual_music_video.py --duration 10 --mode auto`

- 10-second MP4 in VP9/vp09 mode (for parser reinterpretation and gatekeeper compatibility checks):

  `python3 scripts/export_visual_music_video.py --duration 10 --mode vp9-vp09 --truncation-safe`

- Force VP56 bridge pipeline (vp6f intermediate -> H.264 mp4):

  `python3 scripts/export_visual_music_video.py --duration 10 --mode vp56-bridge --keep-intermediate`

Outputs are written to `output/visual_music_5s.mp4` or `output/visual_music_10s.mp4` by default.
Use `--truncation-safe` when fragmented MP4 behavior is required for truncated transfer scenarios.


## VP56 debug testimony

To debug requests like `libxVP56` and inspect what this FFmpeg build actually supports, run:

`python3 scripts/debug_ffmpeg_vp56_testimony.py`

This writes:

- `output/ffmpeg_vp56_testimony.md`
- `output/ffmpeg_vp56_testimony.json`

The report includes local codec/encoder evidence and links to original FFmpeg VP56 source files on GitHub.

A versioned summary is stored at `cubic-nls/VP56_DEBUG_TESTIMONY.md`.

## Notes

- This branch is intended as a combined repository candidate.
- Keep it unmerged into `master` until full creative and technical review is done.

## FFmpeg community-forward package

A standalone VP56 family compatibility library is included at `vp56-community-lib/`.

To prepare a review bundle for FFmpeg community forwarding:

- `./vp56-community-lib/upstream/create_submission_bundle.sh`

See: `vp56-community-lib/upstream/FFMPEG_RFC_SUBMISSION.md`

## formZ vcodec core asset

The review-ready handoff document is:

- `cubic-nls/FORMZ_VCODEC_CORE_ASSET.md`

It provides fork/download instructions and the exact files intended for FFmpeg
community review.
