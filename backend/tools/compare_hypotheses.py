"""
Tool: compare_hypotheses

Deterministically evaluates and compares hypotheses based on evidence counts,
categorizing strength into strong, moderate, weak, or insufficient.
NEVER outputs arbitrary confidence percentages.
"""

from typing import List, Dict, Any, Literal


def evaluate_strength(
    supporting_count: int,
    contradicting_count: int = 0,
    has_unresolved_warnings: bool = False,
) -> Literal["strong", "moderate", "weak", "insufficient"]:
    """
    Deterministic rules:
    - STRONG: >= 3 supporting items and 0 contradictions, without disabling warnings
    - MODERATE: >= 2 supporting items OR meaningful unresolved evidence/warnings
    - WEAK: exactly 1 supporting source
    - INSUFFICIENT: 0 supporting sources
    """
    if supporting_count == 0:
        return "insufficient"
    if contradicting_count > 0:
        if supporting_count >= 3:
            return "moderate"
        return "weak"
    if supporting_count >= 3:
        if has_unresolved_warnings:
            return "strong"  # Still strong evidence base with warnings noted
        return "strong"
    if supporting_count >= 2:
        return "moderate"
    if supporting_count == 1:
        return "weak"
    return "insufficient"


def compare_hypotheses(
    hypotheses: List[Dict[str, Any]],
    evidence: List[Dict[str, Any]] | None = None,
) -> List[Dict[str, Any]]:
    """
    Compare multiple candidate hypotheses deterministically.

    Returns a list of compared hypothesis summaries.
    """
    results: List[Dict[str, Any]] = []

    for h in hypotheses:
        h_id = h.get("id", "H")
        title = h.get("title", "")
        supporting = h.get("supporting_evidence", [])
        contradicting = h.get("contradicting_evidence", [])
        missing = h.get("missing_evidence", [])
        has_warnings = bool(h.get("has_warnings", False))

        supp_count = len(supporting)
        contra_count = len(contradicting)
        miss_count = len(missing)

        # Derive strength deterministically
        strength = evaluate_strength(
            supporting_count=supp_count,
            contradicting_count=contra_count,
            has_unresolved_warnings=has_warnings,
        )

        rationale_parts = []
        if supp_count > 0:
            rationale_parts.append(f"Supported by {supp_count} source(s) ({', '.join(supporting[:2])})")
        else:
            rationale_parts.append("No direct supporting engineering records")

        if contra_count > 0:
            rationale_parts.append(f"{contra_count} contradicting finding(s)")
        if miss_count > 0:
            rationale_parts.append(f"{miss_count} field measurement(s) required to confirm")

        results.append({
            "id": h_id,
            "title": title,
            "strength": strength,
            "supporting_count": supp_count,
            "contradicting_count": contra_count,
            "missing_count": miss_count,
            "rationale": ". ".join(rationale_parts) + ".",
        })

    return results

