"""Project model: el modelo interno, independiente del formato de salida.

Contratos pequeños. No asuma que esta estructura es definitiva; está diseñada
para crecer mediante contratos.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from projectmap.core.evidence import Evidence


@dataclass(frozen=True)
class FileEntry:
    path: str
    language: str | None
    role: str | None
    component_id: str | None
    evidence: tuple[Evidence, ...] = ()

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "language": self.language,
            "role": self.role,
            "component_id": self.component_id,
            "evidence": [e.to_dict() for e in self.evidence],
        }


@dataclass
class Component:
    id: str
    name: str
    role: str | None
    files: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "files": self.files,
            "dependencies": self.dependencies,
            "capabilities": self.capabilities,
            "evidence": [e.to_dict() for e in self.evidence],
        }


@dataclass(frozen=True)
class Relation:
    source: str
    target: str
    type: str
    evidence: tuple[Evidence, ...] = ()


@dataclass
class LanguageEntry:
    name: str
    file_count: int
    role_evidence: list[Evidence] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"name": self.name, "file_count": self.file_count,
                "role_evidence": [e.to_dict() for e in self.role_evidence]}


@dataclass
class ProjectModel:
    root: str
    metadata: dict[str, Any] = field(default_factory=dict)
    files: list[FileEntry] = field(default_factory=list)
    languages: dict[str, LanguageEntry] = field(default_factory=dict)
    components: dict[str, Component] = field(default_factory=dict)
    relations: list[Relation] = field(default_factory=list)

    def add_file(self, f: FileEntry) -> None:
        self.files.append(f)
        lang = f.language or "unknown"
        entry = self.languages.get(lang)
        if entry is None:
            self.languages[lang] = LanguageEntry(name=lang, file_count=1)
        else:
            entry.file_count += 1

    def add_component(self, c: Component) -> None:
        self.components[c.id] = c

    def add_relation(self, r: Relation) -> None:
        self.relations.append(r)

    def to_dict(self) -> dict:
        return {
            "root": self.root,
            "metadata": self.metadata,
            "file_count": len(self.files),
            "files": [f.to_dict() for f in self.files],
            "languages": {k: v.to_dict() for k, v in self.languages.items()},
            "components": {k: v.to_dict() for k, v in self.components.items()},
            "relations": [
                {"source": r.source, "target": r.target, "type": r.type,
                 "evidence": [e.to_dict() for e in r.evidence]}
                for r in self.relations
            ],
        }
