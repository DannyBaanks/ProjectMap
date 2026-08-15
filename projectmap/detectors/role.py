"""Role detector: qué papel juega un archivo/componente en el proyecto.

El rol NO se confunde con el lenguaje: un mismo lenguaje puede tener muchos
roles (Python: orchestration, tests, tooling...).

Heurísticas iniciales (todas INFERRED salvo manifest):
- path + nombre del archivo
- presencia de marcadores de test/benchmark
- presencia de hints en el path (adapters/, exporters/, tests/, tools/)

Roles genéricos soportados:
    core, engine, orchestration, adapter, frontend, backend, cli, tooling,
    test, benchmark, configuration, documentation, generated, fixture, unknown
"""
from __future__ import annotations

from projectmap.core.evidence import Confidence, Evidence
from projectmap.scanners.fs_scan import ScannedPath

# Marcadores por path (substring insensible a mayúsculas).
_PATH_HINTS = [
    (("tests/", "test_", "_test.", ".spec.", "/test"), "test"),
    (("benchmarks/", "benchmark", "bench_"), "benchmark"),
    (("fixtures/", "/fixture"), "fixture"),
    (("docs/", ".md", "readme", "license"), "documentation"),
    ((".github/", "workflows/"), "configuration"),
    (("tools/",), "tooling"),
    (("adapters/",), "adapter"),
    (("exporters/",), "adapter"),
    (("cli/",), "cli"),
    (("examples/",), "example"),
    (("__init__",), "configuration"),
    ((".gitignore", ".gitattributes", "pyproject.toml", "cargo.toml", "package.json",
      "setup.py", "requirements.txt", "tsconfig.json", "pom.xml", "build.gradle",
      "cmakelists.txt", "makefile", "dockerfile", ".dockerignore", "pytest.ini"),
     "configuration"),
]

_ROLE_BY_BASENAME = {
    "conftest.py": "test",
    "setup.py": "configuration",
    "manage.py": "cli",
    "main.py": "cli",
    "__main__.py": "cli",
    "app.js": "frontend",
    "index.js": "frontend",
    "index.ts": "frontend",
    "main.rs": "cli",
    "main.go": "cli",
}


def detect_role(path: ScannedPath, language: str | None, declared: dict[str, str] | None = None) -> tuple[str | None, Evidence]:
    declared = declared or {}
    rel = path.path.lower()

    if path.path in declared:
        return declared[path.path], Evidence(
            claim=f"declared role: {declared[path.path]}",
            source="manifest", confidence=Confidence.DECLARED)

    # heurísticas por path
    for markers, role in _PATH_HINTS:
        for m in markers:
            if m in rel:
                return role, Evidence(claim=f"path marker {m!r} -> {role}",
                                      source="heuristic:path", confidence=Confidence.INFERRED)

    # basename exacto
    base = rel.rsplit("/", 1)[-1]
    if base in _ROLE_BY_BASENAME:
        role = _ROLE_BY_BASENAME[base]
        return role, Evidence(claim=f"basename {base!r} -> {role}",
                              source="heuristic:basename", confidence=Confidence.INFERRED)

    # .py + sin info -> orchestration/backend inferido (debilmente)
    if language == "python" and path.suffix == ".py":
        return "orchestration", Evidence(
            claim="python source sin marcador específico -> orchestration",
            source="heuristic:lang-default", confidence=Confidence.INFERRED)

    return None, Evidence(claim="sin rol detectable", source="heuristic", confidence=Confidence.UNKNOWN)
