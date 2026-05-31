# cubic-nls

cubic-nls is the consolidated integration project built from four draft branches in
`nonlineari/CUBEExtrusion3_2_2_1-cpo`.

## Integrated components

- `agentic-nls-blockcode/`: prompt-to-block visual system with geometric master rendering
- `scripts/build_visual_language.py`: visual language animation generator
- `midi_to_metadata.py`: MIDI to metadata conversion CLI
- `analysis/BrushDynamics.java` and `analysis/brush_dynamics.lua`: brush dynamics analysis

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

## Notes

- This branch is intended as a combined repository candidate.
- Keep it unmerged into `master` until full creative and technical review is done.
