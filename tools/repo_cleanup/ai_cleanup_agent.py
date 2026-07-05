from pathlib import Path

ROOT = Path('.')

TASKS = [
    'Detect duplicate modules',
    'Suggest large file decomposition',
    'Identify misplaced docs',
    'Recommend archive candidates',
    'Detect naming inconsistencies',
]


def analyze_repo():
    print('AI Cleanup Agent Analysis')
    print('=' * 40)

    for task in TASKS:
        print(f'- {task}')

    for path in ROOT.rglob('*.py'):
        try:
            text = path.read_text(encoding='utf-8')

            if text.count('\n') > 2000:
                print(f'[SUGGESTION] Split oversized module: {path}')

            if 'TODO' in text:
                print(f'[SUGGESTION] Review TODO markers in: {path}')

        except Exception:
            pass


if __name__ == '__main__':
    analyze_repo()
