"""
IISI — IRG Engine (Impulse-Reasoning Gap)
Implements IH-03 from the MG Universe Formula Vault.

Formula:
    IRG = (Ip / Cv) × (1 + EII)

    Ip  = Impulse intensity       — urgency, reactive language
    Cv  = Cognitive volume        — reasoning, context, explanation
    EII = Ego Influence Index     — amplifier from Master Key

This formula directly addresses the gap the user identified:
"we must act immediately, it's an emergency"
→ Ip is HIGH (urgency words)
→ Cv is NEAR ZERO (no "because", "reason", "evidence", no context given)
→ IRG = HIGH / ~0 × (1+EII) → very large → DISTORTED

The absence of context is the signal. A genuine emergency comes with
an explanation. Panic without context = cognitive distortion.

The stabilization response to high IRG is specifically context-seeking:
"What specifically triggered this urgency?"
"What would change if you had 10 more minutes to explain the situation?"

From MG Universe Formula Vault — IH-03: Impulse-Reasoning Gap.
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List

_EPSILON = 1e-6

# ── Ip: Impulse signals ────────────────────────────────────────────────────────
# Urgency, reactivity, pressure, forced action without deliberation
_IMPULSE_SIGNALS = [
    r"\bimmediately\b", r"\bright now\b", r"\bemergency\b",
    r"\bno time\b", r"\bno time to think\b", r"\bact now\b",
    r"\bmust act\b", r"\bhave to\b", r"\bno choice\b",
    r"\binstantly\b", r"\bthis second\b", r"\bright away\b",
    r"\burge\b", r"\bimpulse\b", r"\breact\b", r"\breflex\b",
    r"\bjust do it\b", r"\bstop thinking\b", r"\bno time to\b",
    r"\bdon't overthink\b", r"\bfast\b", r"\bquick\b.*\bdecid\w*\b",
    r"\bnow or never\b", r"\blast chance\b", r"\bdeadline\b",
]

# ── Cv: Cognitive volume signals ───────────────────────────────────────────────
# Reasoning, context, explanation, deliberation, structured thought
_COGNITIVE_SIGNALS = [
    r"\bbecause\b", r"\bthe reason\b", r"\btherefore\b",
    r"\bspecifically\b", r"\bfor example\b", r"\bfor instance\b",
    r"\bthe situation is\b", r"\bhere is what happened\b",
    r"\bthe context is\b", r"\blet me explain\b",
    r"\bdue to\b", r"\bas a result of\b", r"\bwhich means\b",
    r"\bif.{0,20}then\b", r"\bI analysed\b", r"\bI analyzed\b",
    r"\bthe data\b", r"\bthe evidence\b", r"\bthe facts\b",
    r"\bstep by step\b", r"\bfirst.{0,20}second\b",
    r"\bI considered\b", r"\bafter reviewing\b", r"\bhaving thought\b",
    r"\bthe reason I\b", r"\bwhat happened is\b",
]

# Exclusions — protected inputs
_EXCLUSION = [
    r"\bI believe\b", r"\bmy faith\b", r"\bI grieve\b",
    r"\bmy values\b", r"\bmorally\b",
]


def _density(text: str, patterns: List[str]) -> float:
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
class IRGResult:
    """
    Output of the Impulse-Reasoning Gap computation.
    """
    Ip: float       # Impulse intensity         [0–1]
    Cv: float       # Cognitive volume           [0–1]
    EII: float      # Ego Influence Index        (from EIIEngine)
    IRG: float      # (Ip / Cv) × (1 + EII)

    context_absent: bool    # True when Ip > 0.3 and Cv < 0.1

    @property
    def severity(self) -> str:
        if self.IRG >= 4.0:   return "CRITICAL"
        if self.IRG >= 2.0:   return "DOMINANT"
        if self.IRG >= 0.8:   return "ACTIVE"
        if self.IRG >= 0.2:   return "LATENT"
        return "NONE"

    @property
    def stabilization_prompt(self) -> str:
        """
        Context-seeking prompt — triggered by the absence of reasoning.
        This is the "what is the emergency?" question, implemented as
        a non-coercive reflection prompt.
        """
        if self.context_absent:
            return (
                "You've described urgency without describing the situation. "
                "What specifically triggered this? "
                "Even a single sentence of context changes the quality of any decision."
            )
        if self.IRG >= 2.0:
            return (
                "The impulse to act is strong here. "
                "What is the reasoning behind it? "
                "Impulse and reason often point in the same direction — "
                "but only one of them is auditable."
            )
        return (
            "Before proceeding — what is the specific situation "
            "driving this decision?"
        )

    def summary(self) -> str:
        ctx = " [CONTEXT ABSENT]" if self.context_absent else ""
        return (
            f"IRG={self.IRG:.4f}  [{self.severity}]  "
            f"Ip={self.Ip:.3f}  Cv={self.Cv:.3f}{ctx}"
        )


class IRGEngine:
    """
    Impulse-Reasoning Gap Engine.
    Implements IH-03 from the MG Universe Formula Vault.

    IRG = (Ip / Cv) × (1 + EII)

    The key insight: a genuine emergency comes with context.
    Urgency without explanation is a cognitive distortion signal.
    """

    def compute(self, text: str, eii: float = 0.0) -> IRGResult:
        if not text or not text.strip() or _is_excluded(text):
            return IRGResult(Ip=0.0, Cv=0.0, EII=eii, IRG=0.0, context_absent=False)

        Ip = _density(text, _IMPULSE_SIGNALS)

        # Cv = combined cognitive volume:
        # explicit reasoning connectors + situational context descriptions
        Cv_reasoning    = _density(text, _COGNITIVE_SIGNALS)
        Cv_situational  = _density(text, _SITUATIONAL_CONTEXT_SIGNALS)
        Cv = round(min(1.0, Cv_reasoning + Cv_situational * 0.6), 4)

        # IRG = (Ip / Cv) × (1 + EII)
        # Raw ratio is capped at 10.0 to prevent infinity from near-zero Cv.
        # IRG > 2.0 = dominant gap. IRG > 4.0 = critical.
        raw_ratio = Ip / max(_EPSILON, Cv)
        raw_ratio = min(10.0, raw_ratio)                   # hard cap
        IRG = round(raw_ratio * (1.0 + max(0.0, eii)), 4)

        # Context absent: urgency present AND neither reasoning nor
        # situational context provided
        context_absent = (Ip > 0.3 and Cv_reasoning < 0.05 and Cv_situational < 0.1)

        return IRGResult(
            Ip=Ip,
            Cv=Cv,
            EII=eii,
            IRG=IRG,
            context_absent=context_absent,
        )

# ── Cv supplement: situational context signals ────────────────────────────────
# A genuine emergency also includes WHAT the situation is, not just WHY.
# "The server has been breached" is context even without "because".
_SITUATIONAL_CONTEXT_SIGNALS = [
    r"\bthe situation is\b", r"\bwhat happened\b", r"\bhere is why\b",
    r"\bspecifically\b", r"\bthe issue is\b", r"\bthe problem is\b",
    r"\bhas been\b", r"\bhave been\b", r"\bis happening\b",
    r"\bwe found\b", r"\bwe discovered\b", r"\bwe detected\b",
    r"\breported\b", r"\bconfirmed\b", r"\bbreached\b",
    r"\bexposed\b", r"\bfailed\b", r"\bcrashed\b", r"\bdown\b",
    r"\bthe deadline is\b", r"\bby \d+\b", r"\bin \d+ hour\b",
    r"\bthe contract\b", r"\bthe deal\b", r"\bthe client\b",
    r"\bthis means\b", r"\bwhich is\b",
]
