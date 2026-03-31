#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    ROOT / 'README.md',
    ROOT / 'docs' / 'vision.md',
    ROOT / 'docs' / 'roadmap.md',
    ROOT / 'backend' / 'app' / 'main.py',
    ROOT / 'backend' / 'app' / 'models.py',
    ROOT / 'backend' / 'app' / 'storage.py',
    ROOT / 'backend' / 'requirements.txt',
    ROOT / 'firmware' / 'README.md',
    ROOT / 'assets' / 'README.md',
]
missing = [str(p.relative_to(ROOT)) for p in REQUIRED if not p.exists()]
if missing:
    print('MISSING:')
    for item in missing:
        print('-', item)
    raise SystemExit(1)
print('Skeleton OK')
