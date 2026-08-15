"""Exporters: JSON y Markdown. Neutral por defecto (sin branding)."""
from __future__ import annotations

import json

from projectmap.core.model import ProjectModel


def to_json(model: ProjectModel) -> str:
    return json.dumps(model.to_dict(), indent=2, sort_keys=True, ensure_ascii=False)


def to_markdown(model: ProjectModel, branding: bool = False) -> str:
    """Reporte humano. Neutral por defecto; `--branding` añade nota opcional."""
    out: list[str] = []
    out.append(f"# {model.metadata.get('name', 'project')}")
    out.append("")
    out.append("_ProjectMap is not an architecture for your project. It is a model of your project._")
    out.append("")
    out.append("## Languages")
    out.append("")
    out.append("| Language | Files |")
    out.append("|---|---|")
    for name, lang in sorted(model.languages.items()):
        out.append(f"| {name} | {lang.file_count} |")
    out.append("")
    out.append("## Components")
    out.append("")
    out.append("| Component | Role | Files |")
    out.append("|---|---|---|")
    for cid, c in sorted(model.components.items()):
        out.append(f"| {cid} | {c.role or '-'} | {len(c.files)} |")
    out.append("")
    if model.relations:
        out.append("## Relations")
        out.append("")
        out.append("| Source | Target | Type | Confidence |")
        out.append("|---|---|---|---|")
        for r in model.relations:
            conf = r.evidence[0].confidence.value if r.evidence else "unknown"
            out.append(f"| {r.source} | {r.target} | {r.type} | {conf} |")
        out.append("")
    if branding:
        out.append("---")
        out.append("_Generated with ProjectMap._")
    return "\n".join(out)
