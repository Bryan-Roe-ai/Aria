"""Simple local agent with tools: search, calculator, file ops."""

from __future__ import annotations

import ast
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


_FILE_TOOL_ROOT = Path.cwd().resolve()


# ----- Tools -----
def search_tool(query: str, corpus: list[str]) -> str:
    """Return up to five corpus lines matching the query."""
    q = query.lower().strip()
    if not q:
        return "No search query provided."
    matches = [line for line in corpus if q in line.lower()]
    if not matches:
        return "No matches found."
    return "\n".join(matches[:5])


def _apply_operator(
    operator: ast.operator,
    left: float,
    right: float,
) -> float:
    """Apply a supported arithmetic operator to two numbers."""
    if isinstance(operator, ast.Add):
        return left + right
    if isinstance(operator, ast.Sub):
        return left - right
    if isinstance(operator, ast.Mult):
        return left * right
    if isinstance(operator, ast.Div):
        return left / right
    if isinstance(operator, ast.Pow):
        return left**right
    raise ValueError("Unsupported expression")


def _resolve_text_path(path: str) -> Path:
    """Resolve a file-tool path and keep it within the current working tree."""
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = _FILE_TOOL_ROOT / candidate
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(_FILE_TOOL_ROOT)
    except ValueError as exc:
        raise ValueError(f"Path must stay within {_FILE_TOOL_ROOT}") from exc
    return resolved


def _safe_eval(node: ast.AST) -> float:
    """Safely evaluate basic arithmetic expression nodes."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp):
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return _apply_operator(node.op, left, right)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_safe_eval(node.operand)
    raise ValueError("Unsupported expression")


def calculator_tool(expression: str) -> str:
    """Evaluate a simple arithmetic expression safely."""
    try:
        parsed = ast.parse(expression, mode="eval")
        result = _safe_eval(parsed.body)
        return str(result)
    except (ValueError, SyntaxError, TypeError, ZeroDivisionError) as exc:
        return f"Calculation error: {exc}"


def read_file_tool(path: str) -> str:
    """Read and return up to 2000 characters from a file."""
    try:
        p = _resolve_text_path(path)
    except ValueError as exc:
        return f"File access error: {exc}"
    if not p.exists() or not p.is_file():
        return "File not found."
    contents = p.read_text(encoding="utf-8", errors="replace")
    if len(contents) <= 2000:
        return contents
    return f"{contents[:2000]}\n...[truncated]"


def write_file_tool(path: str, content: str) -> str:
    """Write text content to a file and report the result."""
    try:
        p = _resolve_text_path(path)
    except ValueError as exc:
        return f"File access error: {exc}"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} chars to {p}"


# ----- Router / Agent -----
@dataclass
class ToolAgent:
    """Route user commands to local utility tools."""

    corpus: list[str]

    def route(self, user_input: str) -> tuple[str, Callable[..., str], tuple]:
        """Select a tool and arguments based on command prefixes."""
        text = user_input.strip()

        # search: <query>
        if text.lower().startswith("search:"):
            query = text.split(":", 1)[1].strip()
            return ("search", search_tool, (query, self.corpus))

        # calc: <expr>
        if text.lower().startswith("calc:"):
            expr = text.split(":", 1)[1].strip()
            return ("calculator", calculator_tool, (expr,))

        # read: <path>
        if text.lower().startswith("read:"):
            path = text.split(":", 1)[1].strip()
            return ("read_file", read_file_tool, (path,))

        # write: <path> | <content>
        if text.lower().startswith("write:"):
            payload = text.split(":", 1)[1].strip()
            parts = re.split(r"\s*\|\s*", payload, maxsplit=1)
            if len(parts) != 2:
                return ("error", lambda: "Use: write: <path> | <content>", ())
            return ("write_file", write_file_tool, (parts[0], parts[1]))

        help_text = (
            "Try one of:\n"
            "- search: <keyword>\n"
            "- calc: <expression>\n"
            "- read: <path>\n"
            "- write: <path> | <content>"
        )
        return (
            "help",
            lambda: help_text,
            (),
        )

    def run(self, user_input: str) -> str:
        """Execute the routed tool and format the output."""
        tool_name, fn, args = self.route(user_input)
        result = fn(*args)
        return f"[tool={tool_name}]\n{result}"


if __name__ == "__main__":
    sample_corpus = [
        "FastAPI is a modern Python web framework.",
        "Flask is a lightweight WSGI web framework.",
        "Transformers can run local language models.",
        "SQLite is useful for local structured data.",
    ]

    agent = ToolAgent(corpus=sample_corpus)
    print("Tool Agent ready. Type 'exit' to quit.")

    while True:
        user_text = input("You: ").strip()
        if user_text.lower() in {"exit", "quit"}:
            print("Bye 👋")
            break
        print(agent.run(user_text))
