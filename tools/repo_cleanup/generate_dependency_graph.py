from pathlib import Path
import ast

ROOT = Path('.')
OUT = ROOT / 'docs' / 'reports'
OUT.mkdir(parents=True, exist_ok=True)

report = OUT / 'dependency-graph.md'

with report.open('w', encoding='utf-8') as f:
    f.write('# Dependency Graph\n\n')

    for path in ROOT.rglob('*.py'):
        try:
            tree = ast.parse(path.read_text(encoding='utf-8'))
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        imports.append(n.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            f.write(f'## {path}\n')
            for imp in sorted(set(imports)):
                f.write(f'- {imp}\n')
            f.write('\n')
        except Exception:
            pass

print(f'Generated {report}')
