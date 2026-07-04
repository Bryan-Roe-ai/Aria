"""
LM Studio Code Analysis Module.

Provides utilities for code analysis, documentation generation, and
testing via LM Studio.
"""

import json
import os
import subprocess
from pathlib import Path


class LMStudioAnalyzer:
    """Helper class for code analysis via LM Studio"""

    def __init__(self, base_url: str | None = None, model: str | None = None, timeout: int = 90):
        self.repo_root = self._find_repo_root()
        self._load_local_env_defaults()
        self.base_url = base_url or os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1")
        self.model = model or os.getenv("LMSTUDIO_MODEL")
        self.timeout = timeout
        self.chat_cli = self.repo_root / "ai-projects/chat-cli/src/chat_cli.py"
        self.venv_python = self.repo_root / ".venv/bin/python"

    def _find_repo_root(self) -> Path:
        """Find the Aria repository root."""
        current = Path(__file__).resolve()
        while current != current.parent:
            if (current / "ai-projects").exists() and (current / "function_app.py").exists():
                return current
            current = current.parent
        raise RuntimeError("Could not find Aria repository root")

    def _query_lmstudio(self, prompt: str, timeout: int | None = None) -> str:
        """Send query to LM Studio and return response"""
        env = os.environ.copy()
        env["LMSTUDIO_BASE_URL"] = self.base_url
        if self.model:
            env["LMSTUDIO_MODEL"] = self.model
        effective_timeout = timeout if timeout is not None else self.timeout

        cmd = [
            str(self.venv_python),
            str(self.chat_cli),
            "--provider",
            "lmstudio",
            "--no-stream",
            "--once",
            prompt,
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=effective_timeout, env=env, cwd=str(self.repo_root)
            )

            if result.returncode != 0:
                return f"Error: {result.stderr}"

            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return "Error: Query timeout (LM Studio may not be running)"
        except Exception as e:
            return f"Error: {str(e)}"

    def _load_local_env_defaults(self) -> None:
        """Load LM Studio defaults from .env/local.settings.json when unset."""
        env_path = self.repo_root / ".env"
        if env_path.exists():
            for raw_line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                if not key:
                    continue
                value = value.strip().strip('"').strip("'")
                os.environ.setdefault(key, value)

        settings_path = self.repo_root / "local.settings.json"
        if settings_path.exists():
            try:
                payload = json.loads(settings_path.read_text(encoding="utf-8", errors="ignore"))
            except json.JSONDecodeError:
                payload = {}
            values = payload.get("Values", {}) if isinstance(payload, dict) else {}
            if isinstance(values, dict):
                for key, value in values.items():
                    if isinstance(key, str) and isinstance(value, str):
                        os.environ.setdefault(key.strip(), value)

    def analyze_code(self, code: str, language: str = "python") -> str:
        """Analyze code for bugs and improvements."""
        prompt = f"""Analyze this {language} code for:
1. Bugs and potential errors
2. Performance issues
3. Security concerns
4. Code quality improvements

Be concise and actionable.

Code:
{code}"""
        return self._query_lmstudio(prompt)

    def generate_docstring(self, code: str, language: str = "python") -> str:
        """Generate comprehensive docstring and comments."""
        prompt = f"""Generate detailed documentation for this {language} code:
1. Docstring with description, parameters, returns, raises
2. Inline comments explaining complex logic
3. Type hints if not present

Code:
{code}"""
        return self._query_lmstudio(prompt)

    def generate_tests(self, code: str, language: str = "python") -> str:
        """Generate unit tests for code."""
        test_framework = "pytest" if language == "python" else "jest"
        prompt = f"""Write comprehensive {test_framework} tests for this
{language} code:
1. Normal cases
2. Edge cases
3. Error handling
4. Use realistic test data

Code:
{code}"""
        return self._query_lmstudio(prompt)

    def refactor_code(self, code: str, language: str = "python") -> str:
        """Suggest refactoring improvements."""
        prompt = f"""Refactor this {language} code to be:
1. More readable and maintainable
2. Better performance
3. More Pythonic (or idiomatic for the language)
4. Properly documented

Provide the refactored code with explanations.

Current Code:
{code}"""
        return self._query_lmstudio(prompt)

    def debug_error(self, error_msg: str, context: str | None = None) -> str:
        """Help debug an error."""
        prompt = f"""Help me debug this error. Provide:
1. Root cause analysis
2. Step-by-step fix
3. Prevention tips

Error: {error_msg}"""
        if context:
            prompt += f"\n\nContext: {context}"

        return self._query_lmstudio(prompt)

    def design_solution(self, problem: str) -> str:
        """Design an architectural solution."""
        prompt = f"""Design a solution for this problem. Include:
1. High-level architecture
2. Component breakdown
3. Data flow
4. Implementation considerations
5. Potential issues

Problem: {problem}"""
        return self._query_lmstudio(prompt)

    def explain_concept(self, concept: str, context: str | None = None) -> str:
        """Explain a concept in simple terms."""
        prompt = f"""Explain '{concept}' clearly:
1. Simple explanation
2. Practical examples
3. How it relates to Aria project
4. Common pitfalls"""
        if context:
            prompt += f"\n\nContext: {context}"
        return self._query_lmstudio(prompt)

    def review_code(self, code: str, language: str = "python") -> str:
        """Perform a structured code review."""
        prompt = f"""Review this {language} code as a senior engineer:
1. Correctness — logic errors, off-by-one, unhandled cases
2. Security — input validation, injection risks, secrets in code
3. Readability — naming, structure, comments
4. Performance — unnecessary allocations, N+1 queries
5. Verdict — approve / request changes, summarise in one sentence

Code:
{code}"""
        return self._query_lmstudio(prompt)

    def summarize_file(self, code: str, language: str = "python") -> str:
        """Return a concise summary of what a file does."""
        prompt = f"""Summarise this {language} file in 3-5 sentences:
- What does it do?
- What are its main exports/entry points?
- Any notable dependencies or side-effects?

Code:
{code}"""
        return self._query_lmstudio(prompt)

    def query(self, prompt: str) -> str:
        """Send a raw prompt to LM Studio."""
        return self._query_lmstudio(prompt)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="LM Studio Code Analyzer")
    parser.add_argument(
        "command",
        choices=[
            "analyze",
            "docs",
            "tests",
            "refactor",
            "debug",
            "design",
            "explain",
            "review",
            "summary",
            "query",
        ],
    )
    parser.add_argument("input", help="Code/error/concept to analyze")
    parser.add_argument("--language", default="python", help="Programming language")
    parser.add_argument("--context", help="Additional context")
    parser.add_argument(
        "--url",
        default=os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1"),
        help="LM Studio URL",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("LMSTUDIO_MODEL"),
        help="LM Studio model id (e.g. openai/gpt-oss-20b)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.getenv("LMSTUDIO_TIMEOUT", "90")),
        help="Request timeout in seconds (default: 90)",
    )

    args = parser.parse_args()

    analyzer = LMStudioAnalyzer(args.url, args.model, args.timeout)

    # Check if input is a file
    input_path = Path(args.input)
    if input_path.is_file():
        input_text = input_path.read_text()
    else:
        input_text = args.input

    if args.command == "analyze":
        result = analyzer.analyze_code(input_text, args.language)
    elif args.command == "docs":
        result = analyzer.generate_docstring(input_text, args.language)
    elif args.command == "tests":
        result = analyzer.generate_tests(input_text, args.language)
    elif args.command == "refactor":
        result = analyzer.refactor_code(input_text, args.language)
    elif args.command == "debug":
        result = analyzer.debug_error(input_text, args.context)
    elif args.command == "design":
        result = analyzer.design_solution(input_text)
    elif args.command == "explain":
        result = analyzer.explain_concept(input_text, args.context)
    elif args.command == "review":
        result = analyzer.review_code(input_text, args.language)
    elif args.command == "summary":
        result = analyzer.summarize_file(input_text, args.language)
    elif args.command == "query":
        result = analyzer.query(input_text)

    print(result)


if __name__ == "__main__":
    main()
