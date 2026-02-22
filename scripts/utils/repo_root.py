from pathlib import Path


def get_repo_root(start: Path | None = None) -> Path:
    """Return repository root by walking up until .git is found.

    Prioritises .git over other markers because subdirectories (e.g.
    scripts/) may also contain README.md files.
    """
    current = Path(start or __file__).resolve()
    # First pass: look for .git (definitive repo root marker)
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate if candidate.name != ".git" else candidate.parent
    # Fallback: look for function_app.py (workspace-level marker)
    for candidate in (current, *current.parents):
        if (candidate / "function_app.py").exists():
            return candidate
    return current
