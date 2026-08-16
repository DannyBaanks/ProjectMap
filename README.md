# ProjectMap

**ProjectMap is not an architecture for your project. It is a model of your project.**

ProjectMap is community tooling for making complex repositories easier to
understand. It analyzes a repository and produces a structured representation
of its languages, files, components, roles, capabilities, relations and
architecture — with explicit evidence and confidence, never passing inference
off as fact.

It does not arrive saying "your project must have Core, Registry, Providers
and Adapters because we decided so." It arrives saying: "this is what I could
observe; here is the evidence; these parts are inferred; these others were
declared by the author."

## Status
Early prototype. Local scans only. Read-only by design (the only command that
writes into a repo is `apply`, and only when you ask for it). No cloud, no
network, no LLM dependency. See `docs/` and `evidence/`.

## Stack
Python 3.10+ (stdlib only), pytest for tests.

## Install
```
cd projectmap
pip install -e .
```

## Usage
```
projectmap scan .
projectmap scan ./tests/fixtures/multilang
projectmap inspect .
projectmap init .
projectmap export --format markdown
projectmap export --target github      # read-only: artefacts en ./projectmap-output/github
projectmap apply --target github --dry-run   # imprime el plan, no escribe nada
projectmap apply --target github       # escribe .gitattributes + reportes en la raiz
projectmap validate .
```

### GitHub Linguist (M3)
`export --target github` and `apply --target github` generate artifacts GitHub
actually consumes — verified against `github-linguist/linguist` (`docs/overrides.md`
and `lib/linguist/languages.yml`):
- `.gitattributes` with `linguist-language` / `linguist-documentation` — only
  for files whose language/role was **DECLARED** in the manifest. Nothing is
  invented: VERIFIED-by-extension files need no override (Linguist infers the
  same from the same extension).
- Languages GitHub does not know (e.g. malbolge) are reported in
  `github-linguist-report.json` under `unsupported_by_linguist` and never
  written as overrides.
- `language-bar.json` is ProjectMap's **own** report; GitHub does not consume it.
- GitHub only applies `.gitattributes` once it is committed. ProjectMap never
  commits and never pushes.

## Fixtures
- `fixtures/simple/` — one language (control case).
- `fixtures/multilang/` — Python + Rust + C++ + Go (heterogeneous).
- `fixtures/linguist/` — Python/Rust/C++/Java/COBOL + malbolge (unsupported by
  Linguist) + unknown extension, with a manifest declaring language/role.
- `fixtures/meow/` — link to a real, complex repo (MEOW-ENGINE) used as the
  hard test case. ProjectMap core has zero knowledge of MEOW.

## Design
```
ProjectMap Core
      |
 Project Model
      |
Adapters / Exporters / Scanners / Detectors
      |
 Platforms (local now; GitHub/GitLab future)
```
The core never imports a platform SDK or a specific project. MEOW is only a
motivating example and a fixture.
