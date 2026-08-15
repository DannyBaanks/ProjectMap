"""Language detector.

Mecanismos, en orden de prioridad:
1. manifest explícito (.projectmap/project.yaml "declared")
2. extensión del archivo (rápido y confiable para lenguajes comunes)
3. UNKNOWN si no se reconoce.

No soporta 1000 lenguajes manualmente; la tabla es extensible.
"""
from __future__ import annotations

from projectmap.core.evidence import Confidence, Evidence
from projectmap.scanners.fs_scan import ScannedPath

# Tabla extensiva (no exhaustiva). El usuario puede añadir lenguajes via manifest.
_EXT_TO_LANG = {
    ".py": "python",
    ".pyi": "python",
    ".rs": "rust",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".hxx": "cpp",
    ".java": "java",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".scala": "scala",
    ".swift": "swift",
    ".go": "go",
    ".rb": "ruby",
    ".php": "php",
    ".pl": "perl",
    ".lua": "lua",
    ".js": "javascript",
    ".mjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".cs": "csharp",
    ".fs": "fsharp",
    ".fsx": "fsharp",
    ".hs": "haskell",
    ".jl": "julia",
    ".dart": "dart",
    ".groovy": "groovy",
    ".clj": "clojure",
    ".ex": "elixir",
    ".exs": "elixir",
    ".erl": "erlang",
    ".lisp": "common-lisp",
    ".rkt": "racket",
    ".pl2": "prolog",
    ".sql": "sql",
    ".sh": "shell",
    ".ps1": "powershell",
    ".bat": "batch",
    ".r": "r",
    ".nim": "nim",
    ".v": "verilog",
    ".zig": "zig",
    ".cr": "crystal",
    ".d": "d",
    ".ml": "ocaml",
    ".svelte": "svelte",
    ".vue": "vue",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".xml": "xml",
    ".md": "markdown",
    ".txt": "text",
    ".jaja": "jajaja",       # lenguaje esotérico del ecosistema MEOW (detectado genéricamente)
    ".bf": "brainfuck",
    ".mal": "malbolge",
    ".jq": "jq",
    ".tcl": "tcl",
    ".coffee": "coffeescript",
    ".xml2": "xml",
    ".wat": "webassembly-text",
    ".wasm": "webassembly",
    ".vb": "vb",
    ".asm": "assembly",
    ".s": "assembly",
    ".f": "fortran",
    ".f90": "fortran",
    ".f95": "fortran",
    ".cob": "cobol",
    ".cbl": "cobol",
    ".csv": "csv",
    ".ffi": "ffi",
    ".iesy": "iesy",
}


def detect_language(path: ScannedPath, declared: dict[str, str] | None = None) -> tuple[str | None, Evidence]:
    """Devuelve (language, evidence). Ningún claim se inventa como verificado."""
    declared = declared or {}
    rel = path.path
    if rel in declared:
        return declared[rel], Evidence(claim=f"declared: {declared[rel]}",
                                       source="manifest", confidence=Confidence.DECLARED)
    lang = _EXT_TO_LANG.get(path.suffix)
    if lang is not None:
        return lang, Evidence(claim=f"extension {path.suffix} -> {lang}",
                              source="extension", confidence=Confidence.VERIFIED)
    return None, Evidence(claim="lenguaje no reconocido", source="extension", confidence=Confidence.UNKNOWN)


def ext_known(suffix: str) -> bool:
    return suffix in _EXT_TO_LANG
