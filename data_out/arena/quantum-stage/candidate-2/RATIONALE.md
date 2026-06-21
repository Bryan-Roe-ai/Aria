# Arena Candidate 2 — Quantum Stage UX Integration

## Approach

Candidate 2 folds quantum lab workflows into the **main Aria stage** (`index.html`) instead of treating `quantum-stage.html` as the primary surface. Patterns from the standalone quantum page—stage label, preset buttons, sample command chips, and `aria-live` status—are reused in the object-manager / control panel so users never leave the full character + Three.js experience.

Backend contracts stay unchanged: `POST /api/aria/quantum/setup`, `GET /api/aria/presets`, and `aria3D.setStageTheme()` driven by `environment.stage_style`.

## Alternatives considered

| Option | Why rejected |
|--------|----------------|
| **C1: Standalone page only** | Duplicates stage logic; users load quantum world in one tab and watch the main stage in another. Poor discoverability. |
| **Iframe embed of `quantum-stage.html`** | Two JS contexts, no shared `aria_controller` / Three.js mirror, harder to test and maintain. |
| **Client-only quantum theme (no `/quantum/setup`)** | Would not sync qubit/gate objects or run server preset actions; breaks auto-execute and AGI flows that read `stage_state`. |
| **New React/Vue panel** | Out of scope for Aria's static HTML + `aria_controller.js` architecture; adds build tooling without UX gain. |
| **Hard-coded sample chips in HTML** | Drifts from `command_presets.generated.json`; rejected in favor of fetching the Quantum Lab pack at runtime (with graceful fallback copy). |

## Design choices

1. **Stage label overlay** — Mirrors `quantum-stage.html` `#stage-label`; updated by `updateStageLabel()` when environment or presets change.
2. **Toast + aria-live** — `showToast()` for transient feedback; `#quantum-live-status` for persistent, screen-reader-friendly status (success/error classes).
3. **Three.js theme hook** — `applyServerEnvironmentState()` calls `aria3D.setStageTheme()` so CSS gradient and WebGL lighting/fog stay aligned.
4. **Auto-execute bridge** — Toolbar calls the same setup API; preset chips load from `/api/aria/presets` so Quantum Lab commands stay one source of truth.

## Verification

- Structural tests: `tests/test_aria_index_provider_wiring.py`, `tests/test_aria_auto_execute_html.py`
- Server quantum helpers: `tests/test_aria_server.py` (`setup_quantum_stage`, presets endpoint)
- Run: `.venv/bin/python -m pytest tests/test_aria_index_provider_wiring.py tests/test_aria_auto_execute_html.py tests/test_aria_server.py -k quantum --no-header -q`
