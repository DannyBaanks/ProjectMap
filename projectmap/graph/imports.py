"""Import extractor: extrae dependencias de archivos por lenguaje.

Hoy soporta Python (ast). Otros lenguajes se añaden incrementalemente.
El extractor NO importa código del proyecto analizado; lee el archivo como
texto y parsea con stdlib (ast para Python). Para lenguajes sin parser stdlib,
se usa heurística por línea (regex) marcada como INFERRED.

Nunca ejecuta código del proyecto analizado.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

SUPPORTED = {"python", "javascript", "typescript", "rust", "go", "ruby", "java"}


@dataclass(frozen=True)
class ImportRef:
    """Un import referenciando un módulo/ruta símbolo."""
    raw: str          # texto del import (ej: "projectmap.core.model")
    language: str     # lenguaje del archivo que lo contiene
    confidence: str   # "verified" (ast) | "inferred" (regex)


def extract_imports(path: str | Path, language: str | None) -> list[ImportRef]:
    """Devuelve la lista de imports referenciados en el archivo."""
    if language is None:
        return []
    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    if language == "python":
        return _python_imports(text)
    # heurística por línea para lenguajes sin parser stdlib
    if language == "javascript" or language == "typescript":
        return _regex_imports(text, _JS_IMPORT_RE, language)
    if language == "go":
        return _regex_imports(text, _GO_IMPORT_RE, language)
    if language == "rust":
        return _regex_imports(text, _RUST_USE_RE, language)
    if language == "ruby":
        return _regex_imports(text, _RUBY_REQUIRE_RE, language)
    if language == "java":
        return _regex_imports(text, _JAVA_IMPORT_RE, language)
    return []


def _python_imports(text: str) -> list[ImportRef]:
    out: list[ImportRef] = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        # fallback regex débil si el archivo tiene sintaxis rara/parcial
        return _regex_imports(text, _PY_IMPORT_RE, "python")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                out.append(ImportRef(raw=n.name, language="python", confidence="verified"))
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.append(ImportRef(raw=node.module, language="python", confidence="verified"))
    return out


_PY_IMPORT_RE = re.compile(r"^\s*(?:import|from)\s+([\w\.]+)", re.MULTILINE)
_JS_IMPORT_RE = re.compile(r"""(?:import\s+.*?\s+from\s+['"]([^'"]+)['"])|(?:require\(['"]([^'"]+)['"]\))|(?:import\(['"]([^'"]+)['"]\))""", re.MULTILINE)
_GO_IMPORT_RE = re.compile(r'^\s*(?:import\s+"([^"]+)"|"\s*([^"]+)\s*")\s*$', re.MULTILINE)
_RUST_USE_RE = re.compile(r"^\s*use\s+([\w\:]+)", re.MULTILINE)
_RUBY_REQUIRE_RE = re.compile(r"^\s*require(_relative)?\s+['\"]([^'\"]+)['\"]", re.MULTILINE)
_JAVA_IMPORT_RE = re.compile(r"^\s*import\s+([\w\.]+);", re.MULTILINE)


def _regex_imports(text: str, rx: re.Pattern, language: str) -> list[ImportRef]:
    out = []
    for m in rx.finditer(text):
        # tomar el primer grupo no-None
        val = next((g for g in m.groups() if g), None)
        if val:
            out.append(ImportRef(raw=val, language=language, confidence="inferred"))
    return out
