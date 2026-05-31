# Agentic NLS Blockcode Studio

This module adds an "Agentic NLS" workflow builder to the repository.

It provides a browser app that:

- Converts natural-language prompts into a block-based workflow
- Lets you edit and reorder blocks manually
- Executes an L-system pipeline (`axiom -> rules -> iterations -> render`)
- Draws the output directly on an HTML canvas
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

## Notes

- Iterations are capped at 7 to keep rendering responsive.
- A `Render` block is required to execute the workflow.
