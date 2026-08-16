"""M2: grafo de relations por imports (INFERRED/VERIFIED) y GitHub adapter."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import MEOW, MULTILANG  # type: ignore[import]

from projectmap.adapters.github import emit_github_artifacts
from projectmap.exporters.writers import to_json
from projectmap.scanners.analyze import analyze

# --- grafo ---

def test_multilang_has_inferred_imports_relations():
    """El fixture multilang tiene un .py que importa algo resolvible? No por
    defecto (es un fixture minimal), pero tests+tools son .py sueltos. Creamos
    un fixture ad-hoc aquí para testear el grafo."""
    repo = Path(__file__).resolve().parent / "fixtures" / "relrepo"
    _build_relrepo(repo)
    model = analyze(repo)
    # esperamos al menos una relation INFERRED: pkg_app -> pkg_core (import)
    imports_rels = [r for r in model.relations if r.type == "imports"]
    assert imports_rels, "se esperaba al menos una relation 'imports' inferida"
    assert any(r.source == "pkg_app" and r.target == "pkg_core" for r in imports_rels)


def test_inferred_relations_are_inferred_confidence():
    repo = Path(__file__).resolve().parent / "fixtures" / "relrepo"
    model = analyze(repo)
    for r in model.relations:
        if r.type == "imports":
            assert r.evidence[0].confidence.value in ("verified", "inferred")


def test_relations_appear_in_exported_json():
    repo = Path(__file__).resolve().parent / "fixtures" / "relrepo"
    model = analyze(repo)
    d = json.loads(to_json(model))
    assert any(r["type"] == "imports" for r in d["relations"])


def test_meow_has_imports_graph():
    if not MEOW.exists():
        pytest.skip("MEOW-ENGINE no disponible")
    model = analyze(MEOW)
    imports_rels = [r for r in model.relations if r.type == "imports"]
    assert imports_rels, "MEOW tiene imports Python; se esperaban relations"
    # todas INFERRED o VERIFIED según AST
    assert all(r.evidence[0].confidence.value in ("verified", "inferred")
               for r in imports_rels)


def test_relations_reproducible():
    repo = Path(__file__).resolve().parent / "fixtures" / "relrepo"
    a = to_json(analyze(repo))
    b = to_json(analyze(repo))
    assert a == b


# --- github adapter ---

def test_github_export_produces_artifacts(tmp_path: Path):
    model = analyze(MULTILANG)
    out = tmp_path / "gh"
    created = emit_github_artifacts(out, model)
    names = {p.name for p in created}
    assert "ARCHITECTURE.md" in names
    assert ".gitattributes" in names
    assert "language-bar.json" in names


def test_github_gitattributes_neutral(tmp_path: Path):
    model = analyze(MULTILANG)
    out = tmp_path / "gh"
    emit_github_artifacts(out, model)
    attrs = (out / ".gitattributes").read_text(encoding="utf-8")
    assert "linguist" in attrs
    assert "ProjectMap" in attrs.split("#")[1]  # cabecera neutral
    # no mete branding de autor
    assert "Danny" not in attrs and "ISyCo" not in attrs


def test_github_language_bar_neutral(tmp_path: Path):
    model = analyze(MULTILANG)
    out = tmp_path / "gh"
    emit_github_artifacts(out, model)
    bar = json.loads((out / "language-bar.json").read_text(encoding="utf-8"))
    assert bar["project"] == "multilang"
    assert len(bar["languages"]) >= 4
    # sin URLs de marca
    text = json.dumps(bar)
    assert "shields.io" not in text and "badges" not in text


def test_github_branding_opt_in(tmp_path: Path):
    model = analyze(MULTILANG)
    out = tmp_path / "gh"
    emit_github_artifacts(out, model, branding=True)
    md = (out / "ARCHITECTURE.md").read_text(encoding="utf-8")
    assert "ProjectMap" in md  # aparece al final con branding


# --- helper: construye fixture relrepo ---

def _build_relrepo(root: Path) -> None:
    (root / "pkg_app").mkdir(parents=True, exist_ok=True)
    (root / "pkg_core").mkdir(parents=True, exist_ok=True)
    (root / "pkg_app" / "main.py").write_text(
        "from pkg_core.model import X\nimport os\n", encoding="utf-8")
    (root / "pkg_core" / "model.py").write_text("X = 1\n", encoding="utf-8")
