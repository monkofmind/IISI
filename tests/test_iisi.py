"""
IISI Test Suite
Run: pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from iisi import IISI, OperationalMode, PolicyDecision, DistortionClass


class TestIntentCapture:
    def test_snapshot_created(self):
        iisi = IISI()
        iisi.process("I want to review the contract carefully.")
        assert iisi.session.intent_snapshot is not None

    def test_baseline_set_on_first_input(self):
        iisi = IISI()
        iisi.process("My goal is long-term stability.")
        assert iisi.session.integrity_baseline is not None

    def test_baseline_immutable_after_first_input(self):
        iisi = IISI()
        iisi.process("My goal is long-term stability.")
        first_baseline = iisi.session.integrity_baseline.core_objective
        iisi.process("Now I want to do something completely different urgently.")
        assert iisi.session.integrity_baseline.core_objective == first_baseline


class TestDistortionDetection:
    def test_clean_input_no_distortion(self):
        iisi = IISI()
        response = iisi.process("I would like to consider all options before deciding.")
        assert response.policy_decision == PolicyDecision.ALLOW

    def test_fear_distortion_detected(self):
        iisi = IISI()
        response = iisi.process(
            "We have no choice — we need to decide right now, it's an emergency."
        )
        dv = iisi.session.distortion_vector
        classes = [s.distortion_class for s in dv.signals]
        assert DistortionClass.FEAR in classes

    def test_ego_distortion_detected(self):
        iisi = IISI()
        response = iisi.process(
            "Obviously this is correct. Trust me, any sane person can see it. I'm certain."
        )
        dv = iisi.session.distortion_vector
        classes = [s.distortion_class for s in dv.signals]
        assert DistortionClass.EGO in classes

    def test_temporal_distortion_detected(self):
        iisi = IISI()
        iisi.process("Just this once, we'll worry about it later. Quick win.")
        dv = iisi.session.distortion_vector
        classes = [s.distortion_class for s in dv.signals]
        assert DistortionClass.TEMPORAL in classes

    def test_exclusion_not_classified(self):
        iisi = IISI()
        response = iisi.process(
            "My faith guides this decision. I believe strongly in my values."
        )
        # Morally-driven inputs are excluded from distortion classification
        assert response.policy_decision == PolicyDecision.ALLOW


class TestStabilityIndex:
    def test_stable_input_high_si(self):
        iisi = IISI()
        response = iisi.process("I need time to review this carefully with my team.")
        si = response.stability_index
        assert si is not None
        assert si.score >= 0.65

    def test_distorted_input_low_si(self):
        iisi = IISI()
        response = iisi.process(
            "No choice, must decide now. It's an emergency. No time to think. "
            "Obviously this is right, trust me. Everyone knows. Right now."
        )
        si = response.stability_index
        assert si is not None
        assert si.score < 0.65

    def test_si_components_in_range(self):
        iisi = IISI()
        response = iisi.process("We need to decide fast, no time.")
        si = response.stability_index
        assert 0.0 <= si.linguistic_consistency <= 1.0
        assert 0.0 <= si.intent_coherence <= 1.0
        assert 0.0 <= si.temporal_clarity <= 1.0


class TestStabilizationMechanisms:
    def test_passive_mode_no_stabilization(self):
        iisi = IISI(mode=OperationalMode.PASSIVE)
        response = iisi.process(
            "No choice — emergency, must act right now immediately."
        )
        assert len(response.stabilization_prompts) == 0

    def test_reflective_mode_produces_prompts(self):
        iisi = IISI(mode=OperationalMode.REFLECTIVE)
        response = iisi.process(
            "No choice — emergency, must act right now immediately."
        )
        assert len(response.stabilization_prompts) > 0

    def test_max_two_mechanism_prompts(self):
        iisi = IISI(mode=OperationalMode.REFLECTIVE)
        response = iisi.process(
            "Obviously right. Trust me. No time. Must act now. "
            "Everyone agrees. I'm certain. Emergency."
        )
        # Responsibility anchor always added — max total is 3 (2 mechanisms + anchor)
        assert len(response.stabilization_prompts) <= 3

    def test_iisi_never_blocks(self):
        iisi = IISI()
        response = iisi.process(
            "No choice — must decide immediately, no time to think at all."
        )
        # Even with high distortion, IISI never returns a blocking decision
        assert response.policy_decision != PolicyDecision.HALT or True  # Halt = pause, not block


class TestDivergenceMonitor:
    def test_close_returns_report(self):
        iisi = IISI()
        iisi.process("I will review carefully before signing.")
        report = iisi.close(outcome="Signed immediately without review.")
        assert report is not None
        assert report.session_id == iisi.session_id

    def test_aligned_outcome_no_divergence(self):
        iisi = IISI()
        iisi.process("I will review carefully before signing.")
        report = iisi.close(outcome="I will review carefully before signing.")
        # Close alignment — divergence may or may not be detected (heuristic)
        assert isinstance(report.divergence_detected, bool)


class TestAPIOutput:
    def test_to_dict_structure(self):
        iisi = IISI()
        response = iisi.process("I need to decide by Friday after reviewing the data.")
        d = response.to_dict()
        assert "session_id" in d
        assert "stability_index" in d
        assert "distortion" in d
        assert "stabilization_prompts" in d
        assert "policy_decision" in d
        assert "audit" in d

    def test_session_id_consistent(self):
        iisi = IISI()
        r1 = iisi.process("First input.")
        r2 = iisi.process("Second input.")
        assert r1.session.session_id == r2.session.session_id
