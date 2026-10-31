"""
Service: evaluation_service

Runs the 20-case verification benchmark and returns structured results.
"""

import sys
from pathlib import Path

_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from evaluation.runner import run_all_cases
from schemas import EvaluationBenchmarkResult


def run_benchmark() -> EvaluationBenchmarkResult:
    """Execute the full Veritas evaluation benchmark suite."""
    return run_all_cases()

