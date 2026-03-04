# Prompt Library Index

Reusable prompts for common engineering workflows.

## Core prompts

- `agi.prompt.md` — autonomous AGI baseline template.
- `triage-bug.prompt.md` — reproducible bug triage and root-cause workflow.
- `test-first-change.prompt.md` — add/fix tests before implementation.
- `refactor-safely.prompt.md` — constrained refactors with behavior compatibility.
- `sync-docs.prompt.md` — documentation and metadata drift reconciliation.
- `release-readiness.prompt.md` — pre-release checklist and risk validation.
- `security-hardening.prompt.md` — secrets/config/auth hardening pass.
- `optimize-performance.prompt.md` — bottleneck profiling and optimization loop.
- `api-endpoint-addition.prompt.md` — endpoint design, validation, and docs updates.
- `sse-stream-debug.prompt.md` — streaming/SSE reliability troubleshooting.
- `provider-fallback-debug.prompt.md` — provider selection/fallback diagnosis.
- `orchestrator-job-design.prompt.md` — dry-run-safe status-driven job design.
- `quantum-experiment-plan.prompt.md` — simulator-first quantum experiment planning.

## Data, training, and infrastructure prompts

- `database-debug.prompt.md` — SQL/Cosmos connectivity and query debugging.
- `telemetry-debug.prompt.md` — telemetry, tracing, and observability pipeline issues.
- `subscription-feature-gate.prompt.md` — subscription tiers and feature-gate changes.
- `dashboard-widget.prompt.md` — add dashboard pages, widgets, or live-data feeds.
- `dataset-curation.prompt.md` — dataset discovery, download, validation, and organization.
- `lora-training-run.prompt.md` — end-to-end LoRA adapter training configuration and execution.
- `config-yaml-authoring.prompt.md` — YAML config design for orchestrators and pipelines.
- `dependency-audit.prompt.md` — audit and update Python dependencies across requirements files.
- `environment-fix.prompt.md` — resolve import errors, path issues, or venv problems.
- `llm-tool-creation.prompt.md` — create, validate, and register custom LLM tools.

## Operations and deployment prompts

- `ci-pipeline-run.prompt.md` — run CI/CD pipeline: validate, test, prepare artifacts.
- `model-deploy.prompt.md` — deploy a model with quality gates and rollback plan.
- `backup-restore.prompt.md` — create, verify, or restore backups.
- `notification-setup.prompt.md` — configure desktop and email notification channels.
- `chat-memory-debug.prompt.md` — debug embeddings, retrieval, or context pruning.
- `migration-script.prompt.md` — write a safe, reversible database migration.
- `code-review.prompt.md` — review code for correctness, security, and conventions.
- `aria-command-addition.prompt.md` — add a new Aria runtime command or state transition.
- `vision-training.prompt.md` — configure and run vision or multimodal training.
- `cost-estimation.prompt.md` — estimate compute, storage, or API costs before execution.

## Advanced training and infrastructure prompts

- `chat-web-sse-consumer.prompt.md` — build or fix the chat-web frontend SSE streaming consumer.
- `azure-quantum-deploy.prompt.md` — deploy Azure Quantum workspace with Bicep and cost monitoring.
- `lora-rag-pipeline.prompt.md` — set up RAG pipeline with LoRA adapters.
- `deepspeed-training.prompt.md` — configure DeepSpeed Zero-3 distributed training.
- `model-serving.prompt.md` — serve a trained model via the model server.
- `github-actions-workflow.prompt.md` — create or modify a GitHub Actions workflow.
- `data-augmentation.prompt.md` — augment training data for improved generalization.
- `gpu-optimization.prompt.md` — optimize GPU memory usage and training throughput.
- `semantic-pruning.prompt.md` — apply semantic pruning to models or context.
- `cosmos-container-setup.prompt.md` — set up Cosmos DB containers and partition keys.

## High-volume pattern packs (prefix-based)

- `perf-*` — CPU/memory/I/O profiling, cache design, latency/throughput budgets.
- `data-*` — quality checks, lineage, schema evolution, dedup, late-arrival handling.
- `mon-*` — SLI/SLO, alert tuning, trace sampling, dashboards, incident timelines.
- `fe-*` — frontend state, accessibility, virtualization, error boundaries, performance budgets.
- `cfg-*` — configuration policy, schema validation, drift detection, rollout safety.
- `net-*` — timeout/retry policy, DNS/TCP tuning, ingress/egress controls, backpressure.
- `container-*` — image/runtime hardening, probe design, SBOM, vuln scanning, isolation.
- `doc-*` — RFCs, runbooks, postmortems, release notes, troubleshooting trees.
- `azure-*` — Azure cost, identity, Key Vault, monitoring, Cosmos, deployment slots.

## Prompt design conventions

- Use `Task`, `Requirements`, `Constraints`, `Success Criteria` sections.
- Make outputs verifiable (tests, checks, acceptance criteria).
- Keep tasks scoped and explicit; avoid ambiguous “improve everything” phrasing.
- Include guardrails for secrets, cost, and data immutability when relevant.
