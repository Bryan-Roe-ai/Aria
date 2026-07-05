"""Simple local agent with tools: search, calculator, file ops."""

from __future__ import annotations

import ast
import operator as op
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


# ----- Tools -----
def search_tool(query: str, corpus: list[str]) -> str:
    q = query.lower().strip()
    if not q:
        return "No search query provided."
    matches = [line for line in corpus if q in line.lower()]
    if not matches:
        return "No matches found."
    return "\n".join(matches[:5])


_ALLOWED_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return _ALLOWED_OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Unsupported expression")


def calculator_tool(expression: str) -> str:
    try:
        parsed = ast.parse(expression, mode="eval")
        result = _safe_eval(parsed.body)
        return str(result)
    except (ValueError, SyntaxError, TypeError, ZeroDivisionError) as exc:
        return f"Calculation error: {exc}"


def read_file_tool(path: str) -> str:
    p = Path(path)
    if not p.exists() or not p.is_file():
        return "File not found."
    return p.read_text(encoding="utf-8", errors="replace")[:2000]


def write_file_tool(path: str, content: str) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} chars to {p}"


# ----- Router / Agent -----
@dataclass
class ToolAgent:
    corpus: list[str]

    def route(self, user_input: str) -> tuple[str, Callable[..., str], tuple]:
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

        return (
            "help",
            lambda: (
                "Try one of:\n- search: <keyword>\n- calc: <expression>\n- read: <path>\n- write: <path> | <content>"
            ),
            (),
        )

    def run(self, user_input: str) -> str:
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
