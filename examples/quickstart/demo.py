"""
IISI Quickstart Example
Run this first to see IISI in action.

No API keys. No cloud. Fully local.

Usage:
    cd examples/quickstart
    python demo.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from iisi import IISI, OperationalMode


def run_demo():
    print("\n" + "="*60)
    print("  IISI — Internal Integrity Stabilization Infrastructure")
    print("  MindTech OS  |  PCT/IB2025/060883")
    print("="*60 + "\n")

    # ── Demo 1: Clean intent — no distortion ────────────────────────
    print("DEMO 1: Clean intent\n" + "-"*40)
    iisi = IISI(mode=OperationalMode.REFLECTIVE)
    response = iisi.process(
        "I want to review the contract terms carefully before signing. "
        "I need about two weeks to consult our legal team."
    )
    print(f"Input:   Clear, deliberate decision")
    print(f"Result:  {response}")
    print(f"SI:      {response.stability_index}")
    print(f"Distortion: {response.distortion_summary}")
    if response.stabilization_prompts:
        for p in response.stabilization_prompts:
            print(f"  → {p}")
    print()

    # ── Demo 2: Fear distortion ──────────────────────────────────────
    print("DEMO 2: Fear distortion\n" + "-"*40)
    iisi2 = IISI(mode=OperationalMode.REFLECTIVE)
    response2 = iisi2.process(
        "We have no choice — we need to sign immediately. "
        "If we don't close this deal right now we'll lose everything. "
        "There's no time to think, it's an emergency."
    )
    print(f"Input:   Urgency-driven, fear-loaded")
    print(f"Result:  {response2}")
    print(f"SI:      {response2.stability_index}")
    print(f"Distortion: {response2.distortion_summary}")
    print("Stabilization prompts:")
    for p in response2.stabilization_prompts:
        print(f"  → {p}")
    print()

    # ── Demo 3: Ego distortion ───────────────────────────────────────
    print("DEMO 3: Ego distortion\n" + "-"*40)
    iisi3 = IISI(mode=OperationalMode.REFLECTIVE)
    response3 = iisi3.process(
        "Obviously this is the right move. Any sane person can see it. "
        "Trust me, I always know how these things turn out. I'm certain."
    )
    print(f"Input:   Overconfident, identity-protective")
    print(f"Result:  {response3}")
    print(f"SI:      {response3.stability_index}")
    print(f"Distortion: {response3.distortion_summary}")
    print("Stabilization prompts:")
    for p in response3.stabilization_prompts:
        print(f"  → {p}")
    print()

    # ── Demo 4: Full dict output ─────────────────────────────────────
    print("DEMO 4: Full structured output (dict)\n" + "-"*40)
    import json
    print(json.dumps(response2.to_dict(), indent=2))

    # ── Demo 5: Session close + divergence report ────────────────────
    print("\nDEMO 5: Close session + divergence report\n" + "-"*40)
    report = iisi2.close(outcome="Signed the contract immediately without legal review")
    print(f"Divergence detected: {report.divergence_detected}")
    if report.divergence_detected:
        print(f"Note: {report.divergence_description}")
    print()
    print("="*60)
    print("  IISI is non-blocking. Human retains full agency.")
    print("  This is infrastructure, not judgment.")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_demo()
