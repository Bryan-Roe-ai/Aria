```instructions
---
name: "Docs-Markdown"
description: "Guidance for docs/ documentation files and GitHub Pages content"
applyTo: "docs/**/*.md"
---
# Documentation – Markdown

- `docs/` contains project documentation, architecture notes, performance analyses, and GitHub Pages content.
- Subdirectories: `architecture/`, `aria/`, `chat/`, `dashboard/`, `database/`, `deployment/`, `guides/`, `quantum/`, `quickref/`, `training/`.
- `docs/index.html` and `docs/_config.yml` power the GitHub Pages site; keep them in sync.
- Performance docs are extensive; update `docs/PERFORMANCE_INDEX.md` when adding new analyses.
- Use descriptive file names with `UPPER_SNAKE_CASE` for report-style docs.
- Include a date or version reference in analysis docs for traceability.
- Cross-link related docs; avoid orphan pages.
- Keep `.nojekyll` present to disable Jekyll processing on GitHub Pages.
```
