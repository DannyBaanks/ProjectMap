"""Evidence model: confidence levels y claims respaldados.

Evidence before narrative: nunca presentar inferencia como hecho.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Confidence(str, Enum):
    VERIFIED = "verified"
    INFERRED = "inferred"
    DECLARED = "declared"
    UNKNOWN = "unknown"
    CONFLICTING = "conflicting"


@dataclass(frozen=True)
class Evidence:
    """Un claim respaldado por una fuente con confianza."""

    claim: str
    source: str
    confidence: Confidence

    def to_dict(self) -> dict:
        return {"claim": self.claim, "source": self.source, "confidence": self.confidence.value}

    def __str__(self) -> str:
        return f"{self.claim} ({self.source}:{self.confidence.value})"
