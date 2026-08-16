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
    """Parser fallback para YAML plano sin dependencias. Soporta el subconjunto
    documentado en docs/PRINCIPLES.md y el stub de `projectmap init`:

        project:
          name: foo
        file_languages:
          "foo.py": python
        components:
          - id: core
            role: engine
        relations:
          - from: api
            to: core
            type: invokes

    Reglas soportadas:
    - indentación por espacios (niveles consistentes por bloque).
    - key: value  -> string (comillas opcionales). key: solo -> dict|list.
    - "- key: value"  -> item de lista (dict). Las siguientes líneas indentadas
      con mayor indent que el "-" pertenecen al mismo item.
    - comentarios '#' y líneas vacías se ignoran.
    No soporta: anchors, multiline strings, flow style, tipos nativos (todo
    es string). Si necesitas eso, instala PyYAML.
    """
    lines = _yaml_lines(text)
    root: dict = {}
    _parse_block(lines, 0, root)
    return root


def _yaml_lines(text: str) -> list[tuple[int, str]]:
    """Devuelve [(indent, stripped), ...] sin comentarios ni vacías."""
    out = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        out.append((indent, raw.strip()))
    return out


def _parse_block(lines: list[tuple[int, str]], start: int, into: dict | list) -> int:
    """Parse recursivo por indentación. `into` es dict o list del nivel actual.
    Devuelve el índice de la siguiente línea no consumida."""
    i = start
    base_indent = lines[start][0] if start < len(lines) else 0
    while i < len(lines):
        indent, line = lines[i]
        if indent < base_indent:
            # sube un nivel: fin de este bloque
            return i
        if indent > base_indent:
            # no debería pasar aquí; el hijo ya consumió su propio bloque
            i += 1
            continue
        if line.startswith("- "):
            # parent debe ser list; si into es dict, no podemos (no documentado)
            if isinstance(into, list):
                item = {}
                # primera key:value del item
                rest = line[2:].strip()
                if rest:
                    _put_kv(item, rest)
                into.append(item)
                i += 1
                # consumir sub-bloque indentado del item
                if i < len(lines) and lines[i][0] > indent:
                    if isinstance(item, dict):
                        i = _parse_block(lines, i, item)
                    else:
                        i = _parse_block(lines, i, item)  # listas within list (no soportado plenamente)
                continue
            # dict con "-" -> patrón "key:" seguido de lista en nivel hijo. Lo
            # manejamos en la rama key:value (dict) más abajo; si llegamos aquí
            # es formato inválido, ignoramos.
            i += 1
            continue
        # key: value  o  key: (dict|list hijo)
        if isinstance(into, dict):
            key, val = _kv(line)
            if val == "":
                # hijo: dict o lista en el siguiente nivel indentado
                if i + 1 < len(lines) and lines[i + 1][0] > indent:
                    child_indent = lines[i + 1][0]
                    if lines[i + 1][1].startswith("- "):
                        child: list = []
                        into[key] = child
                        i = _parse_list(lines, i + 1, child, child_indent)
                    else:
                        child_d: dict = {}
                        into[key] = child_d
                        i = _parse_block(lines, i + 1, child_d)
                    continue
                into[key] = {}
                i += 1
                continue
            into[key] = _unquote(val)
            i += 1
            continue
        # list item con clave suelta (no documentado): ignorar
        i += 1
    return i


def _parse_list(lines, start: int, into: list, indent: int) -> int:
    """Consume items "- ..." al mismo indent."""
    i = start
    while i < len(lines):
        line_indent, line = lines[i]
        if line_indent < indent:
            return i
        if line_indent > indent:
            # sub-bloque del último item ya consumido por _parse_block; skip
            i += 1
            continue
        if line.startswith("- "):
            item = {}
            rest = line[2:].strip()
            if rest:
                _put_kv(item, rest)
            into.append(item)
            i += 1
            if i < len(lines) and lines[i][0] > indent:
                i = _parse_block(lines, i, item)
            continue
        return i
    return i


def _kv(line: str) -> tuple[str, str]:
    if ":" in line:
        k, v = line.split(":", 1)
        return _unquote(k.strip()), v.strip()
    return line, ""


def _unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] in ('"', "'") and s[-1] == s[0]:
        return s[1:-1]
    return s


def _put_kv(d: dict, rest: str) -> None:
    """key: value para un item de lista."""
    if ":" in rest:
        k, v = rest.split(":", 1)
        d[_unquote(k.strip())] = _unquote(v.strip())
    else:
        d[_unquote(rest)] = ""
