"""Relation detector: construye el grafo de dependencias entre componentes.

Para cada archivo, extrae imports y mapea el import a un componente destino
cuando es posible. Las relaciones automáticas son INFERRED (un import no prueba
arquitectura; la prueba es el comportamiento).

Relaciones declaradas por manifest son DECLARED y NO se duplican con las
inferidas (las declaradas tienen prioridad).
"""
from __future__ import annotations

from pathlib import Path

from projectmap.core.evidence import Confidence, Evidence
from projectmap.core.model import ProjectModel, Relation
from projectmap.graph.imports import extract_imports


def build_relations(model: ProjectModel) -> list[Relation]:
    """Añade relations INFERRED al model y las devuelve. No duplica DECLARED."""
    declared = {(r.source, r.target, r.type) for r in model.relations}
    new: list[Relation] = []

    for f in model.files:
        if f.component_id is None or f.language is None:
            continue
        refs = extract_imports(Path(model.root) / f.path, f.language)
        for ref in refs:
            target = _resolve_target(ref.raw, f.path, model)
            if target is None or target == f.component_id:
                continue
            key = (f.component_id, target, "imports")
            if key in declared or any(
                (r.source, r.target, r.type) == key for r in new
            ):
                continue
            conf = Confidence.VERIFIED if ref.confidence == "verified" else Confidence.INFERRED
            new.append(Relation(
                source=f.component_id, target=target, type="imports",
                evidence=(Evidence(
                    claim=f"{f.component_id} imports {ref.raw} (from {f.path})",
                    source=f"{ref.language}-import", confidence=conf),),
            ))
    model.relations.extend(new)
    return new


def _resolve_target(ref: str, src_path: str, model: ProjectModel) -> str | None:
    """Mapea un import a un component_id del model, si es posible."""
    # Python: "projectmap.core.model" -> buscar componente por path matching
    if "." in ref and "/" not in ref:
        # "." separa módulos; el primer segmento suele ser el top package.
        candidates = [ref.replace(".", "/"), "/".join(ref.split(".")[:-1])]
        for cand in candidates:
            comp = _match_component_by_path(model, cand)
            if comp:
                return comp
        # fallback: primer segmento como dir
        first = ref.split(".")[0]
        if first in model.components:
            return first
        return None
    # JS/Go/Ruby: "import "./foo/bar"'"  ->  foo/bar
    ref_clean = ref.lstrip("./").lstrip("/")
    comp = _match_component_by_path(model, ref_clean)
    if comp:
        return comp
    return None


def _match_component_by_path(model: ProjectModel, fragment: str) -> str | None:
    """Busca un componente cuyo id o sus archivos coincidan con el fragment."""
    if fragment in model.components:
        return fragment
    # buscar archivos cuyo path contenga el fragment
    for f in model.files:
        if fragment in f.path and f.component_id:
            return f.component_id
    return None
