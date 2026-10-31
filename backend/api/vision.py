"""
Vision & Multimodal API Endpoints.

Handles image upload, scene understanding with Muse Vision,
spatial grounding with SAM 3.1, component evidence linkage,
and evidence graph generation.
"""

import logging
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from PIL import Image

import sys
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from config import UPLOADS_DIR
from schemas import (
    VisionAnalysisResponse,
    TraceEvent,
    InvestigationGraph,
    ComponentHistory,
    SegmentationResult,
)
from services.muse_vision_service import analyze_equipment_scene
from services.sam_service import segment_component
from services.graph_service import build_evidence_graph
from tools.get_component_history import get_component_history

router = APIRouter()
log = logging.getLogger("veritas.vision_api")

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def _validate_and_save_image(file: UploadFile) -> tuple[Path, str]:
    """Validate file type and size, then save with a safe unique filename."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image format '{ext}'. Allowed formats: JPEG, PNG, WEBP.",
        )

    # Read content and enforce size limit
    content = file.file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Image size exceeds 10 MB limit ({len(content) / (1024*1024):.1f} MB).",
        )

    # Validate that it can be opened as an image
    safe_id = f"img_{uuid.uuid4().hex[:8]}"
    safe_filename = f"{safe_id}{ext}"
    dest_path = UPLOADS_DIR / safe_filename

    try:
        dest_path.write_bytes(content)
        with Image.open(dest_path) as img:
            img.verify()
    except Exception as e:
        if dest_path.exists():
            dest_path.unlink()
        raise HTTPException(status_code=400, detail=f"Invalid or corrupted image file: {e}")

    # Re-write since verify() can close file handles in PIL
    dest_path.write_bytes(content)

    image_url = f"/media/uploads/{safe_filename}"
    return dest_path, image_url


@router.post("/vision/analyze", response_model=VisionAnalysisResponse)
async def analyze_vision(
    image: UploadFile = File(...),
    problem: str = Form("High vibration after yesterday's coupling replacement."),
    investigation_id: Optional[str] = Form(None),
):
    """
    Multimodal scene analysis & grounding pipeline:
    1. Safely store uploaded image
    2. Muse Vision interprets scene & selects relevant component
    3. SAM 3.1 segments relevant component
    4. Retrieve component maintenance history
    5. Construct dynamically grounded evidence graph
    """
    log.info("Received image upload for vision analysis. Problem: %s", problem[:60])
    
    # 1. Save and validate image
    file_path, image_url = _validate_and_save_image(image)
    inv_id = investigation_id or f"inv_{uuid.uuid4().hex[:8]}"
    trace_events: list[TraceEvent] = []

    trace_events.append(TraceEvent(
        type="image_received",
        message="Equipment image uploaded and validated",
    ))

    # 2. Muse Vision Scene Analysis
    scene_analysis = analyze_equipment_scene(str(file_path), problem)
    equip_name = scene_analysis.equipment_type or "Centrifugal pump assembly"
    trace_events.append(TraceEvent(
        type="scene_analyzed",
        message=f"{equip_name.title()} identified",
    ))

    relevant_comp = scene_analysis.relevant_component or "flexible coupling"
    trace_events.append(TraceEvent(
        type="component_selected",
        message=f"{relevant_comp.title()} selected as relevant component based on problem context",
    ))

    # 3. SAM 3.1 Spatial Grounding
    sam_result = segment_component(str(file_path), relevant_comp)
    if sam_result.status == "completed":
        trace_events.append(TraceEvent(
            type="sam_segmentation",
            message=f"{relevant_comp.title()} visually grounded with SAM 3.1",
        ))
    elif sam_result.status == "not_found":
        trace_events.append(TraceEvent(
            type="sam_not_found",
            message=f"{relevant_comp.title()} could not be reliably localized in image",
        ))
    else:
        trace_events.append(TraceEvent(
            type="sam_failed",
            message="Component grounding unavailable; proceeding with evidence investigation",
        ))

    # Segment remaining visible components if available
    all_segmentations = [sam_result]
    for comp in scene_analysis.visible_components:
        if comp.name.lower() != relevant_comp.lower():
            extra_seg = segment_component(str(file_path), comp.name)
            all_segmentations.append(extra_seg)

    # 4. Component History
    import re
    asset_match = re.search(r"\b([A-Z]{1,6}-\d{1,6}[A-Z]?)\b", problem.upper())
    asset_id = asset_match.group(1) if asset_match else "P-101"
    history_data = get_component_history(asset_id, relevant_comp)
    comp_history = ComponentHistory(**history_data)
    num_records = len(comp_history.related_records)
    trace_events.append(TraceEvent(
        type="component_history",
        message=f"{num_records} related maintenance records found for {relevant_comp}",
    ))

    if any("RCA-017" in r.source for r in comp_history.related_records):
        trace_events.append(TraceEvent(
            type="historical_match",
            message="RCA-017 matched: previous vibration linked to coupling misalignment",
        ))
        trace_events.append(TraceEvent(
            type="revision_warning",
            message="Referenced MNT-014 Rev 2 is superseded by Rev 4 (0.15 mm → 0.08 mm)",
        ))

    # 5. Build Dynamic Evidence Graph
    graph = build_evidence_graph(
        asset_id=asset_id,
        component_name=relevant_comp.title(),
    )

    return VisionAnalysisResponse(
        investigation_id=inv_id,
        image_url=image_url,
        scene_analysis=scene_analysis,
        segmentation=sam_result,
        all_segmentations=all_segmentations,
        component_history=comp_history,
        graph=graph,
        trace_events=trace_events,
    )


@router.get("/investigations/{investigation_id}/graph", response_model=InvestigationGraph)
async def get_investigation_graph(
    investigation_id: str,
    component: Optional[str] = "Flexible Coupling",
):
    """Retrieve the dynamic evidence graph for an investigation."""
    from services.investigation_service import get_investigation
    inv = get_investigation(investigation_id)
    asset_id = (inv.incident.asset_id if inv and inv.incident and inv.incident.asset_id else "P-101")
    graph = build_evidence_graph(
        asset_id=asset_id,
        component_name=component or "Flexible Coupling",
    )
    return graph


@router.get("/components/{component_name}/segmentation", response_model=SegmentationResult)
async def get_component_segmentation(
    component_name: str,
    image_url: Optional[str] = None,
):
    """
    Get SAM 3.1 spatial grounding segmentation for a specific component.
    """
    from config import ASSETS_DIR, UPLOADS_DIR
    # Use uploaded image if specified, otherwise default pump image
    img_path = ASSETS_DIR / "pump_p101_assembly.jpg"
    if image_url:
        clean_name = Path(image_url).name
        candidate = UPLOADS_DIR / clean_name
        if candidate.is_file():
            img_path = candidate

    result = segment_component(str(img_path), component_name)
    return result


@router.get("/components/{component_name}/history", response_model=ComponentHistory)
async def get_component_history_endpoint(
    component_name: str,
    asset_id: str = "P-101",
):
    """
    Retrieve historical maintenance records linked to a specific physical component.
    """
    history_data = get_component_history(asset_id, component_name)
    return ComponentHistory(**history_data)

