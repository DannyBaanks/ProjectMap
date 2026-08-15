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
Early prototype. Local scans only. Read-only by design. No GitHub, no cloud,
no network, no LLM dependency. See `docs/` and `evidence/`.

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
projectmap validate .
```

## Fixtures
- `fixtures/simple/` — one language (control case).
- `fixtures/multilang/` — Python + Rust + C++ + Go (heterogeneous).
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
