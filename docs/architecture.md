# IISI Architecture

## Overview

IISI is a **horizontal, pre-decisional infrastructure layer**.

```
Human
  ↓
IISI Layer
  ↓  ↓  ↓  ↓  ↓
 ICI DDE IBG SLC ODM
  ↓
AI / Agent / System
  ↓
Outcome
  ↓
Divergence Monitor
```

IISI never touches model weights, prompt content, or action execution layers.

---

## Components

### ICI — Intent Capture Interface
Captures stated intent at T₀. Normalizes into `IntentSnapshot`. No rewriting.

### DDE — Distortion Detection Engine
Pattern-based signal detection across 5 distortion classes. No psychological profiling. No identity tracking. Outputs `DistortionVector`.

### IBG — Integrity Baseline Generator
Establishes the immutable reference point for the session from the first input. Outputs `IntegrityBaseline`.

### SLC — Stabilization Logic Core
Computes `StabilityIndex` and applies up to 2 non-coercive mechanisms per interaction. Never blocks. Always closes with responsibility anchor.

### ODM — Outcome Divergence Monitor
Post-decision observation. Compares actual outcome against baseline. Flags divergence. Never corrects.

---

## Data Flow

All data flows **forward only**.

```
IntentSnapshot → DistortionVector → IntegrityBaseline → StabilityIndex → PolicyDecision → StabilizationActions → DivergenceReport
```

No retroactive modification of intent is permitted.

---

## Stability Index Formula

```
SI = (LC + IC + TC) / 3

where:
  LC = linguistic_consistency   (reduced by Ego + Narrative distortion)
  IC = intent_coherence         (reduced by Incentive + Fear distortion)
  TC = temporal_clarity         (reduced by Temporal distortion)

Level weights:
  LATENT:   0.15
  ACTIVE:   0.40
  DOMINANT: 0.65
  CRITICAL: 0.90

Reduction per signal = confidence × level_weight
```

Derived from MIS (Mindset Integrity Score), PCT/IB2025/060883.

---

## Policy Decision Logic

```
CRITICAL distortion  →  HALT
SI < 0.40 + ACTIVE   →  STABILIZE
Any ACTIVE distortion →  REFLECT
Otherwise            →  ALLOW
```

---

## Session Lifecycle

```
iisi = IISI()               # Session created
response = iisi.process()   # T₀ — intent captured, distortion detected
response = iisi.process()   # T₁ — same session, baseline unchanged
report = iisi.close()       # T₂ — divergence observed, session ends
```

Sessions are stateless across restarts by default. Opt-in persistence available via session store.

---

## Security & Privacy

- No identity requirement
- No cross-session memory by default
- Session-scoped intent snapshots only
- No psychological profiling
- Minimal data retention

Intent ≠ Identity. Stability ≠ Surveillance.
