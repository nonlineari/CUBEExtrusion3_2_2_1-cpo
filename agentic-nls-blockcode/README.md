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
