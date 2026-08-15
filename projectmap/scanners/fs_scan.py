"""Scanner: recorre el repo read-only y enumera archivos relevantes.

No interpreta contenido; sólo produce una lista de (path, stat) para que los
detectors la consuman. Ignora .git y directorios de build/caches conocidos.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# Directorios a ignorar por defecto (no son código del proyecto).
_IGNORE_DIRS = {
    ".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".ruff_cache",
    ".mypy_cache", "node_modules", "target", "build", "dist", ".venv", "venv",
    ".idea", ".vscode", ".bsp", ".scala-build",
}
_IGNORE_SUFFIXES = {".pyc", ".pyo", ".class", ".o", ".obj", ".pdb", ".exe", ".dll"}


@dataclass(frozen=True)
class ScannedPath:
    path: str          # relativo al root
    suffix: str
    is_file: bool
    size: int


def scan(root: str | Path) -> list[ScannedPath]:
    root_path = Path(root).resolve()
    if not root_path.exists() or not root_path.is_dir():
        raise NotADirectoryError(f"no es un directorio: {root_path}")

    out: list[ScannedPath] = []
    for p in sorted(root_path.rglob("*")):
        # ignorar si cualquier componente del path está en _IGNORE_DIRS
        if any(part in _IGNORE_DIRS for part in p.parts):
            continue
        if p.is_file():
            if p.suffix in _IGNORE_SUFFIXES:
                continue
            try:
                size = p.stat().st_size
            except OSError:
                size = 0
            out.append(ScannedPath(
                path=str(p.relative_to(root_path)).replace("\\", "/"),
                suffix=p.suffix.lower(),
                is_file=True,
                size=size,
            ))
    return out
