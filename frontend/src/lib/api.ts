/**
 * Veritas Backend API Client
 */

export interface Incident {
  asset_id: string | null;
  equipment_type: string | null;
  symptom: string;
  context: string | null;
}

export interface EvidenceItem {
  id: string;
  source: string;
  document_type: string;
  content: string;
  relevance: string;
  asset_id?: string | null;
  revision?: number | null;
  status?: string | null;
}

export interface RevisionCheck {
  document_id: string;
  referenced_revision: number;
  current_revision: number;
  referenced_source: string | null;
  current_source: string | null;
  status: string;
}

export interface Conflict {
  type: string;
  title: string;
  description: string;
  sources: string[];
  severity: string;
}

export interface Hypothesis {
  id: string;
  title: string;
  status: "strong" | "moderate" | "weak" | "insufficient";
  supporting_evidence: string[];
  contradicting_evidence: string[];
  missing_evidence: string[];
  confirmed: boolean;
}

export interface Claim {
  id: string;
  text: string;
  type: string;
  supporting_sources: string[];
  applicability_status: string;
  revision_warning: string | null;
  status: "supported" | "partially_supported" | "unsupported";
}

export interface TraceEvent {
  type: string;
  message: string;
}

// ── Day 2 Multimodal Models ──────────────────────────────

export interface VisibleComponent {
  name: string;
  category?: string | null;
  relevance?: string | null;
}

export interface SceneAnalysis {
  equipment_type: string | null;
  likely_asset_type: string | null;
  visible_components: VisibleComponent[];
  relevant_component: string | null;
  relevance_reason: string | null;
  uncertainty: string[];
}

export interface BoundingBox {
  left: number;
  top: number;
  right: number;
  bottom: number;
}

export interface SegmentationResult {
  concept: string;
  object_id: string | null;
  box: BoundingBox | null;
  mask_url: string | null;
  mask_svg: string | null;
  width: number | null;
  height: number | null;
  status: "completed" | "not_found" | "failed" | string;
}

export interface ComponentHistoryRecord {
  source: string;
  type: string;
  summary: string;
}

export interface ComponentHistory {
  asset_id: string;
  component: string;
  related_records: ComponentHistoryRecord[];
}

export interface GraphNode {
  id: string;
  type: "asset" | "component" | "work_order" | "rca" | "procedure" | "manual" | "observation" | string;
  label: string;
  status?: string | null;
  metadata?: Record<string, any> | null;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: "HAS_COMPONENT" | "MAINTENANCE_ON" | "OBSERVED_AFTER" | "RELATED_TO" | "REFERENCES" | "SUPERSEDED_BY" | "APPLIES_TO" | string;
  label?: string | null;
}

export interface InvestigationGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface VisionAnalysisResponse {
  investigation_id?: string | null;
  image_url: string;
  scene_analysis: SceneAnalysis;
  segmentation: SegmentationResult;
  all_segmentations: SegmentationResult[];
  component_history?: ComponentHistory | null;
  graph: InvestigationGraph;
  trace_events: TraceEvent[];
}

// ── Day 3 Types: Challenge, Claim Passport & Benchmark ──

export interface ClaimSource {
  source: string;
  title?: string | null;
  snippet?: string | null;
  section?: string | null;
  relevance?: string | null;
  applicability?: string | null;
  revision_status?: string | null;
}

export interface ApplicabilityCheck {
  criterion: string;
  expected?: string | null;
  observed?: string | null;
  status: "match" | "warning" | "mismatch" | "unknown" | string;
  message?: string | null;
}

export interface RevisionContext {
  document_id: string;
  referenced_revision?: number | null;
  current_revision?: number | null;
  status: "CURRENT" | "SUPERSEDED" | string;
  warning?: string | null;
}

export interface ClaimPassport {
  claim_id: string;
  text: string;
  claim_type: string;
  supporting_sources: ClaimSource[];
  contradicting_sources: ClaimSource[];
  applicability_checks: ApplicabilityCheck[];
  revision_context: RevisionContext[];
  missing_information: string[];
  status: "supported" | "partially_supported" | "unsupported";
  confirmation_state: "confirmed" | "hypothesis" | "unknown";
}

export interface SourcePassport {
  source_id: string;
  document_type: string;
  asset?: string | null;
  incident_date?: string | null;
  equipment_family?: string | null;
  applicable_component?: string | null;
  referenced_procedures: string[];
  revision_status?: string | null;
  revision_warning?: string | null;
  current_replacement?: string | null;
  summary?: string | null;
}

export interface CounterEvidenceItem {
  source: string;
  text: string;
  type: string;
  section?: string | null;
  applicability_warning?: string | null;
}

export interface HypothesisComparisonItem {
  id: string;
  title: string;
  strength: "strong" | "moderate" | "weak" | "insufficient";
  supporting_count: number;
  contradicting_count: number;
  missing_count: number;
  rationale?: string | null;
}

export interface UpdatedAssessment {
  leading_hypothesis: string;
  status: string;
  assessment: string;
  comparison: HypothesisComparisonItem[];
  action_items: string[];
}

export interface ChallengeResponse {
  hypothesis_id: string;
  counter_evidence: CounterEvidenceItem[];
  alternative_hypotheses: Hypothesis[];
  missing_information: string[];
  updated_assessment: UpdatedAssessment;
  trace_events: TraceEvent[];
}

export interface BenchmarkMetric {
  correct: number;
  total: number;
  rate: number;
}

export interface BenchmarkCaseResult {
  case_id: string;
  name: string;
  passed: boolean;
  checks: Record<string, boolean>;
  details?: string | null;
}

export interface EvaluationBenchmarkResult {
  cases_tested: number;
  revision_detection: BenchmarkMetric;
  applicability: BenchmarkMetric;
  citation_grounding: BenchmarkMetric;
  conflict_detection: BenchmarkMetric;
  counter_evidence_discovery: BenchmarkMetric;
  unsupported_diagnoses_count: number;
  false_diagnosis_rate: number;
  cases: BenchmarkCaseResult[];
}

export interface InvestigationResult {
  incident: Incident;
  observations: EvidenceItem[];
  evidence: EvidenceItem[];
  relevant_evidence: EvidenceItem[];
  revision_checks: RevisionCheck[];
  conflicts: Conflict[];
  hypotheses: Hypothesis[];
  missing_information: string[];
  investigation_steps: string[];
  claims: Claim[];
  trace: TraceEvent[];
  ai_synthesis_status?: "active" | "unavailable" | string;
  graph?: InvestigationGraph;
  scene_analysis?: SceneAnalysis;
  segmentation?: SegmentationResult;
  image_url?: string;
}

export interface InvestigationResponse {
  investigation_id: string;
  status: string;
  result: InvestigationResult;
}

export const API_BASE_URL =
  (typeof process !== "undefined" && process.env?.["VITE_API_URL"]) ||
  (typeof import.meta !== "undefined" && import.meta.env?.["VITE_API_URL"]) ||
  "http://localhost:8000";

export async function checkHealth(): Promise<{ status: string; service: string }> {
  const res = await fetch(`${API_BASE_URL}/api/health`);
  if (!res.ok) {
    throw new Error(`Health check failed: ${res.statusText}`);
  }
  return res.json();
}

export async function createInvestigation(problem: string): Promise<InvestigationResponse> {
  const res = await fetch(`${API_BASE_URL}/api/investigations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ problem }),
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Investigation failed (${res.status}): ${errorText}`);
  }

  return res.json();
}

export async function getInvestigation(investigationId: string): Promise<InvestigationResponse> {
  const res = await fetch(`${API_BASE_URL}/api/investigations/${investigationId}`);
  if (!res.ok) {
    throw new Error(`Failed to retrieve investigation: ${res.statusText}`);
  }
  return res.json();
}

export async function analyzeVision(
  imageFile: File | Blob,
  problem: string,
  investigationId?: string
): Promise<VisionAnalysisResponse> {
  const formData = new FormData();
  formData.append("image", imageFile, "pump_assembly.jpg");
  formData.append("problem", problem);
  if (investigationId) {
    formData.append("investigation_id", investigationId);
  }

  const res = await fetch(`${API_BASE_URL}/api/vision/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Vision analysis failed (${res.status}): ${errorText}`);
  }

  return res.json();
}

export async function getInvestigationGraph(
  investigationId: string,
  component: string = "Flexible Coupling"
): Promise<InvestigationGraph> {
  const res = await fetch(
    `${API_BASE_URL}/api/investigations/${investigationId}/graph?component=${encodeURIComponent(component)}`
  );
  if (!res.ok) {
    throw new Error(`Failed to retrieve graph: ${res.statusText}`);
  }
  return res.json();
}

// ── Day 3 API Functions ──────────────────────────────────

export async function challengeRecommendation(
  investigationId: string,
  hypothesisId: string = "H1"
): Promise<ChallengeResponse> {
  const res = await fetch(`${API_BASE_URL}/api/investigations/${investigationId}/challenge`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ hypothesis_id: hypothesisId }),
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Challenge request failed (${res.status}): ${errorText}`);
  }
  return res.json();
}

export async function getClaimPassport(claimId: string): Promise<ClaimPassport> {
  const res = await fetch(`${API_BASE_URL}/api/claims/${claimId}`);
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch claim passport (${res.status}): ${errorText}`);
  }
  return res.json();
}

export async function getSourcePassport(sourceId: string): Promise<SourcePassport> {
  const res = await fetch(`${API_BASE_URL}/api/sources/${sourceId}`);
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch source passport (${res.status}): ${errorText}`);
  }
  return res.json();
}

export async function getBenchmarkResults(): Promise<EvaluationBenchmarkResult> {
  const res = await fetch(`${API_BASE_URL}/api/evaluation/benchmark`);
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch benchmark results (${res.status}): ${errorText}`);
  }
  return res.json();
}

export async function getComponentSegmentation(
  componentName: string,
  imageUrl?: string
): Promise<SegmentationResult> {
  const url = new URL(`${API_BASE_URL}/api/components/${encodeURIComponent(componentName)}/segmentation`);
  if (imageUrl) {
    url.searchParams.set("image_url", imageUrl);
  }
  const res = await fetch(url.toString());
  if (!res.ok) {
    throw new Error(`Failed to segment component (${res.status}): ${res.statusText}`);
  }
  return res.json();
}

export async function getComponentHistoryApi(
  componentName: string,
  assetId: string = "P-101"
): Promise<ComponentHistory> {
  const res = await fetch(
    `${API_BASE_URL}/api/components/${encodeURIComponent(componentName)}/history?asset_id=${encodeURIComponent(assetId)}`
  );
  if (!res.ok) {
    throw new Error(`Failed to fetch component history (${res.status}): ${res.statusText}`);
  }
  return res.json();
}
