"""Small SQL connectivity demo using the shared SQL engine helper."""

import sys
from pathlib import Path
from typing import Any, Protocol, cast

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# pylint: disable=wrong-import-position
import shared.sql_engine as se  # noqa: E402


class EngineLike(Protocol):
    """Minimal protocol used by this demo."""

    def connect(self) -> Any:
        """Open a DB connection context manager."""


def main() -> None:
    """Run a minimal `SELECT 1` query and print the result."""
    engine = se.get_engine()
    if engine is None or not hasattr(engine, "connect"):
        print("No SQL engine available")
        return
        return

    typed_engine = cast(EngineLike, engine)
    with typed_engine.connect() as conn:
        result = conn.execute(se.text("SELECT 1"))
        val = result.scalar_one()
        print(f"SQL demo query returned: {val}")

        print(f"SQL demo query returned: {val}")
    main()
