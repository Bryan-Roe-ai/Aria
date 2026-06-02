"""Core runtime primitives for Aria's autonomous agent system."""

if __name__ == "__main__" and __package__ in (None, ""):
    from pathlib import Path
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

    from core.agent import BaseAgent
    from core.registry import AgentRegistry
    from core.task import Task
else:
    from .agent import BaseAgent
    from .registry import AgentRegistry
    from .task import Task

__all__ = ["AgentRegistry", "BaseAgent", "Task"]
