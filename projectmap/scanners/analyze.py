"""Scanner principal: integra fs_scan + detectors + manifest -> ProjectModel.

Lee el repo, NO lo modifica. Produce un ProjectModel reproducible.
"""
from __future__ import annotations

from pathlib import Path

from projectmap.core.evidence import Confidence, Evidence
from projectmap.core.manifest import load_manifest
from projectmap.core.model import Component, FileEntry, ProjectModel, Relation
from projectmap.detectors.component import detect_component
from projectmap.detectors.language import detect_language
from projectmap.detectors.role import detect_role
from projectmap.scanners.fs_scan import scan


def analyze(root: str | Path) -> ProjectModel:
    """Analiza read-only y devuelve el ProjectModel. Reproducible."""
    root_path = Path(root).resolve()
    manifest = load_manifest(root_path)
    scanned = scan(root_path)
    model = ProjectModel(root=str(root_path))
    if manifest.project_name():
        model.metadata["name"] = manifest.project_name()
    else:
        model.metadata["name"] = root_path.name

    # declaraciones del manifest (overrides)
    decl_lang = manifest.file_languages()
    decl_role = manifest.file_roles()
    decl_comp = manifest.file_components()

    # componentes declarados (vacíos, se rellenan con archivos)
    declared_components: dict[str, Component] = {}
    for c in manifest.components():
        cid = c.get("id") or c.get("name")
        if not cid:
            continue
        declared_components[cid] = Component(
            id=cid, name=c.get("name", cid), role=c.get("role"),
            evidence=[Evidence(claim=f"declared component {cid}", source="manifest",
                               confidence=Confidence.DECLARED)],
        )

    for sp in scanned:
        lang, lang_ev = detect_language(sp, declared=decl_lang)
        role, role_ev = detect_role(sp, lang, declared=decl_role)
        cid, comp_ev = detect_component(sp, str(root_path), declared=decl_comp)

        file = FileEntry(
            path=sp.path,
            language=lang,
            role=role,
            component_id=cid,
            evidence=(lang_ev, role_ev, comp_ev),
        )
        model.add_file(file)

        # rellenar componente
        comp = declared_components.get(cid)
        if comp is None:
            comp = Component(id=cid, name=cid, role=None, files=[], evidence=[])
            model.add_component(comp)
            declared_components[cid] = comp
        else:
            if cid not in model.components:
                model.add_component(comp)
        comp.files.append(sp.path)
        # herencia: usar rol del primer archivo detectado si no fue declarado
        if comp.role is None and role is not None:
            comp.role = role
            comp.evidence.append(Evidence(
                claim=f"inferred role from file {sp.path}: {role}",
                source="heuristic", confidence=Confidence.INFERRED))

    # relaciones declaradas en el manifest (prioridad DECLARED)
    for r in manifest.relations():
        src = r.get("from") or r.get("source")
        dst = r.get("to") or r.get("target")
        rtype = r.get("type", "depends_on")
        if src and dst:
            model.add_relation(Relation(
                source=src, target=dst, type=rtype,
                evidence=(Evidence(claim=f"declared relation {src} -> {dst}", source="manifest",
                                   confidence=Confidence.DECLARED),),
            ))

    # relaciones INFERRED por imports (grafo automático). No duplica DECLARED.
    from projectmap.graph.relations import build_relations
    build_relations(model)

    return model
