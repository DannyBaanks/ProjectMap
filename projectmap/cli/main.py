"""CLI: projectmap scan/init/inspect/export/validate.

`scan` y `inspect` son read-only. `init` y `export` escriben, sólo cuando se pide.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from projectmap.exporters.writers import to_json, to_markdown
from projectmap.scanners.analyze import analyze


def _cmd_scan(args: argparse.Namespace) -> int:
    model = analyze(args.path)
    print(to_json(model))
    return 0


def _cmd_inspect(args: argparse.Namespace) -> int:
    """Inspección humana read-only: lenguajes y componentes."""
    model = analyze(args.path)
    print("Project:", model.metadata.get("name", "?"))
    print()
    print("Languages:")
    for name, lang in sorted(model.languages.items()):
        print(f"  {name:14} {lang.file_count}")
    print()
    print("Components:")
    for cid, c in sorted(model.components.items()):
        print(f"  {cid:14} role={c.role or '-'}  files={len(c.files)}")
    if model.relations:
        print()
        print("Relations:")
        for r in model.relations:
            print(f"  {r.source} -> {r.target}  ({r.type})")
    print()
    print(f"Total files: {len(model.files)}")
    return 0


def _cmd_init(args: argparse.Namespace) -> int:
    """Crea .projectmap/project.yamlvacío, sin destruir nada existente."""
    root = Path(args.path).resolve()
    pm = root / ".projectmap"
    pm.mkdir(parents=True, exist_ok=True)
    manifest = pm / "project.yaml"
    if manifest.exists() and not args.force:
        print(f"ya existe: {manifest}  (use --force para sobrescribir)", file=sys.stderr)
        return 1
    stub = (
        "# ProjectMap manifest (optional). Edit by hand.\n"
        f"project:\n  name: {root.name}\n\n"
        "# components:\n#   - id: core\n#     role: engine\n\n"
        "# relations:\n#   - from: orchestration\n#     to: core\n#     type: invokes\n\n"
        "# file_languages:\n#   \"path/to/file\": python\n\n"
        "# file_roles:\n#   \"path/to/file\": test\n\n"
        "# file_components:\n#   \"path/to/file\": core\n"
    )
    manifest.write_text(stub, encoding="utf-8")
    print(f"created: {manifest}")
    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    """Genera artefactos locales. No hace push. Neutral por defecto."""
    model = analyze(args.path)
    out_dir = Path(args.out or "projectmap-output")
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.format == "json" or args.format == "all":
        (out_dir / "projectmap.json").write_text(to_json(model), encoding="utf-8")
    if args.format in ("markdown", "md", "all"):
        (out_dir / "ARCHITECTURE_REPORT.md").write_text(
            to_markdown(model, branding=args.branding), encoding="utf-8")
    if args.target == "github":
        _emit_github_artifacts(out_dir, model)
    print(f"exported -> {out_dir}")
    return 0


def _emit_github_artifacts(out_dir: Path, model) -> None:
    """Artefactos GitHub neutros: report.md opcional. Sin branding si no se pide."""
    (out_dir / "github").mkdir(exist_ok=True)
    # Neutral: sólo el reporte de arquitectura. El usuario decide qué commitear.
    (out_dir / "github" / "ARCHITECTURE.md").write_text(
        to_markdown(model, branding=False), encoding="utf-8")


def _cmd_validate(args: argparse.Namespace) -> int:
    """Valida reproducibilidad: mismo input -> mismo output (salvo timestamps)."""
    m1 = analyze(args.path)
    m2 = analyze(args.path)
    if to_json(m1) == to_json(m2):
        print("OK: reproducible")
        return 0
    print("FAIL: scan no es reproducible", file=sys.stderr)
    return 2


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="projectmap",
                                description="Model your project's architecture (read-only).")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("scan", help="read-only scan -> JSON to stdout")
    sp.add_argument("path")
    sp.set_defaults(func=_cmd_scan)

    sp = sub.add_parser("inspect", help="read-only human inspection")
    sp.add_argument("path")
    sp.set_defaults(func=_cmd_inspect)

    sp = sub.add_parser("init", help="create .projectmap/project.yaml (no overwrite)")
    sp.add_argument("path")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=_cmd_init)

    sp = sub.add_parser("export", help="generate local artefacts")
    sp.add_argument("path")
    sp.add_argument("--format", choices=["json", "markdown", "md", "all"], default="markdown")
    sp.add_argument("--out", default="projectmap-output")
    sp.add_argument("--target", choices=["github"], default=None)
    sp.add_argument("--branding", action="store_true", help="show ProjectMap attribution (default off)")
    sp.set_defaults(func=_cmd_export)

    sp = sub.add_parser("validate", help="verify reproducibility")
    sp.add_argument("path")
    sp.set_defaults(func=_cmd_validate)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
