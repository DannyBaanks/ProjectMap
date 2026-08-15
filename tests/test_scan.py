"""MILESTONE 001: scan reproducible y modela correctamente los fixtures.

same input -> same model (salvo metadata temporal explícita).
El core NO importa MEOW ni GitHub (test arquitectónico aparte).
"""
from __future__ import annotations

import pytest
from conftest import MEOW, MULTILANG, SIMPLE  # type: ignore[import]

from projectmap.exporters.writers import to_json, to_markdown
from projectmap.scanners.analyze import analyze


def test_scan_simple_returns_model():
    model = analyze(SIMPLE)
    assert model.metadata["name"] == "simple"
    assert "python" in model.languages
    assert model.languages["python"].file_count >= 1


def test_scan_simple_reproducible():
    a = to_json(analyze(SIMPLE))
    b = to_json(analyze(SIMPLE))
    assert a == b


def test_scan_multilang_detects_all_languages():
    model = analyze(MULTILANG)
    langs = set(model.languages)
    assert {"python", "rust", "cpp", "go", "markdown"} <= langs


def test_scan_multilang_roles_inferred():
    model = analyze(MULTILANG)
    # tests/ -> test role
    test_files = [f for f in model.files if f.role == "test"]
    assert test_files, "se esperaba detectar rol 'test' en tests/"
    # tools/ -> tooling role
    tool_files = [f for f in model.files if f.role == "tooling"]
    assert tool_files, "se esperaba detectar rol 'tooling' en tools/"


def test_scan_multilang_components_by_directory():
    model = analyze(MULTILANG)
    cids = set(model.components)
    assert "src" in cids or "tests" in cids  # al menos alguna partición por dir


def test_scan_multilang_reproducible():
    assert to_json(analyze(MULTILANG)) == to_json(analyze(MULTILANG))


def test_languages_have_file_counts():
    model = analyze(MULTILANG)
    for name, lang in model.languages.items():
        assert lang.file_count >= 1, name


def test_markdown_export_contains_languages_and_components():
    model = analyze(MULTILANG)
    md = to_markdown(model)
    assert "## Languages" in md
    assert "## Components" in md
    assert "python" in md


def test_markdown_neutral_no_branding_by_default():
    model = analyze(SIMPLE)
    md = to_markdown(model, branding=False)
    # Sin atribución de autor/marca; la frase filosófica general está permitida.
    assert "Danny" not in md and "ISyCo" not in md
    # El footer de branding sólo aparece con --branding
    assert "Generated with ProjectMap" not in md


def test_markdown_branding_opt_in():
    model = analyze(SIMPLE)
    md = to_markdown(model, branding=True)
    assert "ProjectMap" in md


def test_scan_meow_real_repo_hard_case():
    """El caso cabrón: MEOW-ENGINE (40 langs, harness, tools) sin tocar el core."""
    if not MEOW.exists():
        pytest.skip("MEOW-ENGINE no clonado al lado de ProjectMap")
    model = analyze(MEOW)
    langs = set(model.languages)
    # evidencia de que detecta varios lenguajes reales del repo
    assert {"python"}.issubset(langs)
    # no inventa un rol "meow" (el core no conoce MEOW)
    all_roles = {f.role for f in model.files if f.role}
    assert "meow" not in all_roles
    # reproducible
    assert to_json(model) == to_json(analyze(MEOW))
