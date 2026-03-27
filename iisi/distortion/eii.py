"""
IISI — EII Engine (Ego Influence Index)
THE MASTER KEY from the MG Universe Formula Vault.

Formula:
    EII = Σ(Eᵢ × Iᵢ × Dᵢ) / N

    Eᵢ  = Ego Coefficient for emotion i
          -1 = Ego-Dissolving  (gratitude, humility, compassion, joy, peace)
           0 = Ego-Neutral     (curiosity, determination, surprise, confidence)
          +1 = Ego-Amplifying  (anger, fear, pride, disgust, jealousy)

    Iᵢ  = Emotional Intensity   [0–1] — how strongly the emotion fires in text
    Dᵢ  = Duration proxy        [0–1] — density/repetition of the signal

    EII > 0 → Distorted (Risk Zone)
    EII ≈ 0 → Neutral
    EII < 0 → Awareness Zone (ego-dissolving)

Run EII before EUP and IRG. It is the multiplier for all downstream formulas.
From MG Universe Formula Vault — Layer I: IH layer.
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Tuple

# ── Emotion signal lexicons, mapped to ego coefficient Eᵢ ─────────────────────

# Eᵢ = +1: Ego-Amplifying emotions (Risk Zone)
_AMPLIFYING = [
    # Anger / rage
    r"\bfurious\b", r"\brage\b", r"\bangry\b", r"\boutraged\b",
    r"\bhow dare\b", r"\bthis is unacceptable\b",
    # Fear-based self-preservation
    r"\bpanic\b", r"\bterror\b", r"\bpetrified\b", r"\bdoomed\b",
    r"\bno choice\b", r"\bmust survive\b", r"\bdesparate\b",
    # Pride / overconfidence
    r"\bobviously\b", r"\btrust me\b", r"\bI'm certain\b", r"\bno doubt\b",
    r"\beveryone knows\b", r"\bany sane person\b", r"\bI know best\b",
    # Jealousy / contempt
    r"\bthey don't deserve\b", r"\bunfair\b", r"\bthey always\b",
    r"\bthey never\b", r"\bI'm better\b",
    # Disgust
    r"\bdisgusting\b", r"\bhorrible\b", r"\bunethical\b.*\bthey\b",
]

# Eᵢ = -1: Ego-Dissolving emotions (Awareness Zone)
_DISSOLVING = [
    # Gratitude
    r"\bgrateful\b", r"\bthankful\b", r"\bappreciate\b", r"\bgratitude\b",
    # Humility
    r"\bI could be wrong\b", r"\bI may be mistaken\b", r"\bopen to\b",
    r"\bI don't have all the answers\b", r"\bhumble\b",
    # Compassion
    r"\bcompassion\b", r"\bempathy\b", r"\bcaring about\b", r"\btheir wellbeing\b",
    # Peace / equanimity
    r"\bcalm\b", r"\bpeace\b", r"\bequanimity\b", r"\bsteady\b",
    # Trust / surrender
    r"\bI trust\b", r"\bI accept\b", r"\blet it be\b", r"\bsurrender\b",
]

# Eᵢ = 0: Ego-Neutral (neither amplifying nor dissolving)
_NEUTRAL = [
    r"\bcurious\b", r"\binterested\b", r"\bwondering\b",
    r"\bdetermined\b", r"\bfocused\b", r"\bsteadfast\b",
    r"\bsurprised\b", r"\bunexpected\b",
    r"\bconfident\b",  # Note: confidence is neutral, overconfidence is amplifying
]

# Protected — never classified
_EXCLUSION = [
    r"\bI believe\b", r"\bmy faith\b", r"\bI grieve\b", r"\bI mourn\b",
    r"\bmy values\b",
]

_EPSILON = 1e-6


def _signal_density(text: str, patterns: List[str]) -> float:
    """Normalized density [0–1] of signal matches in text."""
    text_lower = text.lower()
    count = sum(1 for p in patterns if re.search(p, text_lower))
    if count == 0:
        return 0.0
    words = max(1, len(text.split()))
    return min(1.0, round(count / max(1, words / 8), 4))


def _is_excluded(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in _EXCLUSION)


@dataclass
class EIIResult:
    """
    Output of the EII computation.
    Variables named as in the Formula Vault.
    """
    # Emotion scores
    amplifying_intensity: float    # Iᵢ for Eᵢ=+1 emotions
    dissolving_intensity: float    # Iᵢ for Eᵢ=-1 emotions
    neutral_intensity: float       # Iᵢ for Eᵢ=0  emotions

    # EII = Σ(Eᵢ × Iᵢ × Dᵢ) / N
    # Simplified: (+1 × Ia × Da) + (-1 × Id × Dd) + (0 × In × Dn)
    # = Ia - Id   (neutral terms cancel to zero)
    EII: float

    @property
    def zone(self) -> str:
        if self.EII > 0.3:   return "RISK"
        if self.EII > 0.0:   return "ELEVATED"
        if self.EII < -0.1:  return "AWARENESS"
        return "NEUTRAL"

    @property
    def is_amplifying(self) -> bool:
        return self.EII > 0.0

    @property
    def is_critical(self) -> bool:
        """Maps to SL-12: total lockdown if EII > 0.9"""
        return self.EII > 0.9

    def summary(self) -> str:
        return (
            f"EII={self.EII:+.4f}  "
            f"[{self.zone}]  "
            f"amp={self.amplifying_intensity:.3f}  "
            f"diss={self.dissolving_intensity:.3f}"
        )


class EIIEngine:
    """
    Computes the Ego Influence Index — the master pre-check.
    Must run before EUP and IRG.

    EII = Σ(Eᵢ × Iᵢ × Dᵢ) / N
        = amplifying_intensity - dissolving_intensity
          (neutral terms multiply by 0 and vanish)
    """

    def compute(self, text: str) -> EIIResult:
        if not text or not text.strip() or _is_excluded(text):
            return EIIResult(
                amplifying_intensity=0.0,
                dissolving_intensity=0.0,
                neutral_intensity=0.0,
                EII=0.0,
            )

        Ia = _signal_density(text, _AMPLIFYING)   # Eᵢ = +1
        Id = _signal_density(text, _DISSOLVING)   # Eᵢ = -1
        In = _signal_density(text, _NEUTRAL)      # Eᵢ = 0 → vanishes

        # EII = (+1 × Ia) + (-1 × Id) + (0 × In)
        EII = round(Ia - Id, 4)

        return EIIResult(
            amplifying_intensity=Ia,
            dissolving_intensity=Id,
            neutral_intensity=In,
            EII=EII,
        )
