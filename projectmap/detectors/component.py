"""Component detector: agrupa archivos en componentes lógicos.

Mecanismos:
1. manifest explícito (.projectmap/project.yaml components[])
2. directorios de primer/segundo nivel como componente (toplevel package)
3. manifests del proyecto (Cargo.toml, package.json, pyproject.toml) como
   marcadores de componente raíz
4. fallback: archivo suelto -> componente "misc"
"""
from __future__ import annotations

from pathlib import PurePosixPath

from projectmap.core.evidence import Confidence, Evidence
from projectmap.scanners.fs_scan import ScannedPath


def detect_component(path: ScannedPath, repo_root: str | None = None,
                     declared: dict[str, str] | None = None) -> tuple[str, Evidence]:
    declared = declared or {}
    if path.path in declared:
        cid = declared[path.path]
        return cid, Evidence(claim=f"declared component: {cid}",
                             source="manifest", confidence=Confidence.DECLARED)

    pp = PurePosixPath(path.path)
    parts = pp.parts
    if len(parts) >= 2:
        # primer directorio significativo como componente
        first = parts[0]
        return first, Evidence(claim=f"top dir {first!r} -> component",
                               source="heuristic:dir", confidence=Confidence.INFERRED)
    # archivo en raíz -> misc
    return "misc", Evidence(claim="archivo en raíz -> misc",
                            source="heuristic:root", confidence=Confidence.INFERRED)
