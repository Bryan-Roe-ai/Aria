"""Module entrypoint so ``python -m aria_bot`` works from the repo root."""

from __future__ import annotations

from importlib import import_module

if __name__ == "__main__":
    raise SystemExit(import_module("aria_bot.cli").main())
