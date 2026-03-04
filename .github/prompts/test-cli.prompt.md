```prompt
---
agent: agent
description: "Test CLI commands with argument parsing and output"
---
# CLI Tests
## Task
Write tests for command-line interface commands.
## Requirements
1. Test argument parsing with all option combinations.
2. Test stdout/stderr output content.
3. Test exit codes (0 for success, non-zero for errors).
4. Test help text generation.
5. Test invalid argument handling.
## Constraints
- Use `click.testing.CliRunner` or `subprocess` for CLI tests. Capture output.
## Success Criteria
- All CLI commands tested. Exit codes correct. Help text accurate.
```
