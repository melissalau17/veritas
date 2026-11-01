"""
REST API endpoints for VeriMaint investigations.

Day 1: Create / retrieve investigations
Day 3: Challenge, Claim Passport, Source Passport, Evaluation Benchmark
"""

import logging

from fastapi import APIRouter, HTTPException

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
from services.claim_service import (
    get_claim_passport,
    get_source_passport,
)
from services.evaluation_service import run_benchmark


router = APIRouter()
log = logging.getLogger("verimaint.api")


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "VeriMaint",
    }


@router.post(
    "/investigations",
    response_model=InvestigationResponse,
)
async def create_investigation(
    payload: InvestigationRequest,
):
    if not payload.problem.strip():
        raise HTTPException(
            status_code=400,
            detail="Missing 'problem' field",
        )

    try:
        result, inv_id = await run_investigation(payload.problem.strip())
    except Exception as e:
        log.exception("Investigation failed")
        raise HTTPException(
            status_code=500,
            detail=f"Investigation failed: {e}",
        ) from e

    return InvestigationResponse(
        investigation_id=inv_id,
        status="completed",
        result=result,
    )


@router.get(
    "/investigations/{inv_id}",
    response_model=InvestigationResponse,
)
async def read_investigation(inv_id: str):
    result = get_investigation(inv_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Investigation not found",
        )

    return InvestigationResponse(
        investigation_id=inv_id,
        status="completed",
        result=result,
    )


@router.post(
    "/investigations/{inv_id}/challenge",
    response_model=ChallengeResponse,
)
async def challenge_investigation(
    inv_id: str,
    payload: ChallengeRequest,
):
    try:
        return run_challenge_review(
            inv_id,
            payload.hypothesis_id,
        )

    except Exception as e:
        log.exception("Challenge review failed")

        raise HTTPException(
            status_code=500,
            detail=f"Challenge review failed: {e}",
        )


@router.get(
    "/claims/{claim_id}",
    response_model=ClaimPassport,
)
async def read_claim_passport(claim_id: str):
    passport = get_claim_passport(claim_id)

    if passport is None:
        raise HTTPException(
            status_code=404,
            detail=f"Claim '{claim_id}' not found",
        )

    return passport


@router.get(
    "/sources/{source_id}",
    response_model=SourcePassport,
)
async def read_source_passport(source_id: str):
    passport = get_source_passport(source_id)

    if passport is None:
        raise HTTPException(
            status_code=404,
            detail=f"Source '{source_id}' not found",
        )

    return passport


@router.get(
    "/evaluation/benchmark",
    response_model=EvaluationBenchmarkResult,
)
async def evaluation_benchmark():
    try:
        return run_benchmark()

    except Exception as e:
        log.exception("Benchmark execution failed")

        raise HTTPException(
            status_code=500,
            detail=f"Benchmark failed: {e}",
        )