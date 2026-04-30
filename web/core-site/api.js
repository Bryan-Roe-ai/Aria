import { executeTool } from "./tools.js";

async function sendToAI(message, context = {}) {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      message,
      context,
      toolMode: true
    })
  });

  if (!res.ok) {
    throw new Error("AI request failed");
  }

  return await res.json();
}

async function runCommandOrAI(input) {
  const trimmed = input.trim();

  if (trimmed.startsWith("/")) {
    const [cmd, ...args] = trimmed.slice(1).split(" ");
    const result = await executeTool(cmd, { args });

    return {
      type: "tool",
      output: result
    };
  }

  const ai = await sendToAI(trimmed);

  return {
    type: "ai",
    output: ai.response || ai,
    tools: ai.tools || []
  };
}

export { sendToAI, runCommandOrAI };