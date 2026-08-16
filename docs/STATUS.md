# ProjectMap — Estado

> Evidence before narrative. Generado 2026-08-15 (M1.1 + M2 + M3).

## Architecture
- `projectmap/core/` — ProjectModel, Evidence, Manifest. **NO importa GitHub ni MEOW** (verificado por `tests/test_core_neutral.py`).
- `projectmap/scanners/` — `fs_scan` (read-only) + `analyze` (orquestador).
- `projectmap/detectors/` — language (extensión + manifest), role (path/basename heuristics), component (dir).
- `projectmap/graph/` — **import extractor** (Python via AST; JS/Go/Rust/Ruby/Java via regex INFERRED) + **relation builder** (imports → components, INFERRED/VERIFIED).
- `projectmap/exporters/` — JSON + Markdown. Neutral por defecto; `--branding` opt-in.
- `projectmap/adapters/github.py` — **GitHub adapter (M3)**: ARCHITECTURE.md + `.gitattributes` (overrides SOLO con evidencia DECLARED) + language-bar.json (reporte propio de ProjectMap) + github-linguist-report.json. Local, sin push, neutral.
- `projectmap/cli/` — scan/init/inspect/export/**apply**/validate. `scan` y `inspect` son read-only; `apply` escribe SOLO si se pide (con `--dry-run`).

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

## M3 (GitHub Linguist integración real)
- Verificado contra `github-linguist/linguist@main` (docs/overrides.md + lib/linguist/languages.yml, 2026-08-15): GitHub SOLO consume `.gitattributes` commiteado con atributos `linguist-*`; los lenguajes fuera de languages.yml se ignoran aunque se declaren.
- **Tabla ProjectMap→Linguist** (60+ lenguajes verificados). Lenguajes esotéricos (malbolge, jajaja, ffi, iesy) → `unsupported_by_linguist`, nunca escritos como override.
- **`.gitattributes` honesto**: overrides SOLO para lenguajes/roles DECLARADOS en manifest (`linguist-language=Nombre` con espacios→guiones, `linguist-documentation`). Los VERIFIED por extensión no se tocan (Linguist infiere lo mismo). Se eliminó el `linguist-generated=true` heurístico de M2 (mentira: json/yaml no son generados).
- **`language-bar.json`** etiquetado como reporte PROPIO de ProjectMap (GitHub no lo consume) — `"source": "projectmap"`.
- **`github-linguist-report.json`**: qué vería GitHub + qué NO consume + `planned_overrides` con evidencia por archivo.
- **`projectmap apply --target github`** escribe en la raíz del repo (con `--dry-run`); nunca commitea ni hace push. **VERIFIED** por `tests/test_github_linguist.py` (11 tests).

## Tests
```
python -m pytest -q   # 44 passed
ruff check .          # All checks passed
```

## Unknown / TODO
- Component detection sigue siendo ingenuo (dir = component). Mejora futura: usar manifests reales del proyecto (Cargo.toml, package.json) — hoy UNKNOWN.
- Role detection más fina (engine vs core) — INFERRED débil.
- content-based language detection (sin extensión) — futuro.
- `linguist-vendored` / `linguist-generated` / `linguist-detectable`: el manifest no tiene campo para declararlos hoy; se emiten solo si se declara rol docs. Futuro: campos `vendored`/`generated` en manifest.
- 5 archivos "unknown" en MEOW (sin extensión) — no inventados.
