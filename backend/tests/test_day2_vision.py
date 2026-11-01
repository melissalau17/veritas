"""
Day 2 Multimodal Verification Tests.

Test A — Relevant component selection
Test B — No visual diagnosis from image alone
Test C — SAM segmentation response
Test D — Empty SAM result handling
Test E — Graph provenance & edge integrity
Test F — End-to-end vision analysis API
"""

import asyncio
import sys
from pathlib import Path

_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from fastapi.testclient import TestClient
from main import app
from services.muse_vision_service import analyze_equipment_scene
from services.sam_service import segment_component
from services.graph_service import build_evidence_graph
from tools.get_component_history import get_component_history
from tools.compare_revisions import compare_revisions

client = TestClient(app)
DEMO_IMAGE_PATH = str(Path(__file__).resolve().parent.parent / "assets" / "pump_p101_assembly.jpg")


# ──────────────────────────────────────────────────────────
# Test A — Relevant component selection
# ──────────────────────────────────────────────────────────

def test_relevant_component_selection():
    """
    Given the problem 'High vibration after yesterday's coupling replacement',
    the scene analysis must select 'flexible coupling' as the relevant component.
    """
    scene = asyncio.run(analyze_equipment_scene(
        image_path=DEMO_IMAGE_PATH,
        problem="High vibration after yesterday's coupling replacement.",
    ))

    assert scene.relevant_component is not None, "relevant_component should not be None"
    assert "coupling" in scene.relevant_component.lower(), (
        f"Expected coupling to be selected, got: {scene.relevant_component}"
    )

    # Must list multiple visible components
    comp_names = [c.name.lower() for c in scene.visible_components]
    assert any("motor" in c for c in comp_names), "Should identify motor"
    assert any("coupling" in c for c in comp_names), "Should identify coupling"
    assert any("pump" in c for c in comp_names), "Should identify pump"


# ──────────────────────────────────────────────────────────
# Test B — No visual diagnosis from photo alone
# ──────────────────────────────────────────────────────────

def test_no_visual_diagnosis():
    """
    The vision system must NOT declare the coupling is misaligned
    from the photo alone without measurements.
    """
    scene = asyncio.run(analyze_equipment_scene(
        image_path=DEMO_IMAGE_PATH,
        problem="High vibration after yesterday's coupling replacement.",
    ))

    reason_lower = (scene.relevance_reason or "").lower()
    assert "coupling is misaligned" not in reason_lower, (
        f"Falsely diagnosed misalignment from visual alone: {scene.relevance_reason}"
    )

    # Must articulate uncertainty
    assert len(scene.uncertainty) > 0, "Visual analysis must state uncertainties"


# ──────────────────────────────────────────────────────────
# Test C — SAM segmentation response
# ──────────────────────────────────────────────────────────

def test_sam_segmentation_response():
    """
    SAM segmentation of 'flexible coupling' must return status='completed',
    a valid bounding box, and an SVG mask.
    """
    seg = asyncio.run(segment_component(
        image_path=DEMO_IMAGE_PATH,
        concept="flexible coupling",
    ))

    assert seg.status == "completed", f"Expected completed status, got: {seg.status}"
    assert seg.box is not None, "Bounding box must be present"
    assert seg.box.left < seg.box.right, "Invalid box horizontal bounds"
    assert seg.box.top < seg.box.bottom, "Invalid box vertical bounds"
    assert seg.mask_url is not None or seg.mask_svg is not None, "Mask must be returned"


# ──────────────────────────────────────────────────────────
# Test D — Empty SAM result handling
# ──────────────────────────────────────────────────────────

def test_sam_empty_result_handling():
    """
    When given an unrecognized or non-existent concept, SAM must return
    status='not_found' with null box/mask without crashing.
    """
    seg = asyncio.run(segment_component(
        image_path=DEMO_IMAGE_PATH,
        concept="turbocharger intercooler",
    ))

    assert seg.status == "not_found", f"Expected status='not_found', got {seg.status}"
    assert seg.box is None, "Box should be None for not_found"
    assert seg.mask_url is None, "mask_url should be None for not_found"


# ──────────────────────────────────────────────────────────
# Test E — Graph provenance & edge integrity
# ──────────────────────────────────────────────────────────

def test_graph_provenance():
    """
    Every edge in the generated evidence graph must match real documents:
    - P-101 HAS_COMPONENT Flexible Coupling
    - Flexible Coupling RELATED_TO RCA-017
    - RCA-017 REFERENCES MNT-014 Rev 2
    - MNT-014 Rev 2 SUPERSEDED_BY MNT-014 Rev 4
    """
    graph = build_evidence_graph(
        asset_id="P-101",
        component_name="Flexible Coupling",
    )

    # Check key nodes
    node_ids = {n.id for n in graph.nodes}
    assert "asset:P-101" in node_ids, "Asset node missing"
    assert "component:flexible_coupling" in node_ids, "Component node missing"
    assert "doc:WO-1842" in node_ids, "WO-1842 node missing"
    assert "doc:RCA-017" in node_ids, "RCA-017 node missing"
    assert "doc:MNT-014-Rev2" in node_ids, "MNT-014 Rev 2 node missing"
    assert "doc:MNT-014-Rev4" in node_ids, "MNT-014 Rev 4 node missing"

    # Check key edges
    edge_pairs = {(e.source, e.target, e.type) for e in graph.edges}

    assert (
        "asset:P-101",
        "component:flexible_coupling",
        "HAS_COMPONENT",
    ) in edge_pairs, "Missing HAS_COMPONENT edge"

    assert (
        "doc:RCA-017",
        "doc:MNT-014-Rev2",
        "REFERENCES",
    ) in edge_pairs, "Missing RCA-017 REFERENCES MNT-014-Rev2 edge"

    assert (
        "doc:MNT-014-Rev2",
        "doc:MNT-014-Rev4",
        "SUPERSEDED_BY",
    ) in edge_pairs, "Missing SUPERSEDED_BY edge"


# ──────────────────────────────────────────────────────────
# Test F — End-to-end vision analysis API
# ──────────────────────────────────────────────────────────

def test_vision_analyze_endpoint():
    """
    POST /api/vision/analyze with multipart image and problem statement
    must return 200 with scene analysis, segmentation, graph, and trace.
    """
    with open(DEMO_IMAGE_PATH, "rb") as f:
        response = client.post(
            "/api/vision/analyze",
            files={"image": ("pump.jpg", f, "image/jpeg")},
            data={"problem": "High vibration after yesterday's coupling replacement."},
        )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()

    assert "scene_analysis" in data
    assert "segmentation" in data
    assert "graph" in data
    assert "trace_events" in data

    # Check that trace has visual events
    trace_types = {t["type"] for t in data["trace_events"]}
    assert "image_received" in trace_types
    assert "scene_analyzed" in trace_types
    assert "component_selected" in trace_types

    # Check graph endpoint
    graph_res = client.get(f"/api/investigations/{data.get('investigation_id', 'inv_001')}/graph")
    assert graph_res.status_code == 200
    assert len(graph_res.json()["nodes"]) > 0


def test_vision_analyze_rejects_unsupported_content_type():
    response = client.post(
        "/api/vision/analyze",
        files={"image": ("image.gif", b"not an image", "image/gif")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported image type"


# ──────────────────────────────────────────────────────────
# Test G — Revision Diff
# ──────────────────────────────────────────────────────────

def test_revision_diff():
    """Compare MNT-014 Rev 2 vs Rev 4 must show 0.15 mm -> 0.08 mm."""
    diff = compare_revisions("MNT-014", 2, 4)
    assert diff["document_id"] == "MNT-014"
    assert len(diff["changes"]) > 0

    offset_changes = [c for c in diff["changes"] if "offset" in c["field"].lower()]
    assert len(offset_changes) > 0
    c = offset_changes[0]
    assert "0.15" in c["old"]
    assert "0.08" in c["new"]
