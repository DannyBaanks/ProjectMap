"""Manifest loader: lee .projectmap/project.yaml (opcional, YAML minimal).

No se requiere PyYAML; soportamos un subconjunto YAML plano/simple en el MVP:
sólo keys/indented lists. Si PyYAML está disponible se usa; si no, fallback.
El manifest NO es obligatorio: el core funciona sin él.
"""
from __future__ import annotations

from pathlib import Path

try:
    import yaml  # type: ignore[unused-ignore]
    _ = yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


class Manifest:
    def __init__(self, data: dict | None = None) -> None:
        self.data = data or {}

    @property
    def exists(self) -> bool:
        return bool(self.data)

    def file_languages(self) -> dict[str, str]:
        return self.data.get("file_languages", {})

    def file_roles(self) -> dict[str, str]:
        return self.data.get("file_roles", {})

    def file_components(self) -> dict[str, str]:
        return self.data.get("file_components", {})

    def components(self) -> list[dict]:
        return self.data.get("components", [])

    def relations(self) -> list[dict]:
        return self.data.get("relations", [])

    def project_name(self) -> str | None:
        return (self.data.get("project") or {}).get("name")


def load_manifest(root: str | Path) -> Manifest:
    path = Path(root) / ".projectmap" / "project.yaml"
    if not path.exists():
        path = Path(root) / ".projectmap" / "project.yml"
    if not path.exists():
        return Manifest({})
    text = path.read_text(encoding="utf-8")
    if _HAS_YAML:
        import yaml
        return Manifest(yaml.safe_load(text) or {})
    # fallback: parseo YAML plano muy simple (top-level keys + listas indentadas)
    return Manifest(_parse_simple_yaml(text))


def _parse_simple_yaml(text: str) -> dict:
    """Parser fallback para YAML plano sin dependencias. Soporta:
    project:
      name: foo
    file_languages:
      "foo.py": python
    components:
      - id: core
        role: engine
    relations:
      - from: a
        to: b
        type: depends_on
    Limitado pero suficiente para el MVP. Si el usuario necesita el parser
    completo, instalar PyYAML.
    """
    # Implementación mínima: por líneas, indentación = nivel.
    root: dict = {}
    stack: list[tuple[int, dict | list]] = [(-1, root)]
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        # descartar llaves sueltas en fallback simplista
        cur_indent, cur = stack[-1]
        while indent <= cur_indent and len(stack) > 1:
            stack.pop()
            cur_indent, cur = stack[-1]
        if isinstance(cur, list):
            # list item
            if line.startswith("- "):
                item = {}
                rest = line[2:].strip()
                if rest:
                    _put(item, rest)
                cur.append(item)
                stack.append((indent, item))
            else:
                # key dentro de un item de lista
                _put(cur, line)
        else:
            if line.startswith("- "):
                # la pass anterior era dict, ahora lista: reemplazar
                _key, _val, _rest = _split_key(line[2:].strip())
                continue
            _put(cur, line)
    return root


def _split_key(s: str) -> tuple[str, str]:
    if ":" in s:
        k, v = s.split(":", 1)
        return k.strip().strip('"'), v.strip()
    return s, ""


def _put(d: dict, line: str) -> None:
    if ":" in line:
        k, v = line.split(":", 1)
        k = k.strip().strip('"')
        v = v.strip()
        if v == "":
            d[k] = {}
        else:
            d[k] = v.strip('"')
