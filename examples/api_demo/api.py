"""
IISI API Server
Exposes IISI as a REST API. Deploy this to make IISI callable
from any language, any system.

Requirements:
    pip install fastapi uvicorn

Run:
    uvicorn api:app --reload --port 8000

Endpoints:
    POST /process     — run input through IISI pipeline
    POST /close       — close session, get divergence report
    GET  /health      — system status
    GET  /session/{id} — retrieve session audit trail
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from typing import Optional, Dict, Any
from datetime import datetime

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
except ImportError:
    print("Install dependencies: pip install fastapi uvicorn")
    sys.exit(1)

from iisi import IISI, OperationalMode

# ─── In-memory session store (use Redis/DB in production) ────────────────────
_sessions: Dict[str, IISI] = {}
_session_meta: Dict[str, Dict] = {}

# ─── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="IISI API",
    description=(
        "Internal Integrity Stabilization Infrastructure — REST API\n\n"
        "MindTech OS / MG Universe | PCT/IB2025/060883"
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request / Response Models ────────────────────────────────────────────────
class ProcessRequest(BaseModel):
    text: str
    session_id: Optional[str] = None
    mode: Optional[str] = "reflective"
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class CloseRequest(BaseModel):
    session_id: str
    outcome: Optional[str] = ""


# ─── Routes ──────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status": "ok",
        "system": "IISI",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "active_sessions": len(_sessions),
    }


@app.post("/process")
def process(req: ProcessRequest):
    """
    Run input through the IISI pipeline.
    
    Creates a new session if session_id not provided.
    Reuses existing session if session_id provided.
    """
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="text field is required")

    # Resolve mode
    try:
        mode = OperationalMode(req.mode or "reflective")
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid mode: {req.mode}")

    # Get or create session
    sid = req.session_id
    if sid and sid in _sessions:
        iisi = _sessions[sid]
    else:
        iisi = IISI(mode=mode, metadata=req.metadata or {})
        sid = iisi.session_id
        _sessions[sid] = iisi
        _session_meta[sid] = {
            "created_at": datetime.utcnow().isoformat(),
            "mode": mode.value,
        }

    # Process
    response = iisi.process(req.text, context=req.context)

    return {
        "session_id": sid,
        **response.to_dict(),
    }


@app.post("/close")
def close(req: CloseRequest):
    """
    Close a session and receive the divergence report.
    IISI observes divergence — never corrects it.
    """
    if req.session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    iisi = _sessions[req.session_id]
    report = iisi.close(outcome=req.outcome or "")

    # Clean up session
    _sessions.pop(req.session_id, None)

    return {
        "session_id": req.session_id,
        "baseline_objective": report.baseline_objective[:200],
        "outcome_summary": report.outcome_summary[:200],
        "divergence_detected": report.divergence_detected,
        "divergence_description": report.divergence_description,
        "closed_at": report.generated_at.isoformat(),
    }


@app.get("/session/{session_id}")
def get_session(session_id: str):
    """Retrieve audit trail for an active session."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found or already closed")

    iisi = _sessions[session_id]
    session = iisi.session

    return {
        "session_id": session_id,
        "mode": session.mode.value,
        "created_at": session.created_at.isoformat(),
        "baseline_captured": session.integrity_baseline is not None,
        "distortion_signals": len(session.distortion_vector.signals) if session.distortion_vector else 0,
        "stability_score": session.stability_index.score if session.stability_index else None,
        "stabilization_actions_applied": len(session.stabilization_actions),
        "policy_decision": session.policy_decision.value if session.policy_decision else None,
        "meta": _session_meta.get(session_id, {}),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
