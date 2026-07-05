import sys
from pathlib import Path

# Ensure the repository root is on PYTHONPATH so that the `shared` package can be imported.
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))
import shared.sql_engine as se


def main():
    engine = se.get_engine()
    if not engine:
        print("No SQL engine available")
        return
    with engine.connect() as conn:
        result = conn.execute(se.text("SELECT 1"))
        val = result.scalar_one()
        print(f"SQL demo query returned: {val}")


if __name__ == "__main__":
    main()
