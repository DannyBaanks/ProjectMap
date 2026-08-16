"""GitHub adapter: genera artefactos locales compatibles con GitHub.

NO hace push. NO modifica el repo del usuario directamente. Produce archivos
en un directorio de salida; el usuario decide qué commitear.

Neutral por defecto (sin branding). `--branding` añade atribución opcional.

Artefactos generados:
- ARCHITECTURE.md     -- reporte humano (neutral)
- .gitattributes       -- hints para GitHub Linguist (lenguajes vendored/docs)
- language-bar.json   -- datos para badges/colores (neutral, sin marca)

Todo es INFERRED/VERIFIED según la evidencia del modelo; nada se inventa.
"""
from __future__ import annotations

import json
from pathlib import Path

from projectmap.core.model import ProjectModel
from projectmap.exporters.writers import to_markdown

# Extensiones que GitHub Linguist suele clasificar mal como "data" o vendored.
# Esta tabla es genérica (no conoce MEOW ni a un proyecto concreto).
_VENDORED_HINTS = {
    "lock", "toml", "json", "yaml", "yml", "xml", "ini", "cfg",
}
_DOC_HINTS = {"md", "rst", "txt"}


def emit_github_artifacts(out_dir: str | Path, model: ProjectModel, branding: bool = False) -> list[Path]:
    """Genera artefactos GitHub locales en out_dir. Devuelve ls lista de rutas creadas."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []

    # ARCHITECTURE.md (neutral salvo --branding)
    arch = to_markdown(model, branding=branding)
    p = out / "ARCHITECTURE.md"
    p.write_text(arch, encoding="utf-8")
    created.append(p)

    # .gitattributes con hints de Linguist (sin crear reglas específicas de un proyecto)
    attrs = _build_gitattributes(model)
    pg = out / ".gitattributes"
    pg.write_text(attrs, encoding="utf-8")
    created.append(pg)

    # language-bar.json: datos crudos para badges/colores neutros
    bar = _build_language_bar(model)
    pb = out / "language-bar.json"
    pb.write_text(json.dumps(bar, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    created.append(pb)

    return created


def _build_gitattributes(model: ProjectModel) -> str:
    """ klassifica algunos lenguajes como vendored/docs para Linguist, genérico."""
    lines: list[str] = ["# ProjectMap -- GitHub Linguist hints (neutral, inferred)"]
    lines.append("# Generado automáticamente. Revisa antes de commitear.")
    lines.append("")
    for name in sorted(model.languages):
        exts = _exts_for_language(model, name)
        if not exts:
            continue
        if name in ("json", "yaml", "toml", "xml"):
            for e in exts:
                lines.append(f"*{e} linguist-generated=true")
        elif name == "markdown":
            for e in exts:
                lines.append(f"*{e} linguist-documentation=true")
    if not lines[-1].startswith("*"):
        lines.append("# (sin hints para este proyecto)")
    return "\n".join(lines) + "\n"


def _exts_for_language(model: ProjectModel, name: str) -> list[str]:
    """Recoge extensiones observadas para el lenguaje `name`."""
    from projectmap.detectors.language import _EXT_TO_LANG
    return sorted([k for k, v in _EXT_TO_LANG.items() if v == name])


def _build_language_bar(model: ProjectModel) -> dict:
    """Datos crudos para una barra de lenguajes neutral (sin URLs de marca)."""
    total = sum(l.file_count for l in model.languages.values()) or 1
    return {
        "project": model.metadata.get("name"),
        "total_files": len(model.files),
        "languages": [
            {"name": name, "files": lang.file_count,
             "fraction": round(lang.file_count / total, 4)}
            for name, lang in sorted(model.languages.items())
        ],
    }
