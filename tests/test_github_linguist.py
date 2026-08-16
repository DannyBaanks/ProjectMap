"""M3: integración GitHub Linguist honesta.

Verificado contra github-linguist/linguist (docs/overrides.md y
lib/linguist/languages.yml, 2026-08-15):
- GitHub solo consume .gitattributes commiteado con atributos linguist-*.
- Los nombres de lenguaje deben existir en languages.yml; si no, se ignoran.
- language-bar.json NO lo consume GitHub: es reporte propio de ProjectMap.
"""
from __future__ import annotations

import json
from pathlib import Path

from conftest import LINGUIST  # type: ignore[import]

from projectmap.adapters.github import apply_github_artifacts, emit_github_artifacts, linguist_name
from projectmap.scanners.analyze import analyze


def test_mapping_table_verified_languages():
    """Lenguajes del fixture con nombre Linguist real (languages.yml)."""
    assert linguist_name("python") == "Python"
    assert linguist_name("rust") == "Rust"
    assert linguist_name("cpp") == "C++"
    assert linguist_name("java") == "Java"
    assert linguist_name("cobol") == "COBOL"
    assert linguist_name("javascript") == "JavaScript"


def test_unsupported_languages_have_no_linguist_name():
    """Lenguajes que NO existen en languages.yml -> None (GitHub los ignora)."""
    assert linguist_name("malbolge") is None
    assert linguist_name("jajaja") is None
    assert linguist_name("iesy") is None
    assert linguist_name("ffi") is None


def test_export_produces_linguist_report(tmp_path: Path):
    model = analyze(LINGUIST)
    out = tmp_path / "gh"
    created = emit_github_artifacts(out, model)
    names = {p.name for p in created}
    assert "github-linguist-report.json" in names
    assert ".gitattributes" in names
    assert "language-bar.json" in names


def test_report_lists_linguist_names(tmp_path: Path):
    model = analyze(LINGUIST)
    out = tmp_path / "gh"
    emit_github_artifacts(out, model)
    rep = json.loads((out / "github-linguist-report.json").read_text(encoding="utf-8"))
    by_name = {l["name"]: l["linguist"] for l in rep["languages"]}
    assert by_name["python"] == "Python"
    assert by_name["rust"] == "Rust"
    assert by_name["cpp"] == "C++"
    assert by_name["java"] == "Java"
    assert by_name["cobol"] == "COBOL"


def test_report_lists_unsupported(tmp_path: Path):
    model = analyze(LINGUIST)
    out = tmp_path / "gh"
    emit_github_artifacts(out, model)
    rep = json.loads((out / "github-linguist-report.json").read_text(encoding="utf-8"))
    assert "malbolge" in rep["unsupported_by_linguist"]
    assert "mystery.xyzzy" in rep["files_with_unknown_language"]


def test_gitattributes_only_declared(tmp_path: Path):
    """Solo los lenguajes DECLARADOS en manifest generan override."""
    model = analyze(LINGUIST)
    out = tmp_path / "gh"
    emit_github_artifacts(out, model)
    attrs = (out / ".gitattributes").read_text(encoding="utf-8")
    assert "legacy.cob linguist-language=COBOL" in attrs
    assert "docs/api.md linguist-documentation" in attrs
    # VERIFIED por extensión: no deben aparecer como override
    assert "app.py" not in attrs
    assert "engine.rs" not in attrs
    assert "core.cpp" not in attrs
    assert "Main.java" not in attrs
    # malbolge no existe en Linguist: nunca se emite
    assert "malbolge" not in attrs


def test_gitattributes_neutral(tmp_path: Path):
    model = analyze(LINGUIST)
    out = tmp_path / "gh"
    emit_github_artifacts(out, model)
    attrs = (out / ".gitattributes").read_text(encoding="utf-8")
    assert "Danny" not in attrs and "ISyCo" not in attrs


def test_language_bar_is_projectmap_report(tmp_path: Path):
    model = analyze(LINGUIST)
    out = tmp_path / "gh"
    emit_github_artifacts(out, model)
    bar = json.loads((out / "language-bar.json").read_text(encoding="utf-8"))
    assert bar["source"] == "projectmap"
    assert "NO lo consume" in bar["note"]
    assert bar["project"] == "linguist"


def test_apply_dry_run_writes_nothing(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("x = 1\n", encoding="utf-8")
    model = analyze(repo)
    plan = apply_github_artifacts(repo, model, dry_run=True)
    assert all(a == "would-write" for a, _, _ in plan)
    assert not (repo / ".gitattributes").exists()
    assert not (repo / "github-linguist-report.json").exists()


def test_apply_writes_artifacts(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("x = 1\n", encoding="utf-8")
    model = analyze(repo)
    plan = apply_github_artifacts(repo, model, dry_run=False)
    assert all(a == "written" for a, _, _ in plan)
    assert (repo / ".gitattributes").exists()
    assert (repo / "language-bar.json").exists()
    assert (repo / "github-linguist-report.json").exists()


def test_apply_never_commits_nor_pushes(tmp_path: Path):
    """apply no toca git: no hay subprocess ni .git creado."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("x = 1\n", encoding="utf-8")
    model = analyze(repo)
    apply_github_artifacts(repo, model, dry_run=False)
    assert not (repo / ".git").exists()
