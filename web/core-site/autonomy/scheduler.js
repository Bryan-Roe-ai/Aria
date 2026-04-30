import { enqueueTask } from "../background/agent-runner.js";
import { generateProjectIdea, expandProject } from "./project-factory.js";
import { deployProject } from "./deployer.js";
import { addMemory } from "../memory.js";

// Autonomous Scheduler (v1)
// Decides what Aria should do next forever

let active = false;

async function cycle() {
  // 1. Generate idea
  const idea = await generateProjectIdea();

  // 2. Expand idea
  const expanded = await expandProject(idea);

  // 3. Enqueue build task
  enqueueTask({
    mode: "multi",
    input: `Build this project: ${JSON.stringify(expanded)}`,
    source: "scheduler"
  });

  // 4. Optionally deploy simulated result
  if (Math.random() > 0.5) {
    await deployProject(idea);
  }

  addMemory({ type: "scheduler_cycle_complete", idea });
}

export function startScheduler(interval = 30000) {
  if (active) return;
  active = true;

  addMemory({ type: "scheduler_started" });

  setInterval(() => {
    cycle().catch(err =>
      addMemory({ type: "scheduler_error", error: err.message })
    );
  }, interval);
}

export function stopScheduler() {
  active = false;
  addMemory({ type: "scheduler_stopped" });
}