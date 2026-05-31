const blockDefinitions = {
  setAxiom: {
    label: "Set Axiom",
    fields: [{ key: "axiom", label: "Axiom", type: "text", defaultValue: "F" }],
  },
  setAngle: {
    label: "Set Angle",
    fields: [{ key: "angle", label: "Angle (degrees)", type: "number", defaultValue: "25" }],
  },
  addRule: {
    label: "Add Rule",
    fields: [
      { key: "symbol", label: "Symbol", type: "text", defaultValue: "F" },
      {
        key: "replacement",
        label: "Replacement",
        type: "text",
        defaultValue: "F[+F]F[-F]F",
      },
    ],
  },
  setIterations: {
    label: "Set Iterations",
    fields: [
      { key: "iterations", label: "Iterations", type: "number", defaultValue: "4" },
    ],
  },
  setStep: {
    label: "Set Step Length",
    fields: [{ key: "step", label: "Step Length", type: "number", defaultValue: "6" }],
  },
  render: {
    label: "Render",
    fields: [],
  },
};

const blocksContainer = document.getElementById("blocksContainer");
const promptInput = document.getElementById("promptInput");
const blockTypeSelect = document.getElementById("blockType");
const generateBtn = document.getElementById("generateBtn");
const clearBlocksBtn = document.getElementById("clearBlocksBtn");
const addBlockBtn = document.getElementById("addBlockBtn");
const runBtn = document.getElementById("runBtn");
const exportBtn = document.getElementById("exportBtn");
const sequenceOut = document.getElementById("sequenceOut");
const statusOut = document.getElementById("statusOut");
const renderCanvas = document.getElementById("renderCanvas");

const appState = {
  blocks: [],
};

function coalesce(value, fallback) {
  return value === null || value === undefined ? fallback : value;
}

function getMatchValue(match, index, fallback) {
  if (match && match[index]) {
    return match[index];
  }
  return fallback;
}

function isElementTag(target, tagName) {
  return Boolean(
    target &&
      target.tagName &&
      String(target.tagName).toUpperCase() === String(tagName).toUpperCase()
  );
}

function createBlock(type, values = {}) {
  const definition = blockDefinitions[type];
  const data = {};
  for (const field of definition.fields) {
    data[field.key] = coalesce(values[field.key], field.defaultValue);
  }

  return {
    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    type,
    values: data,
  };
}

function setStatus(lines) {
  statusOut.textContent = Array.isArray(lines) ? lines.join("\n") : String(lines);
}

function renderBlocks() {
  blocksContainer.innerHTML = "";

  if (appState.blocks.length === 0) {
    const empty = document.createElement("p");
    empty.textContent = "No blocks yet. Generate from prompt or add blocks manually.";
    blocksContainer.appendChild(empty);
    return;
  }

  appState.blocks.forEach((block, index) => {
    const definition = blockDefinitions[block.type];
    const blockEl = document.createElement("article");
    blockEl.className = "block";
    blockEl.dataset.blockId = block.id;

    const fieldsHtml = definition.fields
      .map((field) => {
        const value = coalesce(block.values[field.key], "");
        return `
          <label>${field.label}
            <input
              data-field-key="${field.key}"
              type="${field.type}"
              value="${escapeHtml(String(value))}"
            />
          </label>
        `;
      })
      .join("");

    blockEl.innerHTML = `
      <div class="block-head">
        <strong>${index + 1}. ${definition.label}</strong>
        <div class="block-actions">
          <button data-action="up" type="button" title="Move up">Up</button>
          <button data-action="down" type="button" title="Move down">Down</button>
          <button data-action="delete" type="button" title="Delete">Delete</button>
        </div>
      </div>
      <div class="block-body">${fieldsHtml || "<em>No parameters</em>"}</div>
    `;

    blocksContainer.appendChild(blockEl);
  });
}

function escapeHtml(value) {
  return value
    .split("&")
    .join("&amp;")
    .split("<")
    .join("&lt;")
    .split(">")
    .join("&gt;")
    .split('"')
    .join("&quot;")
    .split("'")
    .join("&#039;");
}

function parsePromptToBlocks(text) {
  const source = text.trim();
  const fallback = [
    createBlock("setAxiom", { axiom: "F" }),
    createBlock("setAngle", { angle: "25" }),
    createBlock("addRule", { symbol: "F", replacement: "F[+F]F[-F]F" }),
    createBlock("setIterations", { iterations: "4" }),
    createBlock("setStep", { step: "6" }),
    createBlock("render"),
  ];

  if (!source) {
    return fallback;
  }

  const blocks = [];
  const lower = source.toLowerCase();

  const axiomMatch = source.match(/axiom\s*(?:is|=|:)?\s*([A-Za-z+\-\[\]\/\\]+)\b/i);
  const angleMatch = source.match(/angle\s*(?:is|of|=|:)?\s*(-?\d+(?:\.\d+)?)/i);
  const iterationMatch =
    source.match(/(\d+)\s*iterations?/i) ||
    source.match(/iterate\s*(?:for)?\s*(\d+)/i) ||
    source.match(/depth\s*(?:is|=|:)?\s*(\d+)/i);
  const stepMatch = source.match(/step(?:\s*length)?\s*(?:is|=|of|:)?\s*(\d+(?:\.\d+)?)/i);

  const rules = [];
  const ruleRegex = /([A-Za-z])\s*(?:->|=>|=|becomes)\s*([A-Za-z+\-\[\]\/\\]+)/g;
  let found;
  while ((found = ruleRegex.exec(source)) !== null) {
    rules.push({ symbol: found[1], replacement: found[2] });
  }

  if (rules.length === 0) {
    if (/(fern|tree|branch|plant)/i.test(lower)) {
      rules.push({ symbol: "F", replacement: "F[+F]F[-F]F" });
    } else if (/koch|snowflake/i.test(lower)) {
      rules.push({ symbol: "F", replacement: "F+F-F-F+F" });
    } else if (/sierpinski/i.test(lower)) {
      rules.push({ symbol: "F", replacement: "F-G+F+G-F" });
      rules.push({ symbol: "G", replacement: "GG" });
    }
  }

  blocks.push(createBlock("setAxiom", { axiom: getMatchValue(axiomMatch, 1, "F") }));
  blocks.push(createBlock("setAngle", { angle: getMatchValue(angleMatch, 1, "25") }));

  if (rules.length === 0) {
    rules.push({ symbol: "F", replacement: "F[+F]F[-F]F" });
  }
  for (const rule of rules) {
    blocks.push(createBlock("addRule", rule));
  }

  blocks.push(
    createBlock("setIterations", { iterations: getMatchValue(iterationMatch, 1, "4") })
  );
  blocks.push(createBlock("setStep", { step: getMatchValue(stepMatch, 1, "6") }));
  blocks.push(createBlock("render"));
  return blocks;
}

function applyLSystem(axiom, rules, iterations) {
  let current = axiom;
  for (let i = 0; i < iterations; i += 1) {
    let next = "";
    for (const symbol of current) {
      next += coalesce(rules[symbol], symbol);
    }
    current = next;
  }
  return current;
}

function validateNumber(value, fallback) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    return fallback;
  }
  return parsed;
}

function runWorkflow(blocks) {
  const context = {
    axiom: "F",
    angle: 25,
    iterations: 4,
    step: 6,
    rules: {},
    shouldRender: false,
  };
  const statusLines = [];

  for (const block of blocks) {
    switch (block.type) {
      case "setAxiom":
        context.axiom = String(block.values.axiom || "F");
        statusLines.push(`Axiom set to ${context.axiom}`);
        break;
      case "setAngle":
        context.angle = validateNumber(block.values.angle, 25);
        statusLines.push(`Angle set to ${context.angle}`);
        break;
      case "addRule":
        if (block.values.symbol && block.values.replacement) {
          context.rules[String(block.values.symbol).trim()] = String(
            block.values.replacement
          ).trim();
          statusLines.push(
            `Rule added: ${block.values.symbol.trim()} -> ${block.values.replacement.trim()}`
          );
        }
        break;
      case "setIterations":
        context.iterations = Math.max(0, Math.floor(validateNumber(block.values.iterations, 4)));
        if (context.iterations > 7) {
          context.iterations = 7;
          statusLines.push("Iteration cap applied at 7 for safe rendering.");
        } else {
          statusLines.push(`Iterations set to ${context.iterations}`);
        }
        break;
      case "setStep":
        context.step = Math.max(1, validateNumber(block.values.step, 6));
        statusLines.push(`Step length set to ${context.step}`);
        break;
      case "render":
        context.shouldRender = true;
        statusLines.push("Render block reached.");
        break;
      default:
        break;
    }
  }

  if (!context.shouldRender) {
    throw new Error("No Render block found. Add a Render block to complete the workflow.");
  }

  const sequence = applyLSystem(context.axiom, context.rules, context.iterations);
  drawSequence(renderCanvas, sequence, context.angle, context.step);

  return {
    sequence,
    statusLines: [
      ...statusLines,
      `Final sequence length: ${sequence.length}`,
      `Rule count: ${Object.keys(context.rules).length}`,
    ],
  };
}

function getBounds(sequence, angleDegrees, step) {
  const angle = (Math.PI / 180) * angleDegrees;
  let x = 0;
  let y = 0;
  let heading = -Math.PI / 2;
  const stack = [];

  let minX = 0;
  let maxX = 0;
  let minY = 0;
  let maxY = 0;

  for (const char of sequence) {
    if (char === "F" || char === "G") {
      x += Math.cos(heading) * step;
      y += Math.sin(heading) * step;
      minX = Math.min(minX, x);
      maxX = Math.max(maxX, x);
      minY = Math.min(minY, y);
      maxY = Math.max(maxY, y);
    } else if (char === "f") {
      x += Math.cos(heading) * step;
      y += Math.sin(heading) * step;
    } else if (char === "+") {
      heading += angle;
    } else if (char === "-") {
      heading -= angle;
    } else if (char === "[") {
      stack.push({ x, y, heading });
    } else if (char === "]") {
      const state = stack.pop();
      if (state) {
        x = state.x;
        y = state.y;
        heading = state.heading;
      }
    }
  }

  return { minX, maxX, minY, maxY };
}

function drawSequence(canvas, sequence, angleDegrees, step) {
  const ctx = canvas.getContext("2d");
  if (!ctx) {
    throw new Error("Canvas rendering is not available in this browser.");
  }
  const { width, height } = canvas;
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, width, height);

  const bounds = getBounds(sequence, angleDegrees, step);
  const drawingWidth = Math.max(1, bounds.maxX - bounds.minX);
  const drawingHeight = Math.max(1, bounds.maxY - bounds.minY);
  const padding = 30;
  const scale = Math.min(
    (width - padding * 2) / drawingWidth,
    (height - padding * 2) / drawingHeight
  );

  const angle = (Math.PI / 180) * angleDegrees;
  let x = ((bounds.minX + bounds.maxX) / -2) * scale + width / 2;
  let y = ((bounds.minY + bounds.maxY) / -2) * scale + height / 2;
  let heading = -Math.PI / 2;
  const stack = [];

  ctx.strokeStyle = "#1f7a1f";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(x, y);

  for (const char of sequence) {
    if (char === "F" || char === "G") {
      const nextX = x + Math.cos(heading) * step * scale;
      const nextY = y + Math.sin(heading) * step * scale;
      ctx.lineTo(nextX, nextY);
      x = nextX;
      y = nextY;
    } else if (char === "f") {
      x += Math.cos(heading) * step * scale;
      y += Math.sin(heading) * step * scale;
      ctx.moveTo(x, y);
    } else if (char === "+") {
      heading += angle;
    } else if (char === "-") {
      heading -= angle;
    } else if (char === "[") {
      stack.push({ x, y, heading });
    } else if (char === "]") {
      const state = stack.pop();
      if (state) {
        x = state.x;
        y = state.y;
        heading = state.heading;
        ctx.moveTo(x, y);
      }
    }
  }
  ctx.stroke();
}

function exportBlocksJson(blocks) {
  const payload = {
    name: "agentic-nls-workflow",
    blocks,
  };
  const jsonPayload = JSON.stringify(payload, null, 2);

  if (
    typeof Blob === "undefined" ||
    typeof URL === "undefined" ||
    typeof URL.createObjectURL !== "function"
  ) {
    sequenceOut.textContent = jsonPayload;
    return {
      exported: false,
      message:
        "Download APIs are unavailable in this browser. JSON was placed in Generated sequence for manual copy.",
    };
  }

  const file = new Blob([jsonPayload], {
    type: "application/json",
  });
  const url = URL.createObjectURL(file);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "agentic-nls-workflow.json";
  anchor.click();
  URL.revokeObjectURL(url);
  return {
    exported: true,
    message: "Workflow exported as JSON.",
  };
}

blocksContainer.addEventListener("click", (event) => {
  const target = event.target;
  if (!isElementTag(target, "button")) {
    return;
  }

  const blockEl = target.closest(".block");
  if (!blockEl) {
    return;
  }

  const blockId = blockEl.dataset.blockId;
  const index = appState.blocks.findIndex((item) => item.id === blockId);
  if (index < 0) {
    return;
  }

  const action = target.dataset.action;
  if (action === "delete") {
    appState.blocks.splice(index, 1);
  } else if (action === "up" && index > 0) {
    const current = appState.blocks[index];
    appState.blocks[index] = appState.blocks[index - 1];
    appState.blocks[index - 1] = current;
  } else if (action === "down" && index < appState.blocks.length - 1) {
    const current = appState.blocks[index];
    appState.blocks[index] = appState.blocks[index + 1];
    appState.blocks[index + 1] = current;
  }

  renderBlocks();
});

blocksContainer.addEventListener("input", (event) => {
  const target = event.target;
  if (!isElementTag(target, "input")) {
    return;
  }

  const blockEl = target.closest(".block");
  if (!blockEl) {
    return;
  }

  const block = appState.blocks.find((item) => item.id === blockEl.dataset.blockId);
  if (!block) {
    return;
  }

  const key = target.dataset.fieldKey;
  if (!key) {
    return;
  }
  block.values[key] = target.value;
});

generateBtn.addEventListener("click", () => {
  appState.blocks = parsePromptToBlocks(promptInput.value);
  renderBlocks();
  setStatus("Blocks generated from natural language prompt.");
});

clearBlocksBtn.addEventListener("click", () => {
  appState.blocks = [];
  renderBlocks();
  sequenceOut.textContent = "";
  setStatus("All blocks cleared.");
});

addBlockBtn.addEventListener("click", () => {
  appState.blocks.push(createBlock(blockTypeSelect.value));
  renderBlocks();
});

runBtn.addEventListener("click", () => {
  try {
    const output = runWorkflow(appState.blocks);
    sequenceOut.textContent = output.sequence;
    setStatus(output.statusLines);
  } catch (error) {
    setStatus(`Error: ${error.message}`);
  }
});

exportBtn.addEventListener("click", () => {
  const output = exportBlocksJson(appState.blocks);
  setStatus(output.message);
});

appState.blocks = parsePromptToBlocks("");
renderBlocks();
setStatus("Ready.");
