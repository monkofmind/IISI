"""
IISI Distortion Detection Engine (DDE)
Detects internal instability without psychological profiling or surveillance.

Detection is signal-based, not inference-based.
No emotion labeling. No identity tracking.
"""

from __future__ import annotations
import re
from typing import List, Tuple
from ..core.models import (
    DistortionClass, DistortionLevel, DistortionSignal, DistortionVector
)


# ─── Signal Lexicons ─────────────────────────────────────────────────────────
# Each pattern maps to a distortion class.
# These are observable linguistic signals, not psychological inferences.

_EGO_SIGNALS = [
    r"\bobviously\b", r"\bclearly\b", r"\bany sane person\b",
    r"\beveryone knows\b", r"\bI always\b", r"\bI never\b",
    r"\btrust me\b", r"\bI'm certain\b", r"\bno doubt\b",
    r"\bI've always been right\b", r"\bmy experience shows\b",
]

_FEAR_SIGNALS = [
    r"\bwhat if.{0,30}fail\b", r"\bworst case\b", r"\bcatastroph\w+\b",
    r"\bwe('re| are) doomed\b", r"\bno choice\b", r"\bhave to\b",
    r"\bimmediately\b", r"\bright now\b", r"\bemergency\b",
    r"\bcan't afford\b", r"\blow on time\b", r"\bno time\b",
]

_INCENTIVE_SIGNALS = [
    r"\bthey('ll| will) be happy\b", r"\bhe('ll| will) approve\b",
    r"\bshe('ll| will) approve\b", r"\bboard wants\b",
    r"\binvestors want\b", r"\bjust this once\b",
    r"\bif I do this.{0,30}reward\b", r"\blooks good\b",
    r"\bappear\b", r"\bimpress\b",
]

_NARRATIVE_SIGNALS = [
    r"\bthe story is\b", r"\bit's always been\b", r"\bthey('re| are) the villain\b",
    r"\bI'm the hero\b", r"\bit's simple\b", r"\bit's obvious\b",
    r"\bjust a matter of\b", r"\bblack and white\b",
    r"\bthey never\b", r"\bthey always\b",
]

_TEMPORAL_SIGNALS = [
    r"\bjust this once\b", r"\bfor now\b", r"\bwe'll fix it later\b",
    r"\bworry about that later\b", r"\bshort.?term\b",
    r"\bquick win\b", r"\bfast\b.*\bdecision\b",
    r"\bdon't have time to think\b", r"\bneed to decide now\b",
]

_SIGNAL_MAP = {
    DistortionClass.EGO: _EGO_SIGNALS,
    DistortionClass.FEAR: _FEAR_SIGNALS,
    DistortionClass.INCENTIVE: _INCENTIVE_SIGNALS,
    DistortionClass.NARRATIVE: _NARRATIVE_SIGNALS,
    DistortionClass.TEMPORAL: _TEMPORAL_SIGNALS,
}

# Phrases IISI never classifies as distortion
_EXCLUSION_PATTERNS = [
    r"\bI believe\b", r"\bin my view\b", r"\bmorally\b",
    r"\bmy values\b", r"\bmy faith\b", r"\bI disagree\b",
    r"\bI grieve\b", r"\bI mourn\b",
]


def _count_matches(text: str, patterns: List[str]) -> Tuple[int, List[str]]:
    """Return count of matched signals and which ones fired."""
    fired = []
    text_lower = text.lower()
    for pattern in patterns:
        if re.search(pattern, text_lower):
            fired.append(pattern.strip(r"\b").replace(r"\w+", "*"))
    return len(fired), fired


def _is_excluded(text: str) -> bool:
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in _EXCLUSION_PATTERNS)


def _score_to_level(match_count: int, text_length: int) -> DistortionLevel:
    """
    Convert raw match count to distortion level.
    Normalized by text length to avoid penalizing longer inputs.
    """
    density = match_count / max(1, text_length / 100)
    if density >= 3.0:
        return DistortionLevel.CRITICAL
    elif density >= 1.5:
        return DistortionLevel.DOMINANT
    elif density >= 0.7:
        return DistortionLevel.ACTIVE
    else:
        return DistortionLevel.LATENT


class DistortionDetectionEngine:
    """
    DDE — Detects internal instability by comparing:
    - Linguistic consistency
    - Temporal compression signals
    - Emotional volatility indicators
    - Goal drift markers

    No emotion inference. No psychological profiling.
    Output: DistortionVector
    """

    def detect(self, text: str, context: dict | None = None) -> DistortionVector:
        if not text or not text.strip():
            return DistortionVector()

        if _is_excluded(text):
            return DistortionVector()  # Protected input — do not classify

        signals: List[DistortionSignal] = []
        text_length = len(text)

        for dist_class, patterns in _SIGNAL_MAP.items():
            count, fired = _count_matches(text, patterns)
            if count == 0:
                continue

            level = _score_to_level(count, text_length)
            confidence = min(0.95, count * 0.25)

            signals.append(DistortionSignal(
                distortion_class=dist_class,
                level=level,
                confidence=confidence,
                signals=fired,
                description=self._describe(dist_class, level),
            ))

        # Composite magnitude = weighted sum
        magnitude = sum(s.level * s.confidence for s in signals) / max(1, len(signals))

        return DistortionVector(signals=signals, composite_magnitude=round(magnitude, 4))

    def _describe(self, cls: DistortionClass, level: DistortionLevel) -> str:
        descriptions = {
            DistortionClass.EGO: "Identity-protective reasoning detected",
            DistortionClass.FEAR: "Threat-driven intent collapse detected",
            DistortionClass.INCENTIVE: "External reward shaping intent",
            DistortionClass.NARRATIVE: "Story-fitting overriding reality",
            DistortionClass.TEMPORAL: "Short-term dominance over long-term",
        }
        return f"{descriptions[cls]} (level: {level.name})"
