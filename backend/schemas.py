"""
Pydantic models for Veritas investigation results.

These define the structured JSON contract between
the backend and the frontend.
"""

from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


# ── Incident ──────────────────────────────────────────────

class Incident(BaseModel):
    asset_id: Optional[str] = None
    equipment_type: Optional[str] = None
    symptom: str = ""
    context: Optional[str] = None


# ── Evidence ──────────────────────────────────────────────

class EvidenceItem(BaseModel):
    id: str
    source: str
    document_type: str = "evidence"
    content: str = ""
    relevance: str = "high"
    asset_id: Optional[str] = None
    revision: Optional[int] = None
    status: Optional[str] = None


# ── Revision Checks ──────────────────────────────────────

class RevisionCheck(BaseModel):
    document_id: str
    referenced_revision: int
    current_revision: int
    referenced_source: Optional[str] = None
    current_source: Optional[str] = None
    status: str  # "current" | "superseded"


# ── Conflicts ─────────────────────────────────────────────

class Conflict(BaseModel):
    type: str
    title: str
    description: str
    sources: List[str]
    severity: str  # "warning" | "critical" | "info"


# ── Hypotheses ────────────────────────────────────────────

class Hypothesis(BaseModel):
    id: str
    title: str

    status: Literal["strong", "moderate", "weak", "insufficient"]

    supporting_evidence: List[str] = Field(default_factory=list)
    contradicting_evidence: List[str] = Field(default_factory=list)
    missing_evidence: List[str] = Field(default_factory=list)

    confirmed: bool = False


# ── Claims ────────────────────────────────────────────────

class Claim(BaseModel):
    id: str
    text: str
    type: str

    supporting_sources: List[str] = Field(default_factory=list)

    applicability_status: str = ""

    revision_warning: Optional[str] = None

    status: Literal["supported", "partially_supported", "unsupported"] = "supported"


# ── Trace Events ─────────────────────────────────────────

class TraceEvent(BaseModel):
    type: str
    message: str


# ── Vision & Scene Analysis (Day 2) ──────────────────────

class VisibleComponent(BaseModel):
    name: str
    category: Optional[str] = None
    relevance: Optional[str] = None


class SceneAnalysis(BaseModel):
    equipment_type: Optional[str] = None
    likely_asset_type: Optional[str] = None
    visible_components: List[VisibleComponent] = Field(default_factory=list)
    relevant_component: Optional[str] = None
    relevance_reason: Optional[str] = None
    uncertainty: List[str] = Field(default_factory=list)


class BoundingBox(BaseModel):
    left: float
    top: float
    right: float
    bottom: float


class SegmentationResult(BaseModel):
    concept: str
    object_id: Optional[str] = None
    box: Optional[BoundingBox] = None
    mask_url: Optional[str] = None
    mask_svg: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    status: str  # "completed" | "not_found" | "failed"


class ComponentHistoryRecord(BaseModel):
    source: str
    type: str
    summary: str


class ComponentHistory(BaseModel):
    asset_id: str
    component: str
    related_records: List[ComponentHistoryRecord] = Field(default_factory=list)


# ── Evidence Graph (Day 2) ────────────────────────────────

class GraphNode(BaseModel):
    id: str
    type: str  # "asset" | "component" | "work_order" | "rca" | "procedure" | "manual" | "observation"
    label: str
    status: Optional[str] = None
    metadata: Optional[dict] = None


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str  # "HAS_COMPONENT" | "MAINTENANCE_ON" | "OBSERVED_AFTER" | "RELATED_TO" | "REFERENCES" | "SUPERSEDED_BY" | "APPLIES_TO"
    label: Optional[str] = None


class InvestigationGraph(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)


# ── Revision Diff (Day 2) ─────────────────────────────────

class RevisionDiffChange(BaseModel):
    field: str
    old: str
    new: str
    change_type: str = "modified"


class RevisionDiff(BaseModel):
    document_id: str
    old_revision: int
    new_revision: int
    changes: List[RevisionDiffChange] = Field(default_factory=list)


# ── Investigation Result (top-level response) ────────────

class InvestigationResult(BaseModel):
    incident: Incident
    observations: List[EvidenceItem] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    relevant_evidence: List[EvidenceItem] = Field(default_factory=list)
    revision_checks: List[RevisionCheck] = Field(default_factory=list)
    conflicts: List[Conflict] = Field(default_factory=list)
    hypotheses: List[Hypothesis] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    investigation_steps: List[str] = Field(default_factory=list)
    claims: List[Claim] = Field(default_factory=list)
    trace: List[TraceEvent] = Field(default_factory=list)
    ai_synthesis_status: str = "active"
    graph: Optional[InvestigationGraph] = None
    scene_analysis: Optional[SceneAnalysis] = None
    segmentation: Optional[SegmentationResult] = None
    image_url: Optional[str] = None


# ── Vision Analysis Response (Day 2 API) ──────────────────

class VisionAnalysisResponse(BaseModel):
    investigation_id: Optional[str] = None
    image_url: str
    scene_analysis: SceneAnalysis
    segmentation: SegmentationResult
    all_segmentations: List[SegmentationResult] = Field(default_factory=list)
    component_history: Optional[ComponentHistory] = None
    graph: InvestigationGraph
    trace_events: List[TraceEvent] = Field(default_factory=list)


# ── Day 3: Claim Passport & Applicability ────────────────

class ClaimSource(BaseModel):
    source: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    section: Optional[str] = None
    relevance: Optional[str] = "high"
    applicability: Optional[str] = None
    revision_status: Optional[str] = None


class ApplicabilityCheck(BaseModel):
    criterion: str
    expected: Optional[str] = None
    observed: Optional[str] = None
    status: str = "match"  # "match" | "warning" | "mismatch" | "unknown"
    message: Optional[str] = None


class SourceApplicability(BaseModel):
    source: str
    overall: str  # "APPLICABLE" | "APPLICABLE WITH WARNING" | "ANALOGOUS ONLY" | "NOT APPLICABLE" | "INSUFFICIENT INFORMATION"
    checks: List[ApplicabilityCheck] = Field(default_factory=list)
    reason: Optional[str] = None


class RevisionContext(BaseModel):
    document_id: str
    referenced_revision: Optional[int] = None
    current_revision: Optional[int] = None
    status: str = "CURRENT"  # "CURRENT" | "SUPERSEDED"
    warning: Optional[str] = None


class ClaimPassport(BaseModel):
    claim_id: str
    text: str
    claim_type: str
    supporting_sources: List[ClaimSource] = Field(default_factory=list)
    contradicting_sources: List[ClaimSource] = Field(default_factory=list)
    applicability_checks: List[ApplicabilityCheck] = Field(default_factory=list)
    revision_context: List[RevisionContext] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    status: Literal["supported", "partially_supported", "unsupported"] = "supported"
    confirmation_state: Literal["confirmed", "hypothesis", "unknown"] = "hypothesis"


class SourcePassport(BaseModel):
    source_id: str
    document_type: str
    asset: Optional[str] = None
    incident_date: Optional[str] = None
    equipment_family: Optional[str] = None
    applicable_component: Optional[str] = None
    referenced_procedures: List[str] = Field(default_factory=list)
    revision_status: Optional[str] = None
    revision_warning: Optional[str] = None
    current_replacement: Optional[str] = None
    summary: Optional[str] = None


# ── Day 3: Challenge Recommendation ──────────────────────

class CounterEvidenceItem(BaseModel):
    source: str
    text: str
    type: str = "alternative_mechanism"  # "alternative_mechanism" | "contradiction" | "weakening_evidence"
    section: Optional[str] = None
    applicability_warning: Optional[str] = None


class HypothesisComparisonItem(BaseModel):
    id: str
    title: str
    strength: Literal["strong", "moderate", "weak", "insufficient"]
    supporting_count: int = 0
    contradicting_count: int = 0
    missing_count: int = 0
    rationale: Optional[str] = None


class UpdatedAssessment(BaseModel):
    leading_hypothesis: str
    status: str
    assessment: str
    comparison: List[HypothesisComparisonItem] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)


class ChallengeRequest(BaseModel):
    hypothesis_id: str = "H1"


class ChallengeResponse(BaseModel):
    hypothesis_id: str
    counter_evidence: List[CounterEvidenceItem] = Field(default_factory=list)
    alternative_hypotheses: List[Hypothesis] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    updated_assessment: UpdatedAssessment
    trace_events: List[TraceEvent] = Field(default_factory=list)


# ── Day 3: Evaluation Benchmark ──────────────────────────

class BenchmarkMetric(BaseModel):
    correct: int
    total: int
    rate: float


class BenchmarkCaseResult(BaseModel):
    case_id: str
    name: str
    passed: bool
    checks: dict = Field(default_factory=dict)
    details: Optional[str] = None


class EvaluationBenchmarkResult(BaseModel):
    cases_tested: int
    revision_detection: BenchmarkMetric
    applicability: BenchmarkMetric
    citation_grounding: BenchmarkMetric
    conflict_detection: BenchmarkMetric
    counter_evidence_discovery: BenchmarkMetric
    unsupported_diagnoses_count: int = 0
    false_diagnosis_rate: float = 0.0
    cases: List[BenchmarkCaseResult] = Field(default_factory=list)


# ── API Request / Response wrappers ──────────────────────

class InvestigationRequest(BaseModel):
    problem: str


class InvestigationResponse(BaseModel):
    investigation_id: str
    status: str = "completed"
    result: InvestigationResult
