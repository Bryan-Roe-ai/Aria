#!/usr/bin/env python3
"""Extensible custom validation rules framework for auto-improve.

This module defines a plugin-based system for custom validation rules.
Rules are automatically discovered and executed as part of health check cycles.

Creating a custom rule:
    1. Create a class inheriting from ValidationRule
    2. Implement `validate()` method that returns a list of
       ValidationIssue objects
    3. Place in rules/ directory or register manually with RuleRegistry

Example custom rule:

    from custom_validation_rules import ValidationRule, ValidationIssue

    class MyCustomRule(ValidationRule):
        name = "my-custom-rule"
        category = "custom"
        description = "Check something specific"

        def validate(self):
            issues = []
            if some_condition_fails():
                issues.append(
                    ValidationIssue(
                        severity="medium",
                        message="Something is wrong",
                        file="path/to/file",
                        remediation="Fix the thing"
                    )
                )
            return issues

    # Register
    from custom_validation_rules import registry
    registry.register(MyCustomRule())

Usage:
    python scripts/custom_validation_rules.py --list
    python scripts/custom_validation_rules.py --run
    python scripts/custom_validation_rules.py --run --rules my-rule,other-rule
"""

from __future__ import annotations

import argparse
import json
import sys
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class ValidationIssue:
    """Represents a validation issue found by a rule."""

    severity: str  # "low", "medium", "high", "critical"
    message: str
    file: str | None = None
    line: int | None = None
    rule: str | None = None
    remediation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            k: v for k, v in asdict(self).items() if v is not None
        }


class ValidationRule(ABC):
    """Base class for custom validation rules."""

    name: str
    category: str  # "code", "config", "security", "performance", "custom"
    description: str
    severity: str = "medium"  # default severity for this rule's issues

    @abstractmethod
    def validate(self) -> list[ValidationIssue]:
        """Run validation and return list of issues.

        Returns:
            List of ValidationIssue objects
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"


class RuleRegistry:
    """Registry for validation rules."""

    def __init__(self) -> None:
        self._rules: dict[str, ValidationRule] = {}

    def register(self, rule: ValidationRule) -> None:
        """Register a validation rule."""
        if rule.name in self._rules:
            print(f"⚠️  Overwriting rule: {rule.name}")
        self._rules[rule.name] = rule

    def unregister(self, name: str) -> None:
        """Unregister a validation rule."""
        if name in self._rules:
            del self._rules[name]

    def get(self, name: str) -> ValidationRule | None:
        """Get a rule by name."""
        return self._rules.get(name)

    def list_all(self) -> dict[str, ValidationRule]:
        """List all registered rules."""
        return dict(self._rules)

    def run_all(self) -> list[ValidationIssue]:
        """Run all rules and collect issues."""
        issues: list[ValidationIssue] = []
        for rule in self._rules.values():
            try:
                rule_issues = rule.validate()
                for issue in rule_issues:
                    if issue.rule is None:
                        issue.rule = rule.name
                    issues.append(issue)
            except (OSError, ValueError, TypeError) as e:
                print(f"❌ Rule {rule.name} failed: {e}", file=sys.stderr)

        return issues

    def run_subset(self, names: list[str]) -> list[ValidationIssue]:
        """Run a subset of rules."""
        issues: list[ValidationIssue] = []
        for name in names:
            rule = self.get(name)
            if rule is None:
                print(f"⚠️  Rule not found: {name}", file=sys.stderr)
                continue

            try:
                rule_issues = rule.validate()
                for issue in rule_issues:
                    if issue.rule is None:
                        issue.rule = rule.name
                    issues.append(issue)
            except (OSError, ValueError, TypeError) as e:
                print(f"❌ Rule {name} failed: {e}", file=sys.stderr)

        return issues


# Global registry
registry = RuleRegistry()


# ============================================================================
# Built-in Rules
# ============================================================================


class NoHardcodedSecretsRule(ValidationRule):
    """Check for hardcoded secrets in Python files."""

    name = "no-hardcoded-secrets"
    category = "security"
    description = "Detect hardcoded API keys, tokens, passwords"
    severity = "critical"

    def validate(self) -> list[ValidationIssue]:
        issues = []
        secret_patterns = [
            ("password =", "hardcoded password"),
            ("api_key =", "hardcoded API key"),
            ("secret =", "hardcoded secret"),
            ("token =", "hardcoded token"),
        ]

        for py_file in REPO_ROOT.rglob("*.py"):
            if any(
                part in py_file.parts
                for part in [".venv", ".git", "node_modules", "__pycache__"]
            ):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        for pattern, description in secret_patterns:
                            if pattern in line.lower():
                                issues.append(
                                    ValidationIssue(
                                        severity="critical",
                                        message=f"Found {description}",
                                        file=str(
                                            py_file.relative_to(REPO_ROOT)
                                        ),
                                        line=line_num,
                                        remediation=(
                                            "Use environment variables "
                                            "instead"
                                        ),
                                    )
                                )
            except (OSError, UnicodeDecodeError):
                pass

        return issues


class RequirementsConsistencyRule(ValidationRule):
    """Check consistency between requirements files."""

    name = "requirements-consistency"
    category = "config"
    description = (
        "Validate requirements.txt vs constraints.txt "
        "vs pyproject.toml"
    )

    def validate(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        requirements_file = REPO_ROOT / "requirements.txt"
        constraints_file = REPO_ROOT / "constraints.txt"

        if not requirements_file.exists():
            return issues

        # Check if both exist
        if constraints_file.exists():
            try:
                req_set = set()
                con_set = set()

                with open(requirements_file, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            req_set.add(
                                line.split("==")[0]
                                .split(">=")[0]
                                .lower()
                            )

                with open(constraints_file, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            con_set.add(
                                line.split("==")[0]
                                .split(">=")[0]
                                .lower()
                            )

                # Check for overlap
                overlap = req_set & con_set
                if overlap:
                    issues.append(
                        ValidationIssue(
                            severity="low",
                            message=(
                                "Requirements and constraints overlap: "
                                f"{', '.join(overlap)}"
                            ),
                            file="requirements.txt",
                            remediation=(
                                "Remove overlapping packages "
                                "from one file"
                            ),
                        )
                    )
            except OSError:
                pass

        return issues


class DocstringCoverageRule(ValidationRule):
    """Check docstring coverage in Python modules."""

    name = "docstring-coverage"
    category = "code"
    description = "Ensure functions/classes have docstrings"

    def validate(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        # This is a simplified check; could use ast module for better coverage
        py_files = list(REPO_ROOT.glob("scripts/*.py"))

        for py_file in py_files:
            if py_file.name.startswith("_"):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                    # Count functions/classes without docstrings (basic check)
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if line.strip().startswith("def "):
                            if (
                                i + 1 < len(lines)
                                and '"""' not in lines[i + 1]
                            ):
                                if "# " not in lines[i + 1]:
                                    # Skip if next line has inline comment
                                    issues.append(
                                        ValidationIssue(
                                            severity="low",
                                            message=(
                                                "Function missing docstring"
                                            ),
                                            file=str(
                                                py_file.relative_to(REPO_ROOT)
                                            ),
                                            line=i + 1,
                                            remediation=(
                                                "Add docstring to function"
                                            ),
                                        )
                                    )
            except (OSError, UnicodeDecodeError):
                pass

        return issues


class ConfigValidationRule(ValidationRule):
    """Validate YAML configuration files."""

    name = "config-validation"
    category = "config"
    description = "Check YAML configs for schema compliance"

    def validate(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError:
            return issues

        config_dir = REPO_ROOT / "config"
        if not config_dir.exists():
            return issues

        for yaml_file in config_dir.rglob("*.yaml"):
            try:
                with open(yaml_file, encoding="utf-8") as f:
                    yaml.safe_load(f)
            except yaml.YAMLError as e:
                issues.append(
                    ValidationIssue(
                        severity="high",
                        message=f"Invalid YAML: {e}",
                        file=str(yaml_file.relative_to(REPO_ROOT)),
                        remediation="Fix YAML syntax",
                    )
                )
            except OSError:
                pass

        return issues


# Register built-in rules
registry.register(NoHardcodedSecretsRule())
registry.register(RequirementsConsistencyRule())
registry.register(DocstringCoverageRule())
registry.register(ConfigValidationRule())


def format_issues_report(issues: list[ValidationIssue]) -> str:
    """Format issues for display."""
    if not issues:
        return "✅ No issues found"

    severity_icon = {
        "low": "ℹ️",
        "medium": "⚠️",
        "high": "🚨",
        "critical": "🔴",
    }

    lines = [f"Found {len(issues)} issue(s):\n"]

    by_severity: dict[str, list[ValidationIssue]] = {}
    for issue in issues:
        sev = issue.severity
        if sev not in by_severity:
            by_severity[sev] = []
        by_severity[sev].append(issue)

    for severity in ["critical", "high", "medium", "low"]:
        if severity not in by_severity:
            continue

        icon = severity_icon.get(severity, "❓")
        lines.append(f"{icon} {severity.upper()}:")

        for issue in by_severity[severity]:
            file_info = f"{issue.file}" if issue.file else "unknown"
            if issue.line:
                file_info += f":{issue.line}"

            lines.append(f"  • [{file_info}] {issue.message}")
            if issue.remediation:
                lines.append(f"    → {issue.remediation}")

    return "\n".join(lines)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Custom validation rules framework"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all registered rules",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Run all rules",
    )
    parser.add_argument(
        "--rules",
        type=str,
        help="Run specific rules (comma-separated)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    args = parser.parse_args()

    if args.list:
        rules = registry.list_all()
        if not rules:
            print("No rules registered")
            return 0

        print(f"Registered rules ({len(rules)}):\n")
        for name, rule in sorted(rules.items()):
            print(f"  • {name} ({rule.category})")
            print(f"    {rule.description}")

        return 0

    if args.run:
        if args.rules:
            issues = registry.run_subset(args.rules.split(","))
        else:
            issues = registry.run_all()

        if args.json:
            print(json.dumps([issue.to_dict() for issue in issues], indent=2))
        else:
            print(format_issues_report(issues))

        return 1 if issues else 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
