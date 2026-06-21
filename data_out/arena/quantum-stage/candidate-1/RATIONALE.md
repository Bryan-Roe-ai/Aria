# Arena Candidate 1 — Quantum Stage Integration Rationale

## Approach

Minimal-diff extension of existing Aria stage files. No new HTML pages; wire quantum world setup through existing `/api/aria/quantum/setup`, preset chips via `/api/aria/presets`, and client sync helpers already present in `aria_controller.js` / `aria_threejs.js`.

## Alternatives considered

| Alternative | Summary | Verdict |
|-------------|---------|---------|
| **C2 — Dedicated quantum SPA** | New standalone page with full AGI chat + stage (expand `quantum-stage.html` into primary UX) | Rejected for C1: violates smallest-diff constraint; duplicates stage markup already in `index.html` |
| **C3 — Server-driven HTML fragments** | Server injects quantum toolbar/chips via templating or `/api/aria/fragments` | Rejected: adds server complexity and a new API surface; static HTML + fetch is sufficient |
| **Iframe embed** | Embed `quantum-stage.html` in main index via iframe | Rejected: breaks shared DOM/state sync (`applyServerEnvironmentState`, object registry) |
| **Inline preset hardcoding only** | Skip `/api/aria/presets` fetch; hardcode all Quantum Lab commands in HTML | Rejected: diverges from generated preset contract and auto-execute pattern; kept as silent fallback only |
| **Bundled Three.js** | Vendor `three.min.js` into repo instead of CDN | Rejected for C1: CDN r152 matches existing `aria_threejs.js` references; avoids binary churn |

## Tradeoffs accepted (C1)

1. **Large `index.html` diff** — Restoring the full stage from `docs/aria/index.html` inflates the file, but avoids maintaining two divergent stage implementations and keeps one command box + character DOM for controller reuse.

2. **CDN dependency** — Three.js r152 loaded from jsDelivr; offline dev needs network once for 3D path (2D CSS stage still works).

3. **Dual quantum entry points** — Main stage toolbar (`loadQuantumStage`) and auto-execute button (`loadQuantumWorld`) both POST to the same endpoint; auto-execute does not live-sync the main stage DOM (by design — separate pages). Users open `/` after loading from auto-execute.

4. **Preset chips duplicated logic** — `index.html` and `auto-execute.html` each fetch `/api/aria/presets` with similar chip rendering; acceptable to avoid extracting a shared module (no new JS files per C1 scope).

5. **Structural tests only** — Wiring verified via string-presence tests in `test_aria_index_provider_wiring.py` and presets API test in `test_aria_schema_endpoint.py`; no browser E2E in this candidate.

## Files touched

- `apps/aria/command_presets.generated.json` — Quantum Lab group (5 commands)
- `apps/aria/index.html` — Full stage + provider controls + Three.js + quantum toolbar/chips
- `apps/aria/auto-execute.html` — Preset chips, Load Quantum World, nav links
- `apps/aria/aria_controller.js` — `loadQuantumStage`, environment/object sync, live status hooks
- `apps/aria/aria_threejs.js` — `setStageTheme` quantum palette
- `tests/test_aria_index_provider_wiring.py`, `tests/unit/test_aria_schema_endpoint.py` — Regression guards

## Verification

```bash
python3 -m pytest tests/test_aria_index_provider_wiring.py tests/unit/test_aria_schema_endpoint.py -v
```

All 13 tests pass (8 wiring + 5 schema/presets).
