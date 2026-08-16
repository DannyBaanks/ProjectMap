"""M1.1: bug fixes criticos de la auditoria.

a) files + evidence por archivo en el JSON exportado.
b) fallback YAML sin PyYAML soporta listas (components/relations).
"""
from __future__ import annotations

import json
from pathlib import Path

from conftest import MULTILANG, SIMPLE  # type: ignore[import]

from projectmap.core.manifest import _parse_simple_yaml, load_manifest
from projectmap.exporters.writers import to_json
from projectmap.scanners.analyze import analyze

# --- a) files + evidence en el JSON exportado ---

def test_json_export_contains_files():
    model = analyze(SIMPLE)
    d = json.loads(to_json(model))
    assert "files" in d
    assert isinstance(d["files"], list)
    assert len(d["files"]) >= 1


def test_file_entry_has_evidence_in_json():
    model = analyze(SIMPLE)
    d = json.loads(to_json(model))
    f = d["files"][0]
    assert f["path"]
    assert f["language"] == "python"
    assert "evidence" in f and isinstance(f["evidence"], list)
    assert len(f["evidence"]) >= 1  # al menos el evidence de lenguaje


def test_file_evidence_has_confidence_and_source():
    model = analyze(MULTILANG)
    d = json.loads(to_json(model))
    found = next(f for f in d["files"] if f["language"] == "rust")
    evkinds = [e["confidence"] for e in found["evidence"]]
    # language via extension es VERIFIED; role/component pueden ser INFERRED
    assert "verified" in evkinds


def test_all_files_have_at_least_one_evidence():
    model = analyze(MULTILANG)
    d = json.loads(to_json(model))
    for f in d["files"]:
        assert isinstance(f["evidence"], list) and len(f["evidence"]) >= 1, f["path"]


# --- b) fallback YAML con listas ---

_MANIFEST_YAML = """\
project:
  name: fixture-test

components:
  - id: core
    role: engine
  - id: api
    role: orchestration

relations:
  - from: api
    to: core
    type: invokes

file_languages:
  "src/x.py": python

file_roles:
  "src/x.py": backend
"""


def test_simple_yaml_parser_parses_components_list():
    d = _parse_simple_yaml(_MANIFEST_YAML)
    assert d["project"]["name"] == "fixture-test"
    comps = d["components"]
    assert isinstance(comps, list) and len(comps) == 2
    assert comps[0] == {"id": "core", "role": "engine"}
    assert comps[1] == {"id": "api", "role": "orchestration"}


def test_simple_yaml_parser_parses_relations_list():
    d = _parse_simple_yaml(_MANIFEST_YAML)
    rels = d["relations"]
    assert isinstance(rels, list) and len(rels) == 1
    assert rels[0] == {"from": "api", "to": "core", "type": "invokes"}


def test_simple_yaml_parser_parses_flat_maps():
    d = _parse_simple_yaml(_MANIFEST_YAML)
    assert d["file_languages"]["src/x.py"] == "python"
    assert d["file_roles"]["src/x.py"] == "backend"


def test_load_manifest_with_fallback(tmp_path: Path):
    pm = tmp_path / ".projectmap"
    pm.mkdir()
    (pm / "project.yaml").write_text(_MANIFEST_YAML, encoding="utf-8")
    # forzamos fallback deshabilitando PyYAML si estuviera presente
    import projectmap.core.manifest as m
    orig = m._HAS_YAML
    m._HAS_YAML = False
    try:
        man = load_manifest(tmp_path)
    finally:
        m._HAS_YAML = orig
    assert man.project_name() == "fixture-test"
    comps = man.components()
    assert len(comps) == 2 and comps[0]["id"] == "core"
    rels = man.relations()
    assert len(rels) == 1 and rels[0]["from"] == "api"
    assert man.file_languages()["src/x.py"] == "python"


def test_analyze_honors_declared_relations(tmp_path: Path):
    """Un manifest con relations se refleja en el ProjectModel."""
    pm = tmp_path / ".projectmap"
    pm.mkdir()
    (pm / "project.yaml").write_text(_MANIFEST_YAML, encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "x.py").write_text("x=1", encoding="utf-8")
    model = analyze(tmp_path)
    assert any(r.source == "api" and r.target == "core" and r.type == "invokes"
               for r in model.relations)
