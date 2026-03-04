```prompt
---
agent: agent
description: "Build a CLI with argparse including subcommands, validation, and help text"
---
# Argparse CLI

## Task
Build a command-line interface using argparse with subcommands and validation.

## Requirements
1. Define a main parser with global arguments.
2. Add subcommands using `add_subparsers`.
3. Add argument validation with `type` and `choices`.
4. Include comprehensive help text and examples.
5. Handle errors with user-friendly messages.

## Constraints
- Use `argparse` for standard CLIs; consider `click` for complex ones.
- Add `--dry-run` and `--verbose` flags where appropriate.
- Support both positional and optional arguments.

## Success Criteria
- CLI is self-documenting with `--help`.
- Invalid arguments produce clear error messages.
- Subcommands are logically organized.
```
