"""Tests arquitectónicos: el core NO conoce GitHub ni MEOW.

Veta imports reales (no strings ni comentarios) que rompan la frontera.
"""
from __future__ import annotations

import ast
from pathlib import Path

import projectmap

CORE = Path(projectmap.__file__).resolve().parent


def _imported_modules(tree: ast.AST) -> set[str]:
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                mods.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module.split(".")[0])
    return mods


def _scan_forbidden_imports(dirs, forbidden):
    offenders = []
    for d in dirs:
        for py in d.rglob("*.py"):
            try:
                tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
            except SyntaxError:
                continue
            imported = _imported_modules(tree)
            bad = imported & forbidden
            if bad:
                offenders.append((py.name, sorted(bad)))
    return offenders


def test_core_does_not_import_github():
    offenders = _scan_forbidden_imports([CORE], {"github", "PyGithub", "octokit", "gh"})
    assert offenders == [], f"core importa GitHub: {offenders}"


def test_core_does_not_import_meow():
    offenders = _scan_forbidden_imports([CORE], {"meow", "gladiator", "jajaja", "caesar", "harness"})
    assert offenders == [], f"core importa MEOW: {offenders}"


def test_core_does_not_import_network():
    offenders = _scan_forbidden_imports([CORE], {"requests", "httpx", "socket", "http", "aiohttp", "urllib"})
    assert offenders == [], f"core hace red: {offenders}"


def test_scan_does_not_write(tmp_path):
    """scan() sobre un repo dummy no crea ni borra archivos dentro del repo."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "a.py").write_text("x=1", encoding="utf-8")
    before = sorted(p.name for p in repo.rglob("*"))
    from projectmap.scanners.analyze import analyze
    analyze(repo)
    after = sorted(p.name for p in repo.rglob("*"))
    assert before == after, "scan modificó el repo (no es read-only)"
