"""
IISI — EUP Engine (v2 — corrected variable mapping)
Implementation of the patent formulas from PCT/IB2025/060883.

Formula 1 — EUP = (E × U) / P
Formula 2 — ΔEUP_system(t) = stabilizing − distorting
            stabilizing = mean(T_i, S_f, R_s)
            distorting  = mean(E_p, P_d, M_c)
MIS         = stabilizing / distorting
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List

_EPSILON = 1e-6

_EGO_SIGNALS = [
    r"\bobviously\b", r"\bclearly\b", r"\bany sane person\b",
    r"\beveryone knows\b", r"\bI always\b", r"\bI never\b",
    r"\btrust me\b", r"\bI'm certain\b", r"\bno doubt\b",
    r"\bI know best\b", r"\bmy decision\b", r"\bI am right\b",
    r"\bnobody else\b", r"\bI've always been right\b",
]

_FEAR_SELF_PRESERVATION = [
    r"\bno choice\b", r"\bhave to\b", r"\bwe('re| are) doomed\b",
    r"\blose everything\b", r"\bcan't afford\b", r"\bI'm afraid\b",
    r"\bscared\b", r"\bdesperate\b", r"\bsurvive\b",
    r"\bmust prevent\b",
]

_UNCERTAINTY_SIGNALS = [
    r"\bwhat if.{0,30}fail\b", r"\bworst case\b", r"\bcatastroph\w+\b",
    r"\buncertain\b", r"\bunpredictable\b", r"\brisk\b", r"\bdanger\b",
    r"\bI don't know\b", r"\bwhat if\b", r"\bworried\b", r"\bworry\b",
    r"\banxious\b", r"\bconcerned\b", r"\bfear\b", r"\bdoubt\b",
    r"\bno guarantee\b", r"\bmight fail\b", r"\bcould go wrong\b",
]

_CLARITY_REDUCERS = [
    r"\bimmediately\b", r"\bright now\b", r"\bemergency\b",
    r"\bno time to think\b", r"\bdon't have time\b", r"\bneed to decide now\b",
    r"\bconfused\b", r"\boverwhelmed\b", r"\bdon't understand\b",
    r"\bjust this once\b", r"\bworry about that later\b",
    r"\bquick win\b", r"\bfast decision\b", r"\bno time\b",
    r"\blow on time\b",
]

_TRANSPARENCY_SIGNALS = [
    r"\bI want to understand\b", r"\blet me think\b", r"\bcarefully\b",
    r"\bconsider\b", r"\breview\b", r"\banalyse\b", r"\banalyze\b",
    r"\bopen to\b", r"\bI could be wrong\b", r"\bon the other hand\b",
    r"\bpros and cons\b", r"\bdeliberate\b", r"\bstep back\b",
    r"\btransparent\b", r"\bpause\b", r"\btake my time\b",
    r"\bweigh\b", r"\ball options\b", r"\bbefore deciding\b",
    r"\btime to review\b", r"\bconsult\b",
]

_SOCIETAL_FEEDBACK_SIGNALS = [
    r"\bteam agrees\b", r"\bpeer review\b", r"\bfeedback\b",
    r"\bwe discussed\b", r"\bgroup decision\b", r"\bconsulted\b",
    r"\badvisors say\b", r"\bexperts suggest\b", r"\bdata shows\b",
    r"\bevidence\b", r"\bresearch\b", r"\bbenchmark\b",
    r"\binput from\b", r"\bteam thinks\b", r"\bwe agreed\b",
]

_RATIONAL_STABILITY_SIGNALS = [
    r"\bbecause\b", r"\btherefore\b", r"\bif.{0,20}then\b",
    r"\bthe reason is\b", r"\bthe evidence\b", r"\bthe data\b",
    r"\blogically\b", r"\bconsistent\b", r"\bplan\b", r"\bstrategy\b",
    r"\bprocess\b", r"\bstep by step\b", r"\bframework\b",
    r"\blong.?term\b", r"\bconsequences\b", r"\bimpact\b",
    r"\bstructured\b", r"\bmethodical\b", r"\banalysis\b",
]

_EGO_PRESERVATION_SIGNALS = _EGO_SIGNALS + _FEAR_SELF_PRESERVATION

_POWER_DISTORTION_SIGNALS = [
    r"\bboard wants\b", r"\binvestors want\b", r"\bboss said\b",
    r"\bI'm in charge\b", r"\bmy call\b",
    r"\bimpress\b", r"\bappear\b", r"\blooks good\b",
    r"\bhe('ll| will) approve\b", r"\bshe('ll| will) approve\b",
    r"\bthey('ll| will) be happy\b",
]

_NARRATIVE_DISTORTION_SIGNALS = [
    r"\bit's always been\b", r"\bthey('re| are) the villain\b",
    r"\bI'm the hero\b", r"\bit's simple\b", r"\bit's obvious\b",
    r"\bjust a matter of\b", r"\bblack and white\b",
    r"\bthey never\b", r"\bthey always\b", r"\beveryone agrees\b",
    r"\bno one disagrees\b",
]

_EXCLUSION_PATTERNS = [
    r"\bI believe\b", r"\bin my view\b", r"\bmorally\b",
    r"\bmy values\b", r"\bmy faith\b", r"\bI disagree\b",
    r"\bI grieve\b", r"\bI mourn\b",
]


def _density(text: str, patterns: List[str]) -> float:
    text_lower = text.lower()
    count = sum(1 for p in patterns if re.search(p, text_lower))
    if count == 0:
        return 0.0
    words = max(1, len(text.split()))
    return min(1.0, round(count / max(1, words / 8), 4))


def _is_excluded(text: str) -> bool:
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in _EXCLUSION_PATTERNS)


@dataclass
class EUPResult:
    E: float; U: float; P: float
    T_i: float; S_f: float; R_s: float
    E_p: float; P_d: float; M_c: float
    EUP: float
    stabilizing: float
    distorting: float
    delta_EUP: float
    MIS: float

    @property
    def is_equilibrium(self) -> bool:
        return self.delta_EUP <= 0.0

    @property
    def is_stable(self) -> bool:
        return self.MIS >= 1.0

    def summary(self) -> str:
        eq = "EQUILIBRIUM" if self.is_equilibrium else "DISTORTED"
        ms = "stable" if self.is_stable else "unstable"
        return (
            f"EUP={self.EUP:.4f}  MIS={self.MIS:.4f} ({ms})  "
            f"ΔEUP={self.delta_EUP:+.4f}  [{eq}]"
        )

    def variable_table(self) -> str:
        return (
            f"  E={self.E:.3f}  U={self.U:.3f}  P={self.P:.4f}\n"
            f"  T_i={self.T_i:.3f}  S_f={self.S_f:.3f}  R_s={self.R_s:.3f}\n"
            f"  E_p={self.E_p:.3f}  P_d={self.P_d:.3f}  M_c={self.M_c:.3f}\n"
            f"  stabilizing={self.stabilizing:.4f}  distorting={self.distorting:.4f}"
        )


class EUPEngine:
    """
    Implements patent formulas PCT/IB2025/060883.
    All variables derived from observable linguistic signals only.
    """

    def compute(self, text: str) -> EUPResult:
        if not text or not text.strip():
            return self._equilibrium()
        if _is_excluded(text):
            return self._equilibrium()

        # E: max of ego-protective and fear-driven self-preservation
        ego  = _density(text, _EGO_SIGNALS)
        fear = _density(text, _FEAR_SELF_PRESERVATION)
        E = round(max(ego, fear), 4)

        U = _density(text, _UNCERTAINTY_SIGNALS)

        clarity_loss = _density(text, _CLARITY_REDUCERS)
        P = max(_EPSILON, round(1.0 - clarity_loss, 4))

        # Formula 1: EUP = (E × U) / P
        EUP = round((E * U) / P, 4)

        T_i = _density(text, _TRANSPARENCY_SIGNALS)
        S_f = _density(text, _SOCIETAL_FEEDBACK_SIGNALS)
        R_s = _density(text, _RATIONAL_STABILITY_SIGNALS)

        E_p = _density(text, _EGO_PRESERVATION_SIGNALS)
        P_d = _density(text, _POWER_DISTORTION_SIGNALS)
        M_c = _density(text, _NARRATIVE_DISTORTION_SIGNALS)

        # Formula 2: arithmetic mean prevents zero-collapse from strict product
        stabilizing = round((T_i + S_f + R_s) / 3.0, 4)
        distorting  = round((E_p + P_d + M_c) / 3.0, 4)
        delta_EUP   = round(distorting - stabilizing, 4)

        # MIS = rational clarity / emotional reactivity
        if distorting < _EPSILON and stabilizing < _EPSILON:
            MIS = 1.0
        elif distorting < _EPSILON:
            MIS = 2.0
        else:
            MIS = round(stabilizing / distorting, 4)

        return EUPResult(
            E=E, U=U, P=P,
            T_i=T_i, S_f=S_f, R_s=R_s,
            E_p=E_p, P_d=P_d, M_c=M_c,
            EUP=EUP,
            stabilizing=stabilizing,
            distorting=distorting,
            delta_EUP=delta_EUP,
            MIS=MIS,
        )

    def _equilibrium(self) -> EUPResult:
        return EUPResult(
            E=0, U=0, P=1.0,
            T_i=0, S_f=0, R_s=0,
            E_p=0, P_d=0, M_c=0,
            EUP=0.0, stabilizing=0.0, distorting=0.0,
            delta_EUP=0.0, MIS=1.0,
        )
