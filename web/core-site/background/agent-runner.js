import { runAgent } from "../agent.js";
import { runMultiAgentTask } from "../agents/orchestrator.js";
import { addMemory } from "../memory.js";

// Aria Agent Runner (v1)
// Processes queued tasks over time

let running = false;
let queue = [];

export function enqueueTask(task) {
  queue.push(task);
  addMemory({ type: "task_enqueued", task });
}

async function processTask(task) {
  if (task.mode === "multi") {
    return await runMultiAgentTask(task.input);
  }

  return await runAgent(task.input, task.context || {});
}

export function startAgentRunner(interval = 5000) {
  if (running) return;
  running = true;

  addMemory({ type: "agent_runner_started" });

  setInterval(async () => {
    if (queue.length === 0) return;

    const task = queue.shift();

    try {
      const result = await processTask(task);
      addMemory({ type: "task_completed", task, result });
    } catch (err) {
      addMemory({ type: "task_error", task, error: err.message });
    }
  }, interval);
}

export function stopAgentRunner() {
  running = false;
  addMemory({ type: "agent_runner_stopped" });
}