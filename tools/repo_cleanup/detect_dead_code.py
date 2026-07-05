from pathlib import Path

ROOT = Path('.')


def scan_python_files():
    for path in ROOT.rglob('*.py'):
        try:
            text = path.read_text(encoding='utf-8')
            if 'TODO' in text or 'pass' in text:
                print(f'Potential unfinished logic: {path}')
        except Exception:
            pass


if __name__ == '__main__':
    print('Scanning for potential dead or incomplete code...')
    scan_python_files()
