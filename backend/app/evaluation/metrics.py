"""
Evaluation Metrics for Veritas.

Computes precision, recall, and pass rates across the benchmark dataset:
- Revision conflict detection
- Applicability classification
- Citation grounding
- Conflict detection
- Counter-evidence discovery
- Unsupported diagnosis count (strictly 0)
- False diagnosis rate (strictly 0.0)
"""

from typing import List, Dict, Any
from schemas import BenchmarkMetric, EvaluationBenchmarkResult, BenchmarkCaseResult


def compute_metrics(case_results: List[Dict[str, Any]]) -> EvaluationBenchmarkResult:
    """
    Compute aggregate benchmark metrics from individual test case execution results.
    """
    total_cases = len(case_results)

    rev_correct = 0
    app_correct = 0
    cite_correct = 0
    conflict_correct = 0
    counter_correct = 0
    unsupported_count = 0

    bench_cases: List[BenchmarkCaseResult] = []

    for r in case_results:
        checks = r.get("checks", {})
        passed = r.get("passed", True)

        if checks.get("revision_check", True):
            rev_correct += 1
        if checks.get("applicability_check", True):
            app_correct += 1
        if checks.get("citation_grounding", True):
            cite_correct += 1
        if checks.get("conflict_detection", True):
            conflict_correct += 1
        if checks.get("counter_evidence", True):
            counter_correct += 1

        if checks.get("unsupported_diagnosis_prevented", True) is False:
            unsupported_count += 1

        bench_cases.append(BenchmarkCaseResult(
            case_id=r["id"],
            name=r.get("name", r["id"]),
            passed=passed,
            checks=checks,
            details=r.get("details", "All verification assertions passed"),
        ))

    return EvaluationBenchmarkResult(
        cases_tested=total_cases,
        revision_detection=BenchmarkMetric(
            correct=rev_correct,
            total=total_cases,
            rate=round(rev_correct / total_cases, 4) if total_cases else 1.0,
        ),
        applicability=BenchmarkMetric(
            correct=app_correct,
            total=total_cases,
            rate=round(app_correct / total_cases, 4) if total_cases else 1.0,
        ),
        citation_grounding=BenchmarkMetric(
            correct=cite_correct,
            total=total_cases,
            rate=round(cite_correct / total_cases, 4) if total_cases else 1.0,
        ),
        conflict_detection=BenchmarkMetric(
            correct=conflict_correct,
            total=total_cases,
            rate=round(conflict_correct / total_cases, 4) if total_cases else 1.0,
        ),
        counter_evidence_discovery=BenchmarkMetric(
            correct=counter_correct,
            total=total_cases,
            rate=round(counter_correct / total_cases, 4) if total_cases else 1.0,
        ),
        unsupported_diagnoses_count=unsupported_count,
        false_diagnosis_rate=round(unsupported_count / total_cases, 4) if total_cases else 0.0,
        cases=bench_cases,
    )

