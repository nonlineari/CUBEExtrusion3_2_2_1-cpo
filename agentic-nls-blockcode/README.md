# Agentic NLS Blockcode Studio

This module adds an "Agentic NLS" workflow builder to the repository.

It provides a browser app that:

- Converts natural-language prompts into a block-based workflow
- Lets you edit and reorder blocks manually
- Executes an L-system pipeline (`axiom -> rules -> iterations -> render`)
- Draws the output directly on an HTML canvas
- Supports a geometric master renderer for cube/folding/circular prompts
- Exports block workflows as JSON

## Open it

You can open the app directly in any browser:

1. Navigate to `agentic-nls-blockcode/index.html`
2. Enter a prompt (for example, a fern or tree instruction)
3. Click **Generate Blocks**
4. Click **Run Workflow**

## Prompt examples

- `Build a fern style L-system with axiom F, angle 25, rule F=F[+F]F[-F]F and run 4 iterations.`
- `Create a Koch pattern with angle 90 and rule F->F+F-F-F+F with 3 iterations.`
- `Complete a build using a folding neural network left 2 right system inside a 3 dimensional circular 6sided folding cube with red, white and blue in black background (0).`

## Notes

- Iterations are capped at 7 to keep rendering responsive.
- A `Render` block is required to execute the workflow.

## Tor Browser and Brave compatibility

- The app now avoids newer JavaScript-only syntax so it can run on stricter browser engines.
- If download APIs are blocked by browser privacy settings, the export JSON is shown in the **Generated sequence** panel for manual copy.
- In Tor Browser, JavaScript must be enabled for the app to run (the highest security mode may disable scripts).

## Geometric master mode

Prompts containing terms such as `cube`, `3 dimensional`, `folding`, `neural`, `circular`, or `6 sided` automatically activate the geometric master renderer. This mode uses:

- dark background detection (e.g., "black background")
- color palette extraction (e.g., red/white/blue)
- sided polygon guidance (e.g., 6-sided)
- pseudo-3D line projection and cube wireframe accents

## Video export presets (5s / 10s)

Generate `.mp4` output from prompt-driven visual style using FFmpeg:

- `python3 scripts/export_visual_music_video.py --duration 5 --mode h264`
- `python3 scripts/export_visual_music_video.py --duration 10 --mode auto`
- `python3 scripts/export_visual_music_video.py --duration 10 --mode vp9-vp09 --truncation-safe`

`--mode auto` attempts VP56 bridge (`vp6f`) when available, then encodes final `.mp4` with H.264.
`--mode vp9-vp09` uses `libvpx-vp9` and writes MP4 with `vp09` codec tag for cross-platform parser compatibility.
`--truncation-safe` enables fragmented MP4 flags for better partial/truncated playback behavior.

## VP56 / libxVP56 debugging

If VP56 bridge mode fails, generate a diagnostic testimony report:

- `python3 scripts/debug_ffmpeg_vp56_testimony.py`

This produces markdown + JSON evidence in `output/` and links directly to FFmpeg GitHub VP56 source files used for verification.
