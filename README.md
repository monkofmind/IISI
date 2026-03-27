# IISI — Internal Integrity Stabilization Infrastructure

**Decision integrity infrastructure for AI-assisted environments.**

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Patent](https://img.shields.io/badge/patent-PCT%2FIB2025%2F060883-green.svg)](https://mindtechos.com)
[![Tests](https://img.shields.io/badge/tests-19%20passed-brightgreen.svg)](tests/)

---

## What is IISI?

IISI is a **pre-decisional infrastructure layer** that stabilizes human intent before, during, and after interaction with AI systems.

It sits between the human and the AI — detecting when reasoning is distorted by fear, ego, incentive pressure, or short-term thinking, and surfacing that distortion without blocking, judging, or substituting for human judgment.

```
Human → IISI → AI System → Output → IISI Divergence Monitor
```

**IISI does not make decisions.** It stabilizes the conditions under which decisions are made.

---

## The Problem

Modern AI systems amplify three silent failures:

| Failure | What happens |
|---|---|
| **Intent drift** | You start with one goal, end with another — without noticing |
| **Ego contamination** | Confidence, fear, or status-seeking distorts reasoning |
| **Temporal collapse** | Short-term urgency overrides long-term consequence awareness |

AI alignment focuses on model safety. IISI addresses the **human instability layer** — the part no model can fix.

---

## Quickstart

### Install

```bash
# No dependencies required for core IISI
git clone https://github.com/mindtechos/iisi.git
cd iisi
pip install -e .
```

### Basic Usage

```python
from iisi import IISI

iisi = IISI()
response = iisi.process("We have no choice — must decide right now, it's an emergency.")

print(response.policy_decision)          # halt / reflect / stabilize / allow
print(response.stability_index)          # SI=0.715 (LC=1.00, IC=0.14, TC=1.00)
print(response.distortion_summary)       # Detected: Fear (CRITICAL)

for prompt in response.stabilization_prompts:
    print(prompt)
# → "The current state shows critical instability. Please pause..."

# After the decision is made:
report = iisi.close(outcome="Signed the contract immediately.")
print(report.divergence_detected)        # True / False
```

### Run the Demo

```bash
python examples/quickstart/demo.py
```

### Run as an API

```bash
pip install fastapi uvicorn
uvicorn examples.api_demo.api:app --reload --port 8000
```

```bash
# Process input
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"text": "No choice — must sign immediately, emergency."}'

# Close session
curl -X POST http://localhost:8000/close \
  -H "Content-Type: application/json" \
  -d '{"session_id": "<id>", "outcome": "Signed without review."}'
```

---

## How It Works

### Signal Flow (forward-only)

```
Human Input
  → Intent Snapshot (T₀)        — baseline captured, immutable
    → Distortion Detection        — 5-class taxonomy, signal-based
      → Integrity Baseline        — what was actually meant
        → Stability Index         — SI ∈ [0,1], three components
          → Policy Decision       — allow / reflect / stabilize / halt
            → Stabilization       — non-coercive prompts only
              → AI System
                → Outcome
                  → Divergence Monitor (T₂)
```

No signal ever flows backward to alter original intent.

### Stability Index (SI)

```
SI = (linguistic_consistency + intent_coherence + temporal_clarity) / 3
```

Derived from the patent's Mindset Integrity Score (MIS) model.

- **SI ≥ 0.65** — stable, proceed
- **SI 0.40–0.64** — active distortion, stabilization engaged
- **SI < 0.40** — dominant distortion, full stabilization
- **CRITICAL signals** — halt + return agency

### Distortion Classes

| Class | Description | Signals |
|---|---|---|
| **Ego** | Identity-protective reasoning | "obviously", "trust me", "I'm certain" |
| **Fear** | Threat-driven intent collapse | "no choice", "emergency", "right now" |
| **Incentive** | External reward shaping intent | "they'll approve", "looks good", "impress" |
| **Narrative** | Story-fitting overriding reality | "it's simple", "they always", "black and white" |
| **Temporal** | Short-term overriding long-term | "just this once", "worry later", "quick win" |

### What IISI Never Does

- ❌ Block action
- ❌ Substitute judgment
- ❌ Claim correctness
- ❌ Enforce morality
- ❌ Profile users psychologically
- ❌ Learn or adapt across sessions by default
- ❌ Classify grief, moral conviction, or religious belief as distortion

---

## Operational Modes

| Mode | Behaviour |
|---|---|
| `PASSIVE` | Observe only. No intervention. Audit trail only. |
| `REFLECTIVE` | Surface contradictions. Advisory prompts. **(default)** |
| `STABILIZATION` | Full delay + reflection mechanisms active. |
| `AUDIT` | Post-decision trace and divergence monitoring only. |

```python
from iisi import IISI, OperationalMode

# Observe without any intervention
iisi = IISI(mode=OperationalMode.PASSIVE)

# Audit mode — for post-decision review only
iisi = IISI(mode=OperationalMode.AUDIT)
```

---

## Policy Packs

Domain-specific thresholds and rules. Drop-in YAML configuration.

```
policy_packs/
├── default/       — general professional use
├── finance/       — ADGM/DIFC aligned, elevated incentive sensitivity
├── healthcare/    — safety-critical, conservative thresholds
└── leadership/    — executive decision contexts
```

Finance pack example — stricter thresholds, regulatory alignment:

```yaml
thresholds:
  stability_index_minimum: 0.50    # vs 0.40 default
  incentive_sensitivity: 1.5
compliance_notes:
  - "Designed for ADGM / DIFC regulatory environment"
```

---

## Enterprise Integration

IISI wraps any AI system without modifying it:

```python
from iisi import IISI, PolicyDecision

def governed_ai_call(user_input: str, ai_fn) -> dict:
    iisi = IISI()
    response = iisi.process(user_input)

    if response.policy_decision == PolicyDecision.HALT:
        return {"status": "paused", "reason": "critical_instability"}

    # Surface stabilization prompts to user before AI runs
    for prompt in response.stabilization_prompts:
        show_to_user(prompt)

    # Run the AI
    ai_output = ai_fn(user_input)

    # Monitor divergence
    report = iisi.close(outcome=ai_output[:200])

    return {
        "ai_output": ai_output,
        "stability_index": response.stability_index.score,
        "divergence_detected": report.divergence_detected,
        "audit_session_id": iisi.session_id,
    }
```

---

## Project Structure

```
iisi/
├── iisi/
│   ├── core/
│   │   └── models.py           — all data structures
│   ├── distortion/
│   │   └── engine.py           — distortion detection (DDE)
│   ├── stabilization/
│   │   └── core.py             — stabilization mechanisms (SLC)
│   └── pipeline.py             — main IISI orchestrator
├── examples/
│   ├── quickstart/             — run this first
│   ├── enterprise_demo/        — IISI wrapping an AI workflow
│   └── api_demo/               — FastAPI REST server
├── policy_packs/
│   ├── default/
│   ├── finance/
│   ├── healthcare/
│   └── leadership/
├── tests/                      — 19 tests, 100% passing
└── docs/
```

---

## Tests

```bash
pip install pytest
pytest tests/ -v
```

19 tests covering: intent capture, distortion detection, stability index, stabilization mechanisms, divergence monitoring, API output.

---

## Roadmap

- [ ] v0.2 — LLM connector (OpenAI, Anthropic, Ollama)
- [ ] v0.2 — Persistent session store (Redis)
- [ ] v0.3 — Dashboard UI (stability trends, session history)
- [ ] v0.3 — Webhook support (real-time distortion alerts)
- [ ] v0.4 — Multi-turn conversation tracking
- [ ] v0.4 — Healthcare and legal policy packs
- [ ] v1.0 — Enterprise SLA + support tier

---

## IP & Licensing

IISI is proprietary software.

**Patent:** PCT/IB2025/060883 — Humanity-Driven Decision Intelligence System (MindTech Framework)  
**Priority date:** 25 October 2025  
**Applicant:** GAJENDRABABU, Prasannaa — Dubai, UAE

Use of this software requires a valid license. Contact: founder@mindtechos.com

For open-source integrations, academic research, or commercial licensing enquiries, see [mindtechos.com/iisi](https://mindtechos.com/iisi).

---

## About

**MindTech OS / MG Universe**  
Dubai, United Arab Emirates  
founder@mindtechos.com  
[mindtechos.com](https://mindtechos.com)

> *IISI does not exist to make decisions easier.*  
> *It exists to make irresponsible decisions harder.*
