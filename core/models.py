"""
IISI Core Models
Internal Integrity Stabilization Infrastructure
MindTech OS / MG Universe — All rights reserved
PCT/IB2025/060883
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


# ─── Enumerations ────────────────────────────────────────────────────────────

class DistortionClass(str, Enum):
    EGO = "ego"
    FEAR = "fear"
    INCENTIVE = "incentive"
    NARRATIVE = "narrative"
    TEMPORAL = "temporal"


class DistortionLevel(int, Enum):
    LATENT = 1       # detectable but non-dominant — observe only
    ACTIVE = 2       # influencing reasoning — stabilize
    DOMINANT = 3     # driving decisions — stabilize
    CRITICAL = 4     # overriding intent — halt, return agency


class OperationalMode(str, Enum):
    PASSIVE = "passive"           # observe only, no intervention
    REFLECTIVE = "reflective"     # surface contradictions, advisory
    STABILIZATION = "stabilization"  # delay + reflection active
    AUDIT = "audit"               # post-decision trace only


class PolicyDecision(str, Enum):
    ALLOW = "allow"
    REFLECT = "reflect"
    STABILIZE = "stabilize"
    HALT = "halt"


# ─── Core Data Structures ────────────────────────────────────────────────────

@dataclass
class IntentSnapshot:
    """
    Immutable capture of human intent at T₀.
    This baseline cannot be modified once set for the session.
    """
    session_id: str
    raw_input: str
    captured_at: datetime = field(default_factory=datetime.utcnow)
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    context: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Freeze — intent snapshot is immutable
        object.__setattr__(self, "_locked", True)


@dataclass
class DistortionSignal:
    """A single detected distortion with its class and intensity."""
    distortion_class: DistortionClass
    level: DistortionLevel
    confidence: float           # 0.0–1.0
    signals: List[str]          # detected linguistic/behavioral markers
    description: str = ""


@dataclass
class DistortionVector:
    """
    Composite of all active distortions in a session.
    IISI evaluates vector magnitude, not binary presence.
    """
    signals: List[DistortionSignal] = field(default_factory=list)
    composite_magnitude: float = 0.0

    def dominant_class(self) -> Optional[DistortionClass]:
        if not self.signals:
            return None
        return max(self.signals, key=lambda s: s.level * s.confidence).distortion_class

    def requires_stabilization(self) -> bool:
        return any(
            s.level in (DistortionLevel.ACTIVE, DistortionLevel.DOMINANT)
            for s in self.signals
        )

    def requires_halt(self) -> bool:
        return any(s.level == DistortionLevel.CRITICAL for s in self.signals)


@dataclass
class IntegrityBaseline:
    """
    What the human meant — not what they want to hear.
    Established once per session from the Intent Snapshot.
    Immutable reference for divergence monitoring.
    """
    session_id: str
    intent_snapshot: IntentSnapshot
    core_objective: str
    key_constraints: List[str] = field(default_factory=list)
    established_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class StabilityIndex:
    """
    SI ∈ [0, 1]
    Composite of three sub-scores derived from the patent's MIS model.
    SI = (linguistic_consistency + intent_coherence + temporal_clarity) / 3
    """
    linguistic_consistency: float   # 0–1: language matches stated intent
    intent_coherence: float         # 0–1: alignment between goal and reasoning
    temporal_clarity: float         # 0–1: short/long horizon awareness

    @property
    def score(self) -> float:
        return round(
            (self.linguistic_consistency + self.intent_coherence + self.temporal_clarity) / 3,
            4
        )

    @property
    def is_stable(self) -> bool:
        return self.score >= 0.65

    def __str__(self):
        return f"SI={self.score:.3f} (LC={self.linguistic_consistency:.2f}, IC={self.intent_coherence:.2f}, TC={self.temporal_clarity:.2f})"


@dataclass
class StabilizationAction:
    """A single non-coercive stabilization mechanism applied."""
    mechanism: str              # delay | reflection | temporal_widening | responsibility_anchor | decentering
    prompt: str                 # the actual output to the human
    distortion_targeted: DistortionClass
    is_blocking: bool = False   # IISI never blocks — this is always False


@dataclass
class DivergenceReport:
    """
    Post-interaction observation. IISI never corrects — only observes.
    """
    session_id: str
    baseline_objective: str
    outcome_summary: str
    divergence_detected: bool
    divergence_description: str = ""
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class IISISession:
    """Full session record — the audit trail."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    mode: OperationalMode = OperationalMode.REFLECTIVE
    intent_snapshot: Optional[IntentSnapshot] = None
    integrity_baseline: Optional[IntegrityBaseline] = None
    distortion_vector: Optional[DistortionVector] = None
    stability_index: Optional[StabilityIndex] = None
    stabilization_actions: List[StabilizationAction] = field(default_factory=list)
    policy_decision: Optional[PolicyDecision] = None
    divergence_report: Optional[DivergenceReport] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
