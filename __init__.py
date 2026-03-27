"""
IISI — Internal Integrity Stabilization Infrastructure
MindTech OS / MG Universe

PCT/IB2025/060883 — Humanity-Driven Decision Intelligence System

Public API:
    from iisi import IISI, OperationalMode
    
    iisi = IISI()
    response = iisi.process("your input here")
    print(response.stabilization_prompts)
    print(response.stability_index)
"""

from .pipeline import IISI, IISIResponse
from .core.models import (
    OperationalMode,
    PolicyDecision,
    DistortionClass,
    DistortionLevel,
    StabilityIndex,
    IISISession,
    DivergenceReport,
)

__version__ = "0.1.0"
__author__ = "MindTech OS / MG Universe"
__license__ = "Proprietary — see LICENSE"

__all__ = [
    "IISI",
    "IISIResponse",
    "OperationalMode",
    "PolicyDecision",
    "DistortionClass",
    "DistortionLevel",
    "StabilityIndex",
    "IISISession",
    "DivergenceReport",
]
