"""
Day 3 Test Suite — Veritas Engineering Verification

Tests for:
1. Challenge agent finds alternative evidence (bearing degradation)
2. Challenge agent does not simply repeat original recommendation
3. Claim Passport sources exist in real data files
4. No invented citations
5. Wrong equipment family (RCA-022.txt for CP-100) receives ANALOGOUS ONLY
6. Missing measurements remain missing
7. Unsupported hypothesis remains unconfirmed (confirmed: false)
8. Evaluation benchmark executes all 20 cases and returns real metrics
9. No fake confidence percentages
10. Hypothesis comparison deterministic rules
"""

import sys
from pathlib import Path

# Ensure backend modules are importable
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))


def test_challenge_finds_alternative_evidence():
    """Test 1: Challenge agent finds alternative evidence (bearing degradation)."""
    from services.challenge_service import run_challenge_review

    result = run_challenge_review("test_inv", "H1")

    # Must find counter-evidence
    assert len(result.counter_evidence) > 0, "Should find counter-evidence"

    # Must include bearing degradation as alternative mechanism
    sources = [ce.source for ce in result.counter_evidence]
    texts = [ce.text.lower() for ce in result.counter_evidence]
    assert any("bearing" in t for t in texts), \
        f"Should find bearing-related counter-evidence, got: {texts}"

    # Must include alternative hypotheses
    assert len(result.alternative_hypotheses) > 0, "Should generate alternative hypotheses"
    alt_titles = [h.title.lower() for h in result.alternative_hypotheses]
    assert any("bearing" in t for t in alt_titles), \
        f"Should include bearing degradation alternative, got: {alt_titles}"


def test_challenge_does_not_repeat_original():
    """Test 2: Challenge agent does not simply repeat original recommendation."""
    from services.challenge_service import run_challenge_review

    result = run_challenge_review("test_inv", "H1")

    # The challenge must NOT just confirm coupling misalignment as definitive
    assessment = result.updated_assessment.assessment.lower()
    assert "cannot be ruled out" in assessment or "cannot be excluded" in assessment, \
        "Challenge must acknowledge alternatives cannot be ruled out"

    # Must have alternative hypotheses different from H1
    alt_ids = [h.id for h in result.alternative_hypotheses]
    assert "H1" not in alt_ids, "Alternatives should not include the original hypothesis"
    assert len(alt_ids) > 0, "Must propose at least one alternative"


def test_claim_passport_sources_exist():
    """Test 3: Claim Passport sources exist in real data files."""
    from services.claim_service import get_claim_passport
    from config import DATA_DIR

    passport = get_claim_passport("CLM-001")
    assert passport is not None, "Should return a claim passport for CLM-001"

    # Every supporting source must exist on disk
    for src in passport.supporting_sources:
        src_path = DATA_DIR / src.source
        assert src_path.is_file(), \
            f"Supporting source '{src.source}' does not exist at {src_path}"


def test_no_invented_citations():
    """Test 4: No invented citations."""
    from tools.verify_claim import verify_claim

    # Verify a known-good claim
    result = verify_claim(
        "Coupling misalignment is a relevant investigation path.",
        ["RCA-017.txt", "WO-1842.txt"],
    )
    assert result["grounded"] is True, "Known sources should be grounded"
    assert len(result["invented_sources"]) == 0, "Should have no invented sources"

    # Verify a claim with an invented source
    result_bad = verify_claim(
        "Some invented claim.",
        ["FAKE-DOC-999.txt"],
    )
    assert result_bad["grounded"] is False, "Invented source should fail grounding"
    assert "FAKE-DOC-999.txt" in result_bad["invented_sources"]


def test_wrong_equipment_family_analogous_only():
    """Test 5: Wrong equipment family (RCA-022 CP-100) receives ANALOGOUS ONLY."""
    from services.applicability_service import verify_source_applicability

    result = verify_source_applicability("RCA-022.txt", target_asset_id="P-101")

    assert result.overall == "ANALOGOUS ONLY", \
        f"Expected 'ANALOGOUS ONLY', got '{result.overall}'"

    # Reason should mention equipment family
    assert "equipment family" in result.reason.lower() or "CP-100" in result.reason, \
        f"Reason should mention equipment family mismatch: {result.reason}"


def test_missing_measurements_remain_missing():
    """Test 6: Missing measurements remain missing."""
    from services.challenge_service import run_challenge_review

    result = run_challenge_review("test_inv", "H1")

    assert len(result.missing_information) > 0, "Must identify missing measurements"

    # Should include alignment measurement as missing
    missing_lower = [m.lower() for m in result.missing_information]
    assert any("alignment" in m for m in missing_lower), \
        f"Should list alignment measurement as missing, got: {missing_lower}"

    # Should include vibration spectrum
    assert any("vibration" in m or "spectrum" in m for m in missing_lower), \
        f"Should list vibration spectrum as missing, got: {missing_lower}"


def test_unsupported_hypothesis_unconfirmed():
    """Test 7: Unsupported hypothesis remains unconfirmed (confirmed: false)."""
    from services.challenge_service import run_challenge_review

    result = run_challenge_review("test_inv", "H1")

    for h in result.alternative_hypotheses:
        assert h.confirmed is False, \
            f"Hypothesis {h.id} ({h.title}) must not be confirmed without measurements"


def test_evaluation_benchmark_20_cases():
    """Test 8: Evaluation benchmark executes all 20 cases and returns real metrics."""
    from evaluation.runner import run_all_cases

    benchmark = run_all_cases()

    assert benchmark.cases_tested == 20, f"Expected 20 cases, got {benchmark.cases_tested}"
    assert len(benchmark.cases) == 20, f"Expected 20 case results, got {len(benchmark.cases)}"

    # Metrics must be present and real
    assert benchmark.revision_detection.total == 20
    assert benchmark.applicability.total == 20
    assert benchmark.citation_grounding.total == 20

    # Unsupported diagnoses must be zero
    assert benchmark.unsupported_diagnoses_count == 0, \
        f"Expected 0 unsupported diagnoses, got {benchmark.unsupported_diagnoses_count}"

    # False diagnosis rate must be zero
    assert benchmark.false_diagnosis_rate == 0.0, \
        f"Expected 0.0 false diagnosis rate, got {benchmark.false_diagnosis_rate}"


def test_no_fake_confidence_percentages():
    """Test 9: No fake confidence percentages (like 92%, 68%)."""
    from services.challenge_service import run_challenge_review

    result = run_challenge_review("test_inv", "H1")

    # Check updated_assessment text
    assessment_text = result.updated_assessment.assessment

    import re
    # Pattern for suspicious percentage values
    pct_pattern = re.compile(r'\d{1,3}(\.\d+)?%')
    matches = pct_pattern.findall(assessment_text)
    assert len(matches) == 0, \
        f"Assessment should not contain arbitrary percentages, found: {pct_pattern.findall(assessment_text)}"

    # Evidence strength must use deterministic categories only
    valid_strengths = {"strong", "moderate", "weak", "insufficient"}
    for comp in result.updated_assessment.comparison:
        assert comp.strength in valid_strengths, \
            f"Strength '{comp.strength}' is not a valid deterministic category"


def test_hypothesis_comparison_deterministic():
    """Test 10: Hypothesis comparison uses deterministic evidence-counting rules."""
    from tools.compare_hypotheses import compare_hypotheses, evaluate_strength

    # Rule: >= 3 supporting, 0 contradicting => strong
    assert evaluate_strength(3, 0) == "strong"

    # Rule: >= 2 supporting => moderate
    assert evaluate_strength(2, 0) == "moderate"

    # Rule: 1 supporting => weak
    assert evaluate_strength(1, 0) == "weak"

    # Rule: 0 supporting => insufficient
    assert evaluate_strength(0, 0) == "insufficient"

    # Rule: >= 3 supporting with contradiction => moderate (not strong)
    assert evaluate_strength(3, 1) == "moderate"

    # Compare multiple hypotheses
    result = compare_hypotheses([
        {
            "id": "H1",
            "title": "Coupling misalignment",
            "supporting_evidence": ["RCA-017.txt", "WO-1842.txt", "OEM-Pump-Manual.txt"],
            "contradicting_evidence": [],
            "missing_evidence": ["alignment measurement"],
        },
        {
            "id": "H2",
            "title": "Bearing degradation",
            "supporting_evidence": ["OEM-Pump-Manual.txt"],
            "contradicting_evidence": [],
            "missing_evidence": ["bearing temp", "spectrum", "grease"],
        },
    ])

    assert len(result) == 2
    assert result[0]["strength"] == "strong"
    assert result[1]["strength"] == "weak"
    assert result[0]["supporting_count"] == 3
    assert result[1]["supporting_count"] == 1

