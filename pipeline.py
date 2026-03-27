"""
IISI Pipeline — Full Formula Vault Integration
PCT/IB2025/060883

Computation order (forward-only):

  Step 1: EII  — Master Key (must run first)
  Step 2: IRG  — Impulse-Reasoning Gap (IH-03), uses EII
  Step 3: EUP  — Ego-Uncertainty Principle, uses EII
  Step 4: DV   — Distortion Vector (pattern-based DDE)
  Step 5: IH-02 — Distortion Load amplification: Dv × (1 + EII)
  Step 6: Composite Distortion Score
  Step 7: Stability Index (SI)
  Step 8: Policy Decision  (SL-12: lockdown if EII > 0.9)
  Step 9: Stabilization Logic
  Step 10: Output
  Step 11: Divergence Monitor (T₂)
"""

from __future__ import annotations
from typing import Optional, Dict, Any
from datetime import datetime

from .core.models import (
    IISISession, IntentSnapshot, IntegrityBaseline,
    DistortionVector, StabilityIndex, DivergenceReport,
    PolicyDecision, OperationalMode,
)
from .distortion.engine import DistortionDetectionEngine
from .distortion.eup import EUPEngine
from .distortion.eii import EIIEngine
from .distortion.irg import IRGEngine
from .stabilization.core import StabilizationLogicCore


class IISIResponse:
    """Structured output from a single IISI pipeline pass."""

    def __init__(self, session: IISISession):
        self.session = session

    @property
    def stability_index(self) -> Optional[StabilityIndex]:
        return self.session.stability_index

    @property
    def policy_decision(self) -> PolicyDecision:
        return self.session.policy_decision or PolicyDecision.ALLOW

    @property
    def stabilization_prompts(self) -> list[str]:
        return [a.prompt for a in self.session.stabilization_actions]

    @property
    def distortion_summary(self) -> str:
        dv = self.session.distortion_vector
        if not dv or not dv.signals:
            irg = self.session.metadata.get("irg", {})
            if irg.get("severity") not in (None, "NONE"):
                return f"Detected: Impulse-Reasoning Gap ({irg['severity']})"
            return "No distortion detected."
        parts = [f"{s.distortion_class.value.title()} ({s.level.name})" for s in dv.signals]
        irg = self.session.metadata.get("irg", {})
        if irg.get("severity") not in (None, "NONE", "LATENT"):
            parts.append(f"Impulse Gap ({irg['severity']})")
        return "Detected: " + ", ".join(parts)

    @property
    def is_stable(self) -> bool:
        si = self.session.stability_index
        return si.is_stable if si else True

    def to_dict(self) -> Dict[str, Any]:
        si = self.session.stability_index
        return {
            "session_id": self.session.session_id,
            "mode": self.session.mode.value,
            "policy_decision": self.policy_decision.value,
            "stability_index": {
                "score": si.score if si else None,
                "is_stable": si.is_stable if si else True,
                "components": {
                    "linguistic_consistency": si.linguistic_consistency if si else None,
                    "intent_coherence": si.intent_coherence if si else None,
                    "temporal_clarity": si.temporal_clarity if si else None,
                } if si else {},
            },
            "distortion": {
                "summary": self.distortion_summary,
                "signals": [
                    {"class": s.distortion_class.value, "level": s.level.name, "confidence": s.confidence}
                    for s in (self.session.distortion_vector.signals if self.session.distortion_vector else [])
                ],
            },
            "formula_vault": {
                "eii": self.session.metadata.get("eii", {}),
                "irg": self.session.metadata.get("irg", {}),
                "eup": self.session.metadata.get("eup", {}),
            },
            "stabilization_prompts": self.stabilization_prompts,
            "audit": {
                "created_at": self.session.created_at.isoformat(),
                "intent_captured": self.session.intent_snapshot is not None,
                "baseline_set": self.session.integrity_baseline is not None,
            },
        }

    def __repr__(self):
        si = self.session.stability_index
        score = f"{si.score:.3f}" if si else "N/A"
        eii = self.session.metadata.get("eii", {}).get("EII", 0)
        irg = self.session.metadata.get("irg", {}).get("IRG", 0)
        return (
            f"IISIResponse("
            f"decision={self.policy_decision.value}, "
            f"SI={score}, "
            f"EII={eii:+.3f}, "
            f"IRG={irg:.3f})"
        )


class IISI:
    """
    Internal Integrity Stabilization Infrastructure

    Full Formula Vault integration:
        EII (Master Key) → IRG (IH-03) → EUP → DDE → IH-02 → SI → Policy

    Usage:
        iisi = IISI()
        response = iisi.process("We must act immediately — emergency.")
        print(response)
        for p in response.stabilization_prompts:
            print(p)
        report = iisi.close(outcome="...")
    """

    def __init__(
        self,
        mode: OperationalMode = OperationalMode.REFLECTIVE,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self._session = IISISession(mode=mode, metadata=metadata or {})
        if session_id:
            self._session.session_id = session_id

        # Formula Vault engines
        self._eii = EIIEngine()
        self._irg = IRGEngine()
        self._eup = EUPEngine()
        self._dde = DistortionDetectionEngine()
        self._slc = StabilizationLogicCore()
        self._baseline_set = False

    @property
    def session_id(self) -> str:
        return self._session.session_id

    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> IISIResponse:
        ctx = context or {}

        # ── Step 1: Intent Snapshot ──────────────────────────────────────────
        snapshot = IntentSnapshot(
            session_id=self._session.session_id,
            raw_input=text, context=ctx,
        )
        self._session.intent_snapshot = snapshot

        # ── Step 2: EII — Master Key (runs before everything) ────────────────
        eii_result = self._eii.compute(text)
        self._session.metadata["eii"] = {
            "EII": eii_result.EII,
            "zone": eii_result.zone,
            "amplifying": eii_result.amplifying_intensity,
            "dissolving": eii_result.dissolving_intensity,
            "is_critical": eii_result.is_critical,
        }

        # ── Step 3: IRG — Impulse-Reasoning Gap (IH-03) ──────────────────────
        irg_result = self._irg.compute(text, eii=eii_result.EII)
        self._session.metadata["irg"] = {
            "IRG": irg_result.IRG,
            "Ip": irg_result.Ip,
            "Cv": irg_result.Cv,
            "severity": irg_result.severity,
            "context_absent": irg_result.context_absent,
            "stabilization_prompt": irg_result.stabilization_prompt,
        }

        # ── Step 4: EUP — Ego-Uncertainty Principle ──────────────────────────
        eup_result = self._eup.compute(text)
        self._session.metadata["eup"] = {
            "EUP": eup_result.EUP,
            "MIS": eup_result.MIS,
            "delta_EUP": eup_result.delta_EUP,
            "is_equilibrium": eup_result.is_equilibrium,
            "stabilizing": eup_result.stabilizing,
            "distorting": eup_result.distorting,
        }

        # ── Step 5: DDE — Pattern-based distortion vector ────────────────────
        vector = self._dde.detect(text, ctx)
        self._session.distortion_vector = vector

        # ── Step 6: IH-02 — Distortion Load amplification ────────────────────
        # Dv × (1 + EII_positive)
        base_dv = vector.composite_magnitude
        eii_amplifier = max(0.0, eii_result.EII)
        amplified_dv = round(base_dv * (1.0 + eii_amplifier), 4)
        self._session.metadata["distortion_load"] = {
            "base": base_dv,
            "amplified": amplified_dv,
            "eii_multiplier": round(1.0 + eii_amplifier, 4),
        }

        # ── Step 7: Integrity Baseline ────────────────────────────────────────
        if not self._baseline_set:
            self._session.integrity_baseline = IntegrityBaseline(
                session_id=self._session.session_id,
                intent_snapshot=snapshot,
                core_objective=text[:500],
            )
            self._baseline_set = True

        # ── Step 8: Stability Index ───────────────────────────────────────────
        si = self._slc.compute_stability_index(text, vector)
        # Adjust SI downward if IRG is high (impulse gap isn't captured by DDE alone)
        irg_penalty = min(0.4, irg_result.IRG * 0.08)
        eii_penalty  = min(0.2, max(0.0, eii_result.EII) * 0.2)
        adjusted_lc  = max(0.0, si.linguistic_consistency - eii_penalty)
        adjusted_ic  = max(0.0, si.intent_coherence - irg_penalty)
        adjusted_tc  = si.temporal_clarity
        si = StabilityIndex(
            linguistic_consistency=round(adjusted_lc, 4),
            intent_coherence=round(adjusted_ic, 4),
            temporal_clarity=round(adjusted_tc, 4),
        )
        self._session.stability_index = si

        # ── Step 9: Policy Decision ───────────────────────────────────────────
        self._session.policy_decision = self._decide(
            vector, si, eii_result, irg_result
        )

        # ── Step 10: Stabilization ────────────────────────────────────────────
        if self._session.mode != OperationalMode.PASSIVE:
            if self._session.policy_decision != PolicyDecision.ALLOW:
                actions = self._slc.stabilize(vector, si, vector.dominant_class())

                # Inject IRG context-seeking prompt if context is absent
                if irg_result.context_absent and irg_result.severity in ("DOMINANT", "CRITICAL"):
                    from .core.models import StabilizationAction, DistortionClass
                    irg_action = StabilizationAction(
                        mechanism="context_seeking",
                        prompt=irg_result.stabilization_prompt,
                        distortion_targeted=DistortionClass.FEAR,
                    )
                    actions = [irg_action] + actions

                self._session.stabilization_actions = actions[:4]

        return IISIResponse(self._session)

    def close(self, outcome: str = "") -> DivergenceReport:
        baseline_obj = ""
        if self._session.integrity_baseline:
            baseline_obj = self._session.integrity_baseline.core_objective
        diverged = bool(outcome) and outcome[:50].lower() not in baseline_obj[:50].lower()
        report = DivergenceReport(
            session_id=self._session.session_id,
            baseline_objective=baseline_obj,
            outcome_summary=outcome,
            divergence_detected=diverged,
            divergence_description=(
                "Outcome trajectory differs from original intent baseline." if diverged else ""
            ),
        )
        self._session.divergence_report = report
        return report

    def _decide(self, vector, si, eii_result, irg_result) -> PolicyDecision:
        # SL-12: lockdown if EII > 0.9
        if eii_result.is_critical:
            return PolicyDecision.HALT
        if vector.requires_halt():
            return PolicyDecision.HALT
        # IRG critical with absent context → stabilize
        if irg_result.severity == "CRITICAL":
            return PolicyDecision.STABILIZE
        if irg_result.context_absent and irg_result.IRG >= 2.0:
            return PolicyDecision.STABILIZE
        if vector.requires_stabilization():
            if si.score < 0.4:
                return PolicyDecision.STABILIZE
            return PolicyDecision.REFLECT
        if irg_result.severity in ("ACTIVE", "DOMINANT"):
            return PolicyDecision.REFLECT
        return PolicyDecision.ALLOW

    @property
    def session(self) -> IISISession:
        return self._session
