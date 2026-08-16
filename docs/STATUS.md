# ProjectMap — Estado

> Evidence before narrative. Generado 2026-08-15 (M1.1 + M2).

## Architecture
- `projectmap/core/` — ProjectModel, Evidence, Manifest. **NO importa GitHub ni MEOW** (verificado por `tests/test_core_neutral.py`).
- `projectmap/scanners/` — `fs_scan` (read-only) + `analyze` (orquestador).
- `projectmap/detectors/` — language (extensión + manifest), role (path/basename heuristics), component (dir).
- `projectmap/graph/` — **import extractor** (Python via AST; JS/Go/Rust/Ruby/Java via regex INFERRED) + **relation builder** (imports → components, INFERRED/VERIFIED).
- `projectmap/exporters/` — JSON + Markdown. Neutral por defecto; `--branding` opt-in.
- `projectmap/adapters/github.py` — **GitHub adapter**: ARCHITECTURE.md + .gitattributes (Linguist hints) + language-bar.json. Local, sin push, neutral.
- `projectmap/cli/` — scan/init/inspect/export/validate. `scan` y `inspect` son read-only.

## Detection
- **Languages**: por extensión (70+ ext) + manifest DECLARED. VERIFIED.
- **Roles**: test/tooling/docs/cli/adapter/orchestration por path. INFERRED (excepto manifest).
- **Components**: por directorio top-level. INFERRED.
- **Relations**: DECLARED via manifest + **INFERRED por imports** (grafo automático). Un `import` no prueba arquitectura; es INFERRED salvo AST confirmado (VERIFIED en Python).

## Evidence
| Fixtura       | Lenguajes | Relations inferidas        | Estado    |
|---------------|-----------|----------------------------|-----------|
| simple        | 1         | 0                          | VERIFIED  |
| multilang     | 5         | 0 (fixture minimal)       | VERIFIED  |
| relrepo (test) | 1        | 1 (pkg_app -> pkg_core)    | VERIFIED  |
| MEOW-ENGINE   | 28 impl   | múltiples (harness/languages/tests) | VERIFIED |

## M1.1 (bug fixes auditoría)
- **FileEntry.to_dict()** + `ProjectModel.to_dict()` ahora incluyen `files` con evidencia por archivo. **VERIFIED**.
- **Fallback YAML reparado**: soporta listas de dicts (components/relations) sin PyYAML. **VERIFIED** por tests con y sin PyYAML.

## M2 (grafo + GitHub adapter)
- Grafo de imports: Python (AST VERIFIED), JS/TS/Go/Rust/Ruby/Java (regex INFERRED). **VERIFIED**.
- GitHub adapter: `.gitattributes` (Linguist hints), `ARCHITECTURE.md`, `language-bar.json`. Neutral. **VERIFIED**.
- `projectmap export --target github` genera todo local; no hace push.

## Tests
```
python -m pytest -q   # 33 passed
ruff check .          # All checks passed
```

## Unknown / TODO
- Component detection sigue siendo ingenuo (dir = component). Mejora futura: usar manifests reales del proyecto (Cargo.toml, package.json) — hoy UNKNOWN.
- Role detection más fina (engine vs core) — INFERRED débil.
- content-based language detection (sin extensión) — futuro.
- GitHub adapter completo (badges shields.io, Actions workflow) — hoy genera artefactos sueltos.
- 5 archivos "unknown" en MEOW (sin extensión) — no inventados.
