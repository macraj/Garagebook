#!/usr/bin/env python3
"""
build_dist.py — Garagebook distribution builder
=================================================

Tworzy gotowy do instalacji ZIP dla wybranej platformy.

Użycie:
    python3 dev/build_dist.py              # tryb interaktywny
    python3 dev/build_dist.py macos        # ZIP dla macOS
    python3 dev/build_dist.py windows      # ZIP dla Windows
    python3 dev/build_dist.py linux        # ZIP dla Linux
    python3 dev/build_dist.py all          # ZIP dla wszystkich platform

Wynik (w katalogu dist/):
    Garagebook-macos-YYYY-MM-DD.zip
    Garagebook-windows-YYYY-MM-DD.zip
    Garagebook-linux-YYYY-MM-DD.zip
"""

import os
import sys
import zipfile
from pathlib import Path
from datetime import date

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT     = Path(__file__).parent.parent.resolve()
DIST_DIR = ROOT / 'dist'

# ── Colors ─────────────────────────────────────────────────────────────────────
_USE_COLOR = sys.platform != 'win32' or os.environ.get('ANSICON')
class C:
    G    = '\033[32m'  if _USE_COLOR else ''
    Y    = '\033[33m'  if _USE_COLOR else ''
    R    = '\033[31m'  if _USE_COLOR else ''
    B    = '\033[34m'  if _USE_COLOR else ''
    BOLD = '\033[1m'   if _USE_COLOR else ''
    N    = '\033[0m'   if _USE_COLOR else ''

def _die(msg: str):
    print(f'\n{C.R}✗ {msg}{C.N}\n')
    sys.exit(1)

def _ok(msg: str):
    print(f'  {C.G}✓{C.N} {msg}')

def _info(msg: str):
    print(f'  {C.B}►{C.N} {msg}')

def _warn(msg: str):
    print(f'  {C.Y}⚠{C.N} {msg}')

# ── Platform config ────────────────────────────────────────────────────────────
PLATFORMS = {
    'macos': {
        'name':        'macOS',
        'launchers':   ['Garagebook.command'],
        'scripts_dir': 'scripts/macos',
        'extra':       ['start.sh'],
    },
    'windows': {
        'name':        'Windows',
        'launchers':   ['Garagebook.bat'],
        'scripts_dir': 'scripts/windows',
        'extra':       [],
    },
    'linux': {
        'name':        'Linux',
        'launchers':   ['Garagebook.sh'],
        'scripts_dir': 'scripts/linux',
        'extra':       ['start.sh'],
    },
}

# ── File collection ────────────────────────────────────────────────────────────

# Pliki wspólne dla wszystkich platform
COMMON_FILES = [
    'main.py',
    'pyproject.toml',
    'uv.lock',
    'INSTRUKCJA.md',
    'INSTALACJA.txt',
]

# Katalogi skanowane rekurencyjnie
COMMON_TREES = {
    'db': {'.py', '.sql'},
    'ui': {'.py'},
}

# Pliki i katalogi których NIGDY nie dodajemy
EXCLUDE_NAMES = {
    '.DS_Store', '.gitignore', 'CLAUDE.md', 'garagebook.db',
    '__pycache__', '.git', '.venv', 'dist', 'dev', 'backups',
    '.claude', '.deps_installed',
}


def collect_files(platform: str) -> list[tuple[Path | None, str]]:
    """Zwraca listę (source_path, dest_in_zip)."""
    Z = 'Garagebook'
    result: list[tuple[Path | None, str]] = []

    def add(rel: str):
        p = ROOT / rel
        if p.exists():
            result.append((p, f'{Z}/{rel}'))
        else:
            _warn(f'Plik nie znaleziony, pomijam: {rel}')

    def add_tree(rel_dir: str, exts: set[str]):
        d = ROOT / rel_dir
        if not d.exists():
            _warn(f'Katalog nie znaleziony, pomijam: {rel_dir}')
            return
        for f in sorted(d.rglob('*')):
            if not f.is_file():
                continue
            if any(part in EXCLUDE_NAMES for part in f.parts):
                continue
            if f.suffix.lower() not in exts:
                continue
            result.append((f, f'{Z}/{f.relative_to(ROOT).as_posix()}'))

    # Wspólne pliki
    for f in COMMON_FILES:
        add(f)

    # Wspólne drzewa katalogów
    for tree_dir, exts in COMMON_TREES.items():
        add_tree(tree_dir, exts)

    # Pliki specyficzne dla platformy
    plats = list(PLATFORMS.keys()) if platform == 'all' else [platform]
    for p in plats:
        cfg = PLATFORMS[p]
        for launcher in cfg['launchers']:
            add(launcher)
        add_tree(cfg['scripts_dir'], {'.sh', '.bat', '.command', '.ps1'})
        for extra in cfg['extra']:
            add(extra)

    return result


# ── ZIP creation ───────────────────────────────────────────────────────────────

def create_zip(platform: str) -> Path:
    """Tworzy ZIP dla jednej platformy. Zwraca ścieżkę do pliku."""
    cfg      = PLATFORMS[platform]
    today    = date.today().isoformat()
    zip_name = f'Garagebook-{platform}-{today}.zip'
    zip_path = DIST_DIR / zip_name

    _info(f'Buduję paczkę dla {cfg["name"]}...')

    files = collect_files(platform)
    seen  = set()

    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for src, dest in files:
            if dest in seen:
                continue
            seen.add(dest)

            if src is None:
                zf.writestr(dest, '')
            else:
                zf.write(src, dest)

        # Ustaw bit wykonywalny dla plików .sh i .command w ZIPie
        for item in zf.infolist():
            if item.filename.endswith(('.sh', '.command')):
                item.external_attr = 0o755 << 16

    size_kb  = zip_path.stat().st_size / 1024
    size_str = f'{size_kb:.0f} KB' if size_kb < 1024 else f'{size_kb / 1024:.1f} MB'
    count    = len([f for f in files if f[0] is not None])
    _ok(f'{zip_name}  ({size_str}, {count} plików)')
    return zip_path


# ── Main ───────────────────────────────────────────────────────────────────────

def ask_platform() -> str:
    print(f'\n{C.BOLD}Garagebook — builder dystrybucji{C.N}')
    print('─' * 40)
    print('  1) macOS')
    print('  2) Windows')
    print('  3) Linux')
    print('  4) Wszystkie platformy')
    print()
    while True:
        choice = input('Wybierz platformę [1-4]: ').strip()
        mapping = {
            '1': 'macos', '2': 'windows', '3': 'linux', '4': 'all',
            'macos': 'macos', 'windows': 'windows', 'linux': 'linux', 'all': 'all',
        }
        if choice in mapping:
            return mapping[choice]
        print('  Podaj liczbę od 1 do 4.')


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg not in (*PLATFORMS.keys(), 'all'):
            _die(f'Nieznana platforma: "{arg}". Dostępne: macos, windows, linux, all')
        platform = arg
    else:
        platform = ask_platform()

    print()
    DIST_DIR.mkdir(exist_ok=True)

    built: list[Path] = []
    targets = list(PLATFORMS.keys()) if platform == 'all' else [platform]
    for p in targets:
        z = create_zip(p)
        built.append(z)

    print()
    print(f'{C.G}{C.BOLD}  ✓ Gotowe!{C.N}  Pliki w katalogu: {DIST_DIR.relative_to(ROOT)}/')
    print()
    for z in built:
        print(f'    {z.name}')
    print()


if __name__ == '__main__':
    main()
