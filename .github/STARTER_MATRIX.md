# Use-Case → Best Prompt / Agent

Quick-pick reference. Find your scenario, grab the recommended agent or prompt, and go.

## At a Glance

| Use-Case | Agent | Prompt | When to pick |
| -------- | ----- | ------ | ------------ |
| Bug triage & root-cause | `agi` | `triage-bug` | Reproduce → isolate → fix a reported defect |
| Add / fix unit tests | `testing-and-regression` | `test-first-change` | Tests must exist or pass before code ships |
| Safe refactor (no behavior change) | `agi` | `refactor-safely` | Restructure without breaking consumers |
| New API endpoint | `functions-api` | `api-endpoint-addition` | Add a route to `function_app.py` |
| Azure Function codegen + deploy | `azure-function-codegen-and-deployment` | `api-endpoint-addition` | Full Function lifecycle with ARM/deployment |
| Azure Static Web App deploy | `azure-static-web-app` | — | SWA config, build, routing, deploy |
| SSE / streaming issue | `chat-provider-stack` | `sse-stream-debug` | Broken `data:` chunks, early disconnect, `[DONE]` |
| Provider fallback / detect | `chat-provider-stack` | `provider-fallback-debug` | Wrong provider selected or silent fallback |
| Aria UI runtime bug | `aria-runtime-debug` | `triage-bug` | `/api/aria/*` state, command, or object issues |
| Orchestrator job design | `orchestrator-dryrun-status` | `orchestrator-job-design` | New autotrain / quantum / evaluation job |
| Orchestrator dry-run check | `orchestrator-dryrun-status` | — | Validate existing job config before real run |
| Quantum experiment | `quantum-safe-execution` | `quantum-experiment-plan` | Design or run a quantum workflow safely |
| Performance bottleneck | `agi` | `optimize-performance` | Profile, measure, optimize a slow path |
| Security / secrets audit | `agi` | `security-hardening` | Harden config, auth, or dependency surfaces |
| Docs / metadata drift | `docs-and-instructions-sync` | `sync-docs` | Instructions, README, or cross-links out-of-date |
| Release go / no-go | `release-readiness` | `release-readiness` | Pre-release checklist, risk gating |
| Autonomous multi-step task | `agi` | `agi` | Complex, cross-surface work with self-correction |
| SQL / Cosmos DB issue | `database-and-telemetry` | `database-debug` | Query failures, connectivity, schema migrations |
| Telemetry / tracing issue | `database-and-telemetry` | `telemetry-debug` | Missing spans, dropped events, observability gaps |
| Subscription / pricing change | `monetization-and-subscriptions` | `subscription-feature-gate` | Tier, feature gate, or Stripe integration work |
| Dashboard widget / page | `dashboard-and-monitoring` | `dashboard-widget` | New monitoring view, live-data feed, or chart |
| Dataset curation / expansion | `dataset-pipeline` | `dataset-curation` | Discover, download, validate, or organize data |
| LoRA training run | `lora-training` | `lora-training-run` | Configure, train, evaluate, and promote adapters |
| YAML config authoring | `orchestrator-dryrun-status` | `config-yaml-authoring` | New or modified orchestrator/pipeline config |
| Dependency / environment fix | `dependency-and-environment` | `environment-fix` | Import errors, missing packages, venv issues |
| Dependency audit | `dependency-and-environment` | `dependency-audit` | Outdated or vulnerable packages |
| LLM tool creation | `llm-maker` | `llm-tool-creation` | Build, validate, register custom LLM tools |
| Cooking AI development | `cooking-ai` | `triage-bug` | Recipe agent, provider, or CLI changes |
| CI/CD pipeline run | `ci-cd-pipeline` | `ci-pipeline-run` | Validate configs, run tests, prepare artifacts |
| Model deployment | `model-deployment` | `model-deploy` | Quality-gated deploy with canary/blue-green/rolling |
| Backup / recovery | `backup-and-recovery` | `backup-restore` | Create, verify, or restore backups of artifacts |
| Notification config | `notification-system` | `notification-setup` | Desktop or email notification channels |
| Chat memory / embeddings | `chat-memory-and-context` | `chat-memory-debug` | Embedding generation, storage, retrieval issues |
| SQL migration | `database-and-telemetry` | `migration-script` | Safe, reversible schema changes |
| Code review | `agi` | `code-review` | Correctness, security, performance, conventions |
| Aria command / state | `aria-runtime-debug` | `aria-command-addition` | New runtime command or state transition |
| Vision / multimodal training | `lora-training` | `vision-training` | Vision fine-tuning or multimodal pipeline |
| Cost estimation | `agi` | `cost-estimation` | Estimate costs before expensive operations |
| Chat-web frontend dev | `chat-web-frontend` | `chat-web-sse-consumer` | SSE consumer, TTS playback, chat UI |
| Azure Quantum deploy | `quantum-azure-infra` | `azure-quantum-deploy` | Workspace provisioning, Bicep, cost monitoring |
| RAG pipeline | `lora-advanced-pipeline` | `lora-rag-pipeline` | Retrieval-augmented generation with LoRA |
| DeepSpeed training | `lora-advanced-pipeline` | `deepspeed-training` | Distributed Zero-3 LoRA training |
| Model serving | `lora-advanced-pipeline` | `model-serving` | Serve trained models for inference |
| GitHub Actions workflow | `ci-cd-pipeline` | `github-actions-workflow` | CI/CD workflow YAML creation/modification |
| Data augmentation | `lora-advanced-pipeline` | `data-augmentation` | Augment training datasets |
| GPU optimization | `performance-profiling` | `gpu-optimization` | GPU memory and throughput tuning |
| Semantic pruning | `agi` | `semantic-pruning` | Prune models, context, or datasets |
| Cosmos DB setup | `database-and-telemetry` | `cosmos-container-setup` | Container, partition key, throughput config |
| Security scan / audit | `security-and-compliance` | `security-hardening` | CodeQL, secrets, auth, dependency audit |

## How to Use

### Agents (interactive sessions)

Invoke from Copilot Chat with the agent selector or `@<agent-name>`:

```text
@functions-api  Add a GET /api/notifications endpoint
@quantum-safe-execution  Run heart_quick job on local sim
```

### Prompts (one-shot templates)

Open a prompt from `.github/prompts/` via the Copilot prompt picker, or paste its contents into chat:

```text
/triage-bug  The /api/chat/stream route returns 500 on empty context
/refactor-safely  Extract token pruning into shared/token_utils.py
```

### Combining Both

For maximum guidance, pick the **agent** for the session and feed it the **prompt** as the first message:

```text
@testing-and-regression  /test-first-change  Cover shared/cosmos_client.py
```

## Decision Flowchart

```text
Is this a quantum task?
  └─ Yes → quantum-safe-execution + quantum-experiment-plan
  └─ No ↓

Is this about streaming / providers?
  └─ Yes → chat-provider-stack + sse-stream-debug or provider-fallback-debug
  └─ No ↓

Is this an API route change?
  └─ Yes → functions-api + api-endpoint-addition
  └─ No ↓

Is this Aria UI / runtime?
  └─ Yes → aria-runtime-debug + triage-bug
  └─ No ↓

Is this a database / telemetry issue?
  └─ Yes → database-and-telemetry + database-debug or telemetry-debug
  └─ No ↓

Is this subscription / monetization?
  └─ Yes → monetization-and-subscriptions + subscription-feature-gate
  └─ No ↓

Is this a dashboard / monitoring change?
  └─ Yes → dashboard-and-monitoring + dashboard-widget
  └─ No ↓

Is this about datasets?
  └─ Yes → dataset-pipeline + dataset-curation
  └─ No ↓

Is this LoRA training?
  └─ Yes → lora-training + lora-training-run
  └─ No ↓

Is this an orchestrator job?
  └─ Yes → orchestrator-dryrun-status + orchestrator-job-design
  └─ No ↓

Is this an import / dependency issue?
  └─ Yes → dependency-and-environment + environment-fix or dependency-audit
  └─ No ↓

Is this LLM tool creation?
  └─ Yes → llm-maker + llm-tool-creation
  └─ No ↓

Is this cooking-ai?
  └─ Yes → cooking-ai + triage-bug
  └─ No ↓

Is this CI/CD or pipeline validation?
  └─ Yes → ci-cd-pipeline + ci-pipeline-run
  └─ No ↓

Is this model deployment or rollback?
  └─ Yes → model-deployment + model-deploy
  └─ No ↓

Is this about backups or recovery?
  └─ Yes → backup-and-recovery + backup-restore
  └─ No ↓

Is this about notifications?
  └─ Yes → notification-system + notification-setup
  └─ No ↓

Is this chat memory / embeddings?
  └─ Yes → chat-memory-and-context + chat-memory-debug
  └─ No ↓

Is this a cost / resource estimation?
  └─ Yes → agi + cost-estimation
  └─ No ↓

Is this a code review?
  └─ Yes → agi + code-review
  └─ No ↓

Is this chat-web frontend / SSE?
  └─ Yes → chat-web-frontend + chat-web-sse-consumer
  └─ No ↓

Is this Azure Quantum infra?
  └─ Yes → quantum-azure-infra + azure-quantum-deploy
  └─ No ↓

Is this advanced LoRA (RAG / DeepSpeed / serving)?
  └─ Yes → lora-advanced-pipeline + lora-rag-pipeline or deepspeed-training or model-serving
  └─ No ↓

Is this GPU optimization?
  └─ Yes → performance-profiling + gpu-optimization
  └─ No ↓

Is this data augmentation?
  └─ Yes → lora-advanced-pipeline + data-augmentation
  └─ No ↓

Is this Cosmos DB setup?
  └─ Yes → database-and-telemetry + cosmos-container-setup
  └─ No ↓

Is this a security scan / audit?
  └─ Yes → security-and-compliance + security-hardening
  └─ No ↓

Is this a release / deploy gate?
  └─ Yes → release-readiness + release-readiness
  └─ No ↓

Is this docs / metadata sync?
  └─ Yes → docs-and-instructions-sync + sync-docs
  └─ No ↓

Default → agi + the most relevant prompt
```
