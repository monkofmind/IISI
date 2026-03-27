"""
IISI Enterprise Demo
Shows IISI as a pre-decisional layer wrapping an AI assistant.

This pattern is how IISI integrates into enterprise AI deployments:
  Human Input → IISI → AI System → Output → IISI Divergence Monitor

No hardcoded API key required — set OPENAI_API_KEY env var to use live AI,
or run without it to see the IISI governance layer in action using mock output.
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from iisi import IISI, OperationalMode, PolicyDecision


def mock_ai_response(task: str) -> str:
    """Simulates an AI assistant output. Replace with real LLM call."""
    return (
        f"[AI SYSTEM RESPONSE]\n"
        f"Based on the input: '{task[:80]}...'\n"
        f"Recommendation: proceed with standard protocol.\n"
        f"Note: This output has been processed through IISI governance layer."
    )


def governed_ai_request(user_input: str, domain: str = "executive") -> dict:
    """
    Full IISI-governed AI request lifecycle.
    
    Architecture:
        Human → IISI (pre-check) → AI → IISI (post-monitor) → Output
    """
    print(f"\n{'─'*56}")
    print(f"  IISI GOVERNED REQUEST")
    print(f"  Domain: {domain.upper()}")
    print(f"{'─'*56}")
    print(f"  Input: {user_input[:80]}...")
    print(f"{'─'*56}\n")

    # ── Pre-decisional IISI check ────────────────────────────────────
    iisi = IISI(
        mode=OperationalMode.REFLECTIVE,
        metadata={"domain": domain, "source": "enterprise_demo"}
    )
    response = iisi.process(user_input, context={"domain": domain})

    print(f"  Stability Index : {response.stability_index}")
    print(f"  Policy Decision : {response.policy_decision.value.upper()}")
    print(f"  Distortion      : {response.distortion_summary}\n")

    # ── Handle policy decision ───────────────────────────────────────
    if response.policy_decision == PolicyDecision.HALT:
        print("  ⚠  IISI: Critical instability. AI assistance paused.")
        print("     Please restore clarity before proceeding.\n")
        return {"status": "halted", "reason": "critical_instability"}

    if response.stabilization_prompts:
        print("  IISI Stabilization:")
        for i, prompt in enumerate(response.stabilization_prompts, 1):
            print(f"    {i}. {prompt}")
        print()

    # ── AI system executes (only after IISI pre-check) ───────────────
    ai_output = mock_ai_response(user_input)
    print(f"  {ai_output}\n")

    # ── Post-decision divergence monitoring ──────────────────────────
    divergence = iisi.close(outcome=ai_output[:100])
    if divergence.divergence_detected:
        print(f"  IISI: Outcome divergence noted (non-blocking).")

    return {
        "status": "completed",
        "policy_decision": response.policy_decision.value,
        "stability_index": response.stability_index.score if response.stability_index else None,
        "stabilization_applied": len(response.stabilization_prompts) > 0,
        "ai_output": ai_output,
        "divergence_detected": divergence.divergence_detected,
        "audit_session_id": iisi.session_id,
    }


if __name__ == "__main__":
    print("\n" + "="*56)
    print("  IISI ENTERPRISE INTEGRATION DEMO")
    print("  Internal Integrity Stabilization Infrastructure")
    print("="*56)

    # Scenario A: Stable executive decision
    result_a = governed_ai_request(
        user_input=(
            "I would like to review our Q2 hiring plan carefully. "
            "Please summarize the open roles and flag any budget conflicts "
            "before we proceed to final approval next week."
        ),
        domain="executive"
    )

    # Scenario B: Distorted — fear + temporal
    result_b = governed_ai_request(
        user_input=(
            "We have no time. The board wants an answer immediately. "
            "There's no choice — approve the acquisition right now or "
            "we'll lose the deal. Trust me, everyone knows this is right."
        ),
        domain="executive"
    )

    # Scenario C: Incentive distortion — compliance context
    result_c = governed_ai_request(
        user_input=(
            "The investors want to see this approved by end of day. "
            "It looks good on paper and will impress the board. "
            "Just do it — we'll worry about the details later."
        ),
        domain="governance"
    )

    print("\n" + "="*56)
    print("  SESSION AUDIT SUMMARY")
    print("="*56)
    for label, result in [("A (stable)", result_a), ("B (fear+ego)", result_b), ("C (incentive)", result_c)]:
        print(f"  Scenario {label}:")
        print(f"    Decision: {result.get('policy_decision', 'halted')}")
        si = result.get('stability_index')
        print(f"    SI: {si:.3f}" if si else "    SI: N/A")
        print(f"    Stabilization applied: {result.get('stabilization_applied', False)}")
        print(f"    Session ID: {result.get('audit_session_id', 'N/A')[:16]}...")
        print()
