"""GitHub adapter (M3): artefactos honestos para GitHub Linguist.

Qué consume GitHub de verdad (verificado contra github-linguist/linguist:
docs/overrides.md y lib/linguist/languages.yml, consultado 2026-08-15):
- `.gitattributes` commiteado, con linguist-language / linguist-documentation /
  linguist-vendored / linguist-generated / linguist-detectable.
- Los nombres de lenguaje DEBEN existir en languages.yml; si no, GitHub los
  ignora aunque se escriban. Por eso los lenguajes sin mapeo se reportan como
  `unsupported_by_linguist` y nunca se escriben como override.

Qué NO consume GitHub:
- language-bar.json  -> reporte propio de ProjectMap (etiquetado como tal).

Regla de evidencia: nunca emitir un override sin evidencia. Un override de
`linguist-language` sólo se genera para lenguajes DECLARADOS en el manifest;
los lenguajes VERIFIED por extensión no necesitan override (Linguist infiere
lo mismo de la misma extensión). Nada de generado/vendored inventado.
"""
from __future__ import annotations

import json
from pathlib import Path

from projectmap.core.evidence import Confidence
from projectmap.core.model import ProjectModel
from projectmap.exporters.writers import to_markdown

# ProjectMap -> GitHub Linguist (sólo lenguajes presentes en languages.yml,
# 2026-08-15). Los que no están aquí son "unsupported_by_linguist".
_LANG_TO_LINGUIST = {
    "python": "Python", "rust": "Rust", "c": "C", "cpp": "C++",
    "java": "Java", "kotlin": "Kotlin", "scala": "Scala", "swift": "Swift",
    "go": "Go", "ruby": "Ruby", "php": "PHP", "perl": "Perl", "lua": "Lua",
    "javascript": "JavaScript", "typescript": "TypeScript", "csharp": "C#",
    "fsharp": "F#", "haskell": "Haskell", "julia": "Julia", "dart": "Dart",
    "groovy": "Groovy", "clojure": "Clojure", "elixir": "Elixir",
    "erlang": "Erlang", "common-lisp": "Common Lisp", "racket": "Racket",
    "prolog": "Prolog", "sql": "SQL", "shell": "Shell",
    "powershell": "PowerShell", "batch": "Batchfile", "r": "R",
    "nim": "Nim", "verilog": "Verilog", "zig": "Zig", "crystal": "Crystal",
    "d": "D", "ocaml": "OCaml", "svelte": "Svelte", "vue": "Vue",
    "html": "HTML", "css": "CSS", "scss": "SCSS", "json": "JSON",
    "yaml": "YAML", "toml": "TOML", "xml": "XML", "markdown": "Markdown",
    "text": "Text", "brainfuck": "Brainfuck", "jq": "jq", "tcl": "Tcl",
    "coffeescript": "CoffeeScript", "webassembly": "WebAssembly",
    "webassembly-text": "WebAssembly", "vb": "Visual Basic .NET",
    "assembly": "Assembly", "fortran": "Fortran", "cobol": "COBOL",
    "csv": "CSV",
}

# Lenguajes en _EXT_TO_LANG sin entrada en languages.yml (ignorados por GitHub).
_UNSUPPORTED = {
    "jajaja", "malbolge", "ffi", "iesy",
}

_LINGUIST_REFERENCE = (
    "github-linguist/linguist@main (lib/linguist/languages.yml, "
    "docs/overrides.md; consultado 2026-08-15)"
)


def linguist_name(lang: str) -> str | None:
    """Nombre Linguist de `lang`, o None si GitHub no lo soporta."""
    if lang in _UNSUPPORTED:
        return None
    return _LANG_TO_LINGUIST.get(lang)


def _linguist_attr_value(name: str) -> str:
    """Valor para `linguist-language=`: los espacios se reemplazan por guiones
    (ver docs/overrides.md: 'Replace any whitespace in the language name')."""
    return name.replace(" ", "-")


def emit_github_artifacts(out_dir: str | Path, model: ProjectModel, branding: bool = False) -> list[Path]:
    """Genera artefactos GitHub locales en out_dir (read-only sobre el repo).
    Devuelve la lista de rutas creadas."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []

    # ARCHITECTURE.md (neutral salvo --branding)
    arch = to_markdown(model, branding=branding)
    p = out / "ARCHITECTURE.md"
    p.write_text(arch, encoding="utf-8")
    created.append(p)

    # .gitattributes: overrides sólo con evidencia DECLARED
    pg = out / ".gitattributes"
    pg.write_text(_build_gitattributes(model), encoding="utf-8")
    created.append(pg)

    # language-bar.json: reporte PROPIO de ProjectMap (GitHub no lo consume)
    pb = out / "language-bar.json"
    pb.write_text(json.dumps(_build_language_bar(model), indent=2, sort_keys=True, ensure_ascii=False),
                  encoding="utf-8")
    created.append(pb)

    # github-linguist-report.json: qué vería GitHub, con evidencia
    pr = out / "github-linguist-report.json"
    pr.write_text(json.dumps(_build_linguist_report(model), indent=2, sort_keys=True, ensure_ascii=False),
                  encoding="utf-8")
    created.append(pr)

    return created


def apply_github_artifacts(repo_root: str | Path, model: ProjectModel, dry_run: bool = False) -> list[tuple[str, str, str]]:
    """Aplica los artefactos GitHub en la raíz del repo (escribe si no es
    dry-run). Nunca commitea ni hace push. Devuelve [(accion, relpath, nota)]."""
    root = Path(repo_root)
    files = {
        ".gitattributes": _build_gitattributes(model),
        "language-bar.json": json.dumps(_build_language_bar(model), indent=2, sort_keys=True, ensure_ascii=False),
        "github-linguist-report.json": json.dumps(_build_linguist_report(model), indent=2, sort_keys=True, ensure_ascii=False),
    }
    plan: list[tuple[str, str, str]] = []
    for rel, content in files.items():
        target = root / rel
        existed = target.exists()
        if dry_run:
            plan.append(("would-write", rel, "sobrescrito" if existed else "nuevo"))
        else:
            target.write_text(content + "\n", encoding="utf-8")
            plan.append(("written", rel, "sobrescrito" if existed else "nuevo"))
    return plan


def _build_gitattributes(model: ProjectModel) -> str:
    """Overrides honestos: sólo lenguajes/roles DECLARADOS en el manifest."""
    lines = [
        "# ProjectMap -- GitHub linguist hints (evidence-only)",
        "# GitHub aplica este archivo solo una vez commiteado; ProjectMap no commitea ni hace push.",
        "# Overrides solo con evidencia DECLARED (manifest); nada se inventa.",
        "",
    ]
    overrides = _planned_overrides(model)
    if overrides:
        for path, attr, _evidence in overrides:
            lines.append(f"{path} {attr}")
    else:
        lines.append("# (sin overrides: ningun lenguaje/rol DECLARADO en manifest)")
    return "\n".join(lines) + "\n"


def _planned_overrides(model: ProjectModel) -> list[tuple[str, str, str]]:
    """[(path, atributo, evidencia)] para .gitattributes, sólo con DECLARED."""
    out: list[tuple[str, str, str]] = []
    for f in model.files:
        lang_ev = f.evidence[0] if f.evidence else None
        if (f.language and f.language != "unknown" and lang_ev is not None
                and lang_ev.confidence is Confidence.DECLARED):
            lname = linguist_name(f.language)
            if lname:
                out.append((f.path, f"linguist-language={_linguist_attr_value(lname)}",
                            "lenguaje DECLARADO en manifest"))
        role_ev = f.evidence[1] if len(f.evidence) > 1 else None
        if f.role in ("docs", "documentation") and role_ev is not None \
                and role_ev.confidence is Confidence.DECLARED:
            out.append((f.path, "linguist-documentation", "rol docs DECLARADO en manifest"))
    return out


def _build_language_bar(model: ProjectModel) -> dict:
    """Barra de lenguajes como reporte propio de ProjectMap, no integración."""
    total = sum(l.file_count for l in model.languages.values()) or 1
    return {
        "source": "projectmap",
        "note": "Reporte propio de ProjectMap. GitHub NO lo consume; "
                "no forma parte de la integracion Linguist.",
        "project": model.metadata.get("name"),
        "total_files": len(model.files),
        "languages": [
            {"name": name, "files": lang.file_count,
             "fraction": round(lang.file_count / total, 4)}
            for name, lang in sorted(model.languages.items())
        ],
    }


def _build_linguist_report(model: ProjectModel) -> dict:
    """Qué vería GitHub en la página del repo, con evidencia y sin claims falsos."""
    langs: list[dict] = []
    unsupported: list[str] = []
    for name, entry in sorted(model.languages.items()):
        if name == "unknown":
            continue
        lname = linguist_name(name)
        if lname is None:
            unsupported.append(name)
        langs.append({"name": name, "linguist": lname, "files": entry.file_count})
    return {
        "source": "projectmap",
        "target": "github-linguist",
        "linguist_reference": _LINGUIST_REFERENCE,
        "github_consumes": [
            (".gitattributes commiteado (linguist-language / -documentation / "
             "-vendored / -generated / -detectable)"),
            "solo lenguajes presentes en languages.yml; el resto se ignora",
        ],
        "github_does_not_consume": [
            "language-bar.json (reporte propio de ProjectMap)",
        ],
        "languages": langs,
        "unsupported_by_linguist": unsupported,
        "files_with_unknown_language": [f.path for f in model.files if not f.language],
        "planned_overrides": [
            {"path": p, "attribute": a, "evidence": e}
            for p, a, e in _planned_overrides(model)
        ],
    }