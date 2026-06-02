"""Shared registries for the deterministic aria-bot loop.

Keep the supported finding kinds in one place so the analyzer, executor,
and tests all agree on the same safe surface area.
"""

from __future__ import annotations

# Keep this tuple small and deterministic: every supported finding kind
# must have a matching pure text transform in the executor.
TRANSFORM_ORDER: tuple[str, ...] = (
    "utf8_bom",
    "mixed_line_endings",
    "trailing_whitespace",
    "trailing_blank_lines",
    "missing_final_newline",
)

# Supported kinds share the same stable canonical order.
SUPPORTED_FINDING_KINDS: tuple[str, ...] = TRANSFORM_ORDER
