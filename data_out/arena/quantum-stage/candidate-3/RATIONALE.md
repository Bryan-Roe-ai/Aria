# Arena Candidate 3 — Quantum Stage Integration (Test-First)

## Approach

Candidate 3 led with **structural tests** before locking implementation. Every deliverable has a corresponding assertion that reads source files or JSON directly (no browser, no GPU). Live-server checks (`/api/aria/presets`) assert the Quantum Lab pack exposes **≥5 commands**, matching the static JSON contract.

## What shipped

| Area | Change |
|------|--------|
| `command_presets.generated.json` | Quantum Lab group with five commands aligned to `setup_quantum_stage()` objects (`qubit`, `gate`) |
| `index.html` | Full stage DOM restored; Three.js r152 CDN → `aria_threejs.js` → `aria_controller.js`; Quantum Lab toolbar with presets + aria-live status |
| `aria_controller.js` | `applyServerEnvironmentState`, `syncWorldObjectsFromServer`, `loadQuantumStage`, `updateStageLabel`; wired into `hydrateStageFromServer` |
| `aria_threejs.js` | `window.aria3D.setStageTheme(stage_style)` for quantum hemi/fog/particle tuning |
| `auto-execute.html` | Fetches `/api/aria/presets` chips, Load Quantum World button, quantum nav links, fallback examples |
| Tests | `test_aria_command_presets.py` (JSON), extended wiring tests, presets endpoint ≥5 commands |

## Alternatives considered

### A — Minimal diff only (Candidate 1 style)

**Rejected:** Would wire scripts without aria-live feedback, preset chips, or script-order tests. Harder to catch regressions when index.html is large and frequently edited.

### B — UX-first from `quantum-stage.html` (Candidate 2 style)

**Partially adopted:** Stage label, live status, and sample chips mirror `quantum-stage.html` patterns, but C3 kept the same UX while requiring **stronger test coverage first** (script order, JSON parity, controller→Three.js bridge).

### C — Separate quantum-only page, no main-stage sync

**Rejected:** Plan requires controller/Three.js sync on `/`. Keeping quantum isolated in `quantum-stage.html` alone leaves dynamic objects and `stage_style` invisible on the flagship demo.

### D — Inline preset commands in HTML only

**Rejected:** Duplicates `command_presets.generated.json` and drifts from `/api/aria/presets`. Auto-execute and index load chips from the API with hardcoded fallback only on fetch failure.

## Test strategy (C3 emphasis)

1. **Static JSON** — `test_aria_command_presets.py` validates parseability, exact Quantum Lab command set, and object references.
2. **HTML/JS structure** — `test_aria_index_provider_wiring.py` asserts CDN→threejs→controller order, quantum helpers, and `aria3D.setStageTheme` delegation.
3. **Auto-execute** — `test_aria_auto_execute_html.py` asserts presets fetch, quantum toolbar, and setup POST.
4. **Server** — Existing `test_aria_server.py` quantum world/setup tests unchanged; presets endpoint test bumped to ≥5 commands.

## Verification

```bash
python3 -m unittest tests.test_aria_command_presets tests.test_aria_index_provider_wiring tests.test_aria_auto_execute_html -v
python3 -c "import tests.test_aria_server as t; t.test_generate_world_fallback_quantum_theme_includes_stage_style(); t.test_setup_quantum_stage_loads_objects_and_runs_intro()"
```

Presets endpoint test (`test_presets_endpoint_returns_curated_commands`) requires pytest + ephemeral server fixture from `tests/unit/test_aria_schema_endpoint.py`.
