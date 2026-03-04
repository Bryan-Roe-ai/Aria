```prompt
---
agent: agent
description: "Set up and configure Cosmos DB containers, partition keys, and throughput"
---
# Cosmos Container Setup

## Task
Create or configure a Cosmos DB container with appropriate partition keys and throughput settings.

## Context
- Cosmos client: `shared/cosmos_client.py`
- Telemetry: `shared/telemetry.py`
- Diagnostics: `/api/ai/status` reports Cosmos connectivity
- DB logging: `shared/db_logging.py`

## Requirements
1. Design the container schema with appropriate partition key strategy.
2. Configure throughput (manual or autoscale RU/s) based on workload.
3. Implement the container setup in `shared/cosmos_client.py`.
4. Set up TTL (time-to-live) if data expiration is needed.
5. Validate connectivity via `/api/ai/status`.

## Constraints
- Cosmos credentials via env vars (`COSMOS_ENDPOINT`, `COSMOS_KEY`); never hardcode.
- Prefer point reads over cross-partition queries for performance.
- Set reasonable RU budgets to control costs.
- Use managed identity where possible instead of key-based auth.

## Success Criteria
- Container created with correct partition key.
- Throughput settings match workload expectations.
- `/api/ai/status` shows healthy Cosmos status.
- Read/write operations perform within latency targets.
```
