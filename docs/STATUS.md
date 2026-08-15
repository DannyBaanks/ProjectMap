# ProjectMap — Estado

> Evidence before narrative. Generado 2026-08-15.

## Architecture
- `projectmap/core/` — ProjectModel, Evidence, Manifest. **NO importa GitHub ni MEOW** (verificado por `tests/test_core_neutral.py`).
- `projectmap/scanners/` — `fs_scan` (read-only) + `analyze` (orquestador).
- `projectmap/detectors/` — language (extensión + manifest), role (path/basename heuristics), component (directorio).
- `projectmap/exporters/` — JSON + Markdown. Neutral por defecto; `--branding` opt-in.
- `projectmap/cli/` — scan/inspect/init/export/validate. `scan` y `inspect` son read-only (verificado por test).

## Detection (VERIFIED en fixtures + MEOW real)
- **Languages**: por extensión (70+ extensiones) + manifest DECLARED. VERIFIED.
- **Roles**: test / tooling / documentation / configuration / cli / adapter / orchestration por heurísticas de path. INFERRED (excepto manifest).
- **Components**: por directorio top-level. INFERRED.
- **Relations**: sólo DECLARED via manifest (graph automático es futuro).

## Evidence
| Fixtura       | Lenguajes detectados                 | Estado    |
|---------------|--------------------------------------|-----------|
| simple        | 1 (python)                           | VERIFIED  |
| multilang     | 5 (python, rust, cpp, go, markdown)  | VERIFIED  |
| MEOW-ENGINE   | 28 lenguajes de implementación + json/yaml/toml/markdown/text | VERIFIED |
| Reproducibilidad | mismo input -> mismo JSON         | VERIFIED  |
| Neutralidad core   | sin imports de GitHub/MEOW/red  | VERIFIED  |
| Read-only scan | no crea/borra archivos en el repo  | VERIFIED  |

## Tests
```
python -m pytest -q   # 15 passed, ruff clean
```
Comandos ejecutados:
- `projectmap inspect fixtures/simple` — OK
- `projectmap inspect fixtures/multilang` — OK (5 lenguajes, roles test/tooling)
- `projectmap inspect C:\Development\ISyCo Git\MEOW-ENGINE` — OK (28 lenguajes, 8 componentes, sin tocar el core)
- `projectmap validate fixtures/multilang` — reproducible

## Unknown / TODO
- Graph automático de relations por imports (milestone futuro).
- GitHub adapter completo (.gitattributes, badges) — sólo `ARCHITECTURE.md` neutral ahora.
- Role detection más fina (engine vs core vs library) — hoy es INFERRED débil.
- 5 archivos "unknown" en MEOW (sin extensión reconocida) — UNKNOWN, no se inventó.
- Detección de capabilities (declaradas vs inferidas) — futuro.
