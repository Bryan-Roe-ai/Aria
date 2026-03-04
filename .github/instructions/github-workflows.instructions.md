```instructions
---
name: "GitHub-Workflows"
description: "Guidance for .github/workflows/ CI/CD workflow YAML files"
applyTo: ".github/workflows/**"
---
# GitHub Workflows

- `.github/workflows/` contains GitHub Actions CI/CD pipeline definitions.
- Workflow files must be valid YAML and pass `yamllint`.
- Use descriptive `name:` fields for workflows, jobs, and steps.
- Define appropriate `on:` triggers (push, pull_request, schedule, workflow_dispatch).
- Pin action versions to full SHA or major version tag for security.
- Use GitHub Secrets for credentials; never hardcode tokens.
- Cache dependencies (`actions/cache`) to keep CI fast.
- Keep workflow files focused: one workflow per concern (CI, deploy, release, etc.).
- Use `concurrency:` to prevent duplicate workflow runs on the same branch.
- Add status badges to `README.md` for key workflows.
```
