"""
REST API endpoints for Veritas investigations.

Day 1: Create / retrieve investigations
Day 3: Challenge, Claim Passport, Source Passport, Evaluation Benchmark
"""

import logging
from fastapi import APIRouter, HTTPException

try:
    from schemas import (
        InvestigationRequest,
        InvestigationResponse,
        ChallengeRequest,
        ChallengeResponse,
        ClaimPassport,
        SourcePassport,
        EvaluationBenchmarkResult,
    )
    from services.investigation_service import (
        run_investigation,
        get_investigation,
    )
    from services.challenge_service import run_challenge_review
    from services.claim_service import get_claim_passport, get_source_passport
    from services.evaluation_service import run_benchmark
except ImportError:
    from ..schemas import (
        InvestigationRequest,
        InvestigationResponse,
        ChallengeRequest,
        ChallengeResponse,
        ClaimPassport,
        SourcePassport,
        EvaluationBenchmarkResult,
    )
    from ..services.investigation_service import (
        run_investigation,
        get_investigation,
    )
    from ..services.challenge_service import run_challenge_review
    from ..services.claim_service import get_claim_passport, get_source_passport
    from ..services.evaluation_service import run_benchmark

router = APIRouter()
log = logging.getLogger("veritas.api")


@router.get("/health")
async def health():
    """Simple health-check endpoint."""
    return {"status": "ok", "service": "Veritas"}


@router.post("/investigations", response_model=InvestigationResponse)
async def create_investigation(payload: InvestigationRequest):
    """
    Run a full Veritas investigation.

    Accepts a free-text problem statement and returns
    structured evidence, revision checks, conflicts,
    hypotheses, claims and investigation steps.
    """
    if not payload.problem.strip():
        raise HTTPException(status_code=400, detail="Missing 'problem' field")

    result, inv_id = run_investigation(payload.problem.strip())

    return InvestigationResponse(
        investigation_id=inv_id,
        status="completed",
        result=result,
    )


@router.get("/investigations/{inv_id}", response_model=InvestigationResponse)
async def read_investigation(inv_id: str):
    """Retrieve a previously completed investigation."""
    result = get_investigation(inv_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return InvestigationResponse(
        investigation_id=inv_id,
        status="completed",
        result=result,
    )


# ── Day 3: Challenge Recommendation ─────────────────────

@router.post("/investigations/{inv_id}/challenge", response_model=ChallengeResponse)
async def challenge_investigation(inv_id: str, payload: ChallengeRequest):
    """
    Challenge the leading hypothesis of an existing investigation.

    The counter-evidence reviewer searches for contradictory evidence,
    alternative failure mechanisms, and missing measurements.
    """
    try:
        challenge_result = run_challenge_review(inv_id, payload.hypothesis_id)
        return challenge_result
    except Exception as e:
        log.error("Challenge review failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Challenge review failed: {str(e)}")


# ── Day 3: Claim Passport ───────────────────────────────

@router.get("/claims/{claim_id}", response_model=ClaimPassport)
async def read_claim_passport(claim_id: str):
    """
    Retrieve the Claim Passport for a specific claim.

    Shows supporting sources, contradicting sources, applicability checks,
    revision context, missing information, and confirmation state.
    """
    passport = get_claim_passport(claim_id)
    if passport is None:
        raise HTTPException(status_code=404, detail=f"Claim '{claim_id}' not found")
    return passport


# ── Day 3: Source Passport ───────────────────────────────

@router.get("/sources/{source_id}", response_model=SourcePassport)
async def read_source_passport(source_id: str):
    """
    Retrieve provenance metadata for a specific engineering source document.
    """
    passport = get_source_passport(source_id)
    if passport is None:
        raise HTTPException(status_code=404, detail=f"Source '{source_id}' not found")
    return passport


# ── Day 3: Evaluation Benchmark ──────────────────────────

@router.get("/evaluation/benchmark", response_model=EvaluationBenchmarkResult)
async def evaluation_benchmark():
    """
    Execute the 20-case verification benchmark and return aggregate results.

    Tests revision detection, applicability classification, citation grounding,
    conflict detection, counter-evidence discovery, and false diagnosis rate.
    """
    try:
        return run_benchmark()
    except Exception as e:
        log.error("Benchmark execution failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Benchmark failed: {str(e)}")
