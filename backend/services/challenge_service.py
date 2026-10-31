"""
Service: challenge_service

Implements Veritas's Counter-Evidence Reviewer Agent.
Challenges the leading hypothesis by actively searching for:
- Contradictory evidence
- Alternative failure mechanisms (e.g. bearing degradation)
- Missing measurements that prevent confirmation
- Applicability and revision weaknesses
- Preserves engineering uncertainty
"""

from pathlib import Path
import sys
from typing import Optional, List, Dict, Any

_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from schemas import (
    ChallengeResponse,
    CounterEvidenceItem,
    Hypothesis,
    HypothesisComparisonItem,
    UpdatedAssessment,
    TraceEvent,
)
from tools.find_counter_evidence import find_counter_evidence
from tools.compare_hypotheses import compare_hypotheses
from services.investigation_service import get_investigation


def run_challenge_review(
    investigation_id: str,
    hypothesis_id: str = "H1",
) -> ChallengeResponse:
    """
    Execute an adversarial counter-evidence review against the current leading hypothesis.
    """
    inv = get_investigation(investigation_id)
    asset_id = inv.incident.asset_id if inv and inv.incident else "P-101"

    trace_events: List[TraceEvent] = [
        TraceEvent(
            type="challenge_initiated",
            message=f"Counter-evidence review initiated for hypothesis {hypothesis_id}",
        ),
    ]

    # 1. Search for counter-evidence and alternative failure mechanisms
    counter_data = find_counter_evidence(
        hypothesis="Coupling misalignment",
        asset_id=asset_id,
    )
    trace_events.append(TraceEvent(
        type="counter_evidence_searched",
        message="Searched OEM-Pump-Manual and RCA archives for alternative failure mechanisms",
    ))

    counter_evidence_items: List[CounterEvidenceItem] = []
    for item in counter_data.get("counter_evidence", []):
        counter_evidence_items.append(CounterEvidenceItem(
            source=item["source"],
            text=item["text"],
            type=item.get("type", "alternative_mechanism"),
            section=item.get("section"),
            applicability_warning=item.get("applicability_warning"),
        ))

    # 2. Formulate Alternative Hypothesis H2: Bearing Degradation
    alternative_hypotheses: List[Hypothesis] = [
        Hypothesis(
            id="H2",
            title="Bearing degradation / lubrication failure",
            status="moderate",
            supporting_evidence=["OEM-Pump-Manual.txt"],
            contradicting_evidence=[],
            missing_evidence=[
                "Drive-end bearing temperature log",
                "High-frequency vibration demodulation spectrum",
                "Lubricant grease analysis",
            ],
            confirmed=False,
        ),
        Hypothesis(
            id="H3",
            title="Mounting bolt looseness / soft foot",
            status="weak",
            supporting_evidence=["OEM-Pump-Manual.txt"],
            contradicting_evidence=[],
            missing_evidence=[
                "Baseplate bolt torque verification",
                "Soft foot dial indicator check",
            ],
            confirmed=False,
        ),
    ]
    trace_events.append(TraceEvent(
        type="alternative_hypothesis_generated",
        message="Formulated alternative failure mechanisms H2 (Bearing degradation) and H3 (Mounting looseness)",
    ))

    # 3. Compile Missing Measurements
    missing_information = counter_data.get("missing_evidence", [
        "Current coupling alignment laser/dial indicator reading",
        "Current vibration spectrum (1X vs 2X harmonics)",
        "Bearing temperature measurement",
        "Pre-maintenance baseline comparison",
    ])
    trace_events.append(TraceEvent(
        type="missing_information_identified",
        message=f"Identified {len(missing_information)} critical field measurements missing for confirmation",
    ))

    # 4. Deterministic Comparison of Hypotheses
    raw_hypotheses = [
        {
            "id": "H1",
            "title": "Coupling misalignment",
            "supporting_evidence": ["WO-1842.txt", "RCA-017.txt", "OEM-Pump-Manual.txt"],
            "contradicting_evidence": [],
            "missing_evidence": [
                "Current coupling alignment measurement",
                "Current vibration spectrum",
            ],
            "has_warnings": True,  # RCA-017 referenced superseded Rev 2
        },
        {
            "id": "H2",
            "title": "Bearing degradation",
            "supporting_evidence": ["OEM-Pump-Manual.txt"],
            "contradicting_evidence": [],
            "missing_evidence": [
                "Drive-end bearing temperature",
                "Demodulated vibration spectrum",
                "Grease sample condition",
            ],
            "has_warnings": False,
        },
        {
            "id": "H3",
            "title": "Mounting bolt looseness / soft foot",
            "supporting_evidence": ["OEM-Pump-Manual.txt"],
            "contradicting_evidence": [],
            "missing_evidence": [
                "Baseplate bolt torque inspection",
                "Soft foot measurement",
            ],
            "has_warnings": False,
        },
    ]

    comp_results = compare_hypotheses(raw_hypotheses)
    comparison_items = [HypothesisComparisonItem(**cr) for cr in comp_results]
    trace_events.append(TraceEvent(
        type="comparative_assessment_completed",
        message="Completed deterministic evidence strength evaluation across all candidate hypotheses",
    ))

    # 5. Updated Assessment
    updated_assessment = UpdatedAssessment(
        leading_hypothesis="Coupling misalignment",
        status="strong",
        assessment=(
            "Cannot be ruled out. Current evidence remains stronger for investigating coupling alignment first "
            "due to recent coupling replacement (WO-1842) and identical historical failure pattern (RCA-017). "
            "However, bearing degradation and mounting looseness cannot be excluded until physical measurements are taken."
        ),
        comparison=comparison_items,
        action_items=[
            "1. Measure coupling alignment using current MNT-014 Rev 4 standard (max offset: 0.08 mm).",
            "2. Collect vibration spectrum data to distinguish misalignment (2X peak) from bearing defect (high-frequency).",
            "3. If alignment passes 0.08 mm, inspect drive-end bearing temperature and grease lubrication.",
        ],
    )

    return ChallengeResponse(
        hypothesis_id=hypothesis_id,
        counter_evidence=counter_evidence_items,
        alternative_hypotheses=alternative_hypotheses,
        missing_information=missing_information,
        updated_assessment=updated_assessment,
        trace_events=trace_events,
    )

