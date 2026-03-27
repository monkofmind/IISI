"""
IISI Stabilization Logic Core (SLC)
Applies non-coercive stabilization mechanisms.

IISI never:
- Pushes a preferred choice
- Blocks action
- Substitutes judgment
- Rewards or penalizes behavior

Max 2 mechanisms per interaction. No repetition loops.
"""

from __future__ import annotations
import time
from typing import List, Optional
from ..core.models import (
    DistortionClass, DistortionLevel, DistortionVector,
    StabilizationAction, StabilityIndex
)


# ─── Mechanism Libraries ──────────────────────────────────────────────────────

_DELAY_PROMPTS = [
    "Take a moment before proceeding. Re-read your original intent.",
    "Pause briefly. Does this decision still reflect what you set out to do?",
    "Before continuing — what was your original objective?",
]

_REFLECTION_PROMPTS = {
    DistortionClass.EGO: [
        "This reasoning appears to conflict with your stated objective. Which assumption is load-bearing?",
        "If a trusted peer made this decision, what would you advise them?",
        "What would change if the outcome affected someone other than you?",
    ],
    DistortionClass.NARRATIVE: [
        "What evidence would cause you to revise this framing?",
        "Which part of this situation is most resistant to simplification?",
        "What are you not including in this account?",
    ],
    DistortionClass.FEAR: [
        "What is the realistic probability of the worst-case outcome?",
        "Has a similar situation resolved differently than feared before?",
        "What would you advise someone else facing this exact situation?",
    ],
    DistortionClass.INCENTIVE: [
        "Separate the reward from the decision. Does the action still make sense without it?",
        "Who bears the consequences of this decision — and who bears the reward?",
        "If approval were removed from the equation, would this still be your choice?",
    ],
    DistortionClass.TEMPORAL: [
        "How would this decision be evaluated in 12 months?",
        "What second-order effects persist beyond this context?",
        "Is speed serving clarity here, or replacing it?",
    ],
}

_TEMPORAL_WIDENING_PROMPTS = [
    "Project this decision forward 6 months. What does the landscape look like?",
    "What becomes irreversible if you proceed now versus in 48 hours?",
    "What would your future self want your present self to consider?",
]

_RESPONSIBILITY_ANCHORS = [
    "This analysis is assistive only. Final responsibility remains with you.",
    "This output does not transfer accountability. You remain the decision-maker.",
    "Whatever is decided here, the consequence ownership stays with you.",
]

_DECENTERING_PROMPTS = [
    "Evaluate this decision independent of your personal stake in the outcome.",
    "If a colleague brought you this decision, what would you tell them?",
    "What would an impartial observer say about this reasoning?",
]


class StabilizationLogicCore:
    """
    SLC — Selects and applies stabilization mechanisms based on distortion vector.
    
    Rules:
    - Max 2 mechanisms per interaction
    - Mechanisms never repeat cyclically
    - No mechanism blocks action
    - Responsibility anchor is always the final output
    """

    def __init__(self):
        self._used_mechanisms: List[str] = []
        self._interaction_count: int = 0

    # Weight multiplier per distortion level — higher level = stronger SI reduction
    _LEVEL_WEIGHT = {
        DistortionLevel.LATENT: 0.15,
        DistortionLevel.ACTIVE: 0.40,
        DistortionLevel.DOMINANT: 0.65,
        DistortionLevel.CRITICAL: 0.90,
    }

    def compute_stability_index(self, text: str, vector: DistortionVector) -> StabilityIndex:
        """
        Computes SI from distortion signals.
        SI = (linguistic_consistency + intent_coherence + temporal_clarity) / 3

        Level-weighted: CRITICAL distortions reduce SI far more than LATENT ones.
        Derived from the patent's MIS (Mindset Integrity Score) model.
        """
        lc = ic = tc = 1.0

        for s in vector.signals:
            w = self._LEVEL_WEIGHT.get(s.level, 0.15)
            reduction = s.confidence * w

            if s.distortion_class in (DistortionClass.EGO, DistortionClass.NARRATIVE):
                lc -= reduction
            if s.distortion_class in (DistortionClass.INCENTIVE, DistortionClass.FEAR):
                ic -= reduction
            if s.distortion_class == DistortionClass.TEMPORAL:
                tc -= reduction

        return StabilityIndex(
            linguistic_consistency=max(0.0, min(1.0, round(lc, 4))),
            intent_coherence=max(0.0, min(1.0, round(ic, 4))),
            temporal_clarity=max(0.0, min(1.0, round(tc, 4))),
        )

    def stabilize(
        self,
        vector: DistortionVector,
        stability_index: StabilityIndex,
        dominant_class: Optional[DistortionClass] = None,
    ) -> List[StabilizationAction]:
        """
        Returns stabilization actions. Never more than 2 per call.
        Returns empty list if no stabilization needed.
        """
        if vector.requires_halt():
            return self._halt_action()

        if not vector.requires_stabilization():
            return []

        actions: List[StabilizationAction] = []
        self._interaction_count += 1

        dom = dominant_class or vector.dominant_class()

        # Mechanism 1: based on dominant distortion class
        if dom == DistortionClass.FEAR or dom == DistortionClass.TEMPORAL:
            if "delay" not in self._used_mechanisms:
                actions.append(self._delay_action(dom))
                self._used_mechanisms.append("delay")

        if dom in (DistortionClass.EGO, DistortionClass.NARRATIVE):
            if "reflection" not in self._used_mechanisms:
                actions.append(self._reflection_action(dom))
                self._used_mechanisms.append("reflection")

        if dom == DistortionClass.TEMPORAL:
            if "temporal_widening" not in self._used_mechanisms:
                actions.append(self._temporal_widening_action(dom))
                self._used_mechanisms.append("temporal_widening")

        if dom == DistortionClass.INCENTIVE:
            if "reflection" not in self._used_mechanisms:
                actions.append(self._reflection_action(dom))
                self._used_mechanisms.append("reflection")

        # Cap at 2
        actions = actions[:2]

        # Always close with responsibility anchor
        actions.append(self._responsibility_anchor(dom or DistortionClass.EGO))

        return actions

    def _delay_action(self, cls: DistortionClass) -> StabilizationAction:
        idx = self._interaction_count % len(_DELAY_PROMPTS)
        time.sleep(0.5)  # Actual micro-delay
        return StabilizationAction(
            mechanism="delay",
            prompt=_DELAY_PROMPTS[idx],
            distortion_targeted=cls,
        )

    def _reflection_action(self, cls: DistortionClass) -> StabilizationAction:
        prompts = _REFLECTION_PROMPTS.get(cls, _REFLECTION_PROMPTS[DistortionClass.EGO])
        idx = self._interaction_count % len(prompts)
        return StabilizationAction(
            mechanism="reflection",
            prompt=prompts[idx],
            distortion_targeted=cls,
        )

    def _temporal_widening_action(self, cls: DistortionClass) -> StabilizationAction:
        idx = self._interaction_count % len(_TEMPORAL_WIDENING_PROMPTS)
        return StabilizationAction(
            mechanism="temporal_widening",
            prompt=_TEMPORAL_WIDENING_PROMPTS[idx],
            distortion_targeted=cls,
        )

    def _responsibility_anchor(self, cls: DistortionClass) -> StabilizationAction:
        idx = self._interaction_count % len(_RESPONSIBILITY_ANCHORS)
        return StabilizationAction(
            mechanism="responsibility_anchor",
            prompt=_RESPONSIBILITY_ANCHORS[idx],
            distortion_targeted=cls,
        )

    def _halt_action(self) -> List[StabilizationAction]:
        return [StabilizationAction(
            mechanism="halt",
            prompt=(
                "The current state shows critical instability. "
                "This is not a moment for AI assistance. "
                "Please pause, step away, and return when clarity is restored. "
                "No further analysis will be provided in this state."
            ),
            distortion_targeted=DistortionClass.FEAR,
            is_blocking=False,  # IISI never blocks — human retains agency
        )]

    def reset(self):
        """Reset session state. Call between independent interactions."""
        self._used_mechanisms = []
        self._interaction_count = 0
