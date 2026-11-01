"""
Muse (LLM) integration service.

Calls the existing meta_client to generate structured JSON
investigation synthesis, with retry on validation failure.
"""

import json
import logging

import sys
from pathlib import Path
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from src.meta_client import ask_muse, model_is_configured, get_model_name
from src.ingest import build_context

log = logging.getLogger("veritas.muse")

STRUCTURED_SYSTEM_ADDENDUM = """

IMPORTANT OUTPUT FORMAT:

You MUST respond with ONLY a JSON object matching this schema:

{
  "hypotheses": [
    {
      "id": "H1",
      "title": "string",
      "status": "strong" | "moderate" | "weak" | "insufficient",
      "supporting_evidence": ["source1.txt"],
      "contradicting_evidence": [],
      "missing_evidence": ["what is missing"],
      "confirmed": false
    }
  ],
  "missing_information": ["string"],
  "investigation_steps": ["string"],
  "claims": [
    {
      "id": "CLM-001",
      "text": "string",
      "type": "investigation_hypothesis",
      "supporting_sources": ["source.txt"],
      "applicability_status": "string",
      "revision_warning": "string or null",
      "status": "supported" | "partially_supported" | "unsupported"
    }
  ]
}

Do NOT include markdown, explanation, or any text outside the JSON.
Do NOT claim a confirmed diagnosis unless the evidence proves it.
"""


def build_structured_prompt(
    problem: str,
    evidence: list[dict],
    conflicts: list[dict],
    revision_diffs: list[dict],
) -> str:
    """Build a prompt that requests structured JSON from Muse."""

    evidence_context = build_context(evidence)

    conflict_lines = []
    for c in conflicts:
        conflict_lines.append(
            f"- {c['source']} references {c['document_id']} Rev {c['referenced_revision']}, "
            f"but current is Rev {c['current_revision']}. "
            f"Old tolerance: {c.get('old_tolerance', 'N/A')}, "
            f"Current tolerance: {c.get('current_tolerance', 'N/A')}"
        )

    diff_lines = []
    for d in revision_diffs:
        for change in d.get("changes", []):
            diff_lines.append(
                f"- {d['document_id']}: {change['field']}: {change['old']} → {change['new']}"
            )

    return f"""ENGINEERING PROBLEM
===================
{problem}

RETRIEVED ENGINEERING EVIDENCE
==============================
{evidence_context}

DETERMINISTIC VERIFICATION RESULTS
===================================
Revision conflicts:
{chr(10).join(conflict_lines) if conflict_lines else "None detected."}

Technical changes between revisions:
{chr(10).join(diff_lines) if diff_lines else "None detected."}

{STRUCTURED_SYSTEM_ADDENDUM}
"""


async def call_muse(
    problem: str,
    evidence: list[dict],
    conflicts: list[dict],
    revision_diffs: list[dict],
    max_retries: int = 1,
) -> dict:
    """
    Call Muse for structured synthesis.

    Returns a dict with keys: hypotheses, missing_information,
    investigation_steps, claims.

    If the model is not configured or fails, returns an empty dict
    so the system can fall back to deterministic-only output.
    """
    if not model_is_configured():
        log.warning("Model not configured — skipping Muse synthesis")
        return {}

    prompt = build_structured_prompt(problem, evidence, conflicts, revision_diffs)

    for attempt in range(1 + max_retries):
        try:
            log.info("Calling Muse (attempt %d), model=%s", attempt + 1, get_model_name())
            raw = await ask_muse(prompt, temperature=0.1)

            # Strip markdown code fences if model wraps output
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                # Remove opening fence
                first_newline = cleaned.index("\n")
                cleaned = cleaned[first_newline + 1:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            parsed = json.loads(cleaned)
            log.info("Muse returned valid JSON")
            return parsed

        except json.JSONDecodeError as e:
            log.warning("Muse returned invalid JSON (attempt %d): %s", attempt + 1, e)
            if attempt < max_retries:
                # Retry with error context
                prompt += f"\n\nYour previous response was not valid JSON. Error: {e}\nPlease respond with ONLY valid JSON."
            continue

        except Exception as e:
            log.exception("Muse call failed")
            return {}

    log.warning("Muse failed to return valid JSON after retries")
    return {}
