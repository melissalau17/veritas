"""
Muse Vision Service.

Analyzes equipment images in the context of an industrial maintenance incident.
Produces structured scene analysis: equipment type, visible components,
the relevant component to investigate, and preserves visual uncertainty.
"""

import base64
import json
import logging
import re
from pathlib import Path
from typing import Optional

import sys
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from config import settings
from schemas import SceneAnalysis, VisibleComponent
from src.meta_client import model_is_configured, get_model_name

log = logging.getLogger("veritas.vision")

MUSE_VISION_SYSTEM_PROMPT = """You are Veritas's visual engineering context agent.

Analyze industrial equipment images to identify visible equipment and components.

You do NOT diagnose defects from appearance unless the defect is directly visible and unambiguous.

Given:
- an equipment image
- an incident description

Return ONLY a JSON object matching this schema:
{
  "equipment_type": "centrifugal pump assembly",
  "likely_asset_type": "rotating equipment",
  "visible_components": [
    {
      "name": "electric motor",
      "category": "driver",
      "relevance": "secondary"
    },
    {
      "name": "flexible coupling",
      "category": "power transmission",
      "relevance": "high"
    },
    {
      "name": "centrifugal pump",
      "category": "pump",
      "relevance": "high"
    },
    {
      "name": "bearing housing",
      "category": "bearing assembly",
      "relevance": "moderate"
    }
  ],
  "relevant_component": "flexible coupling",
  "relevance_reason": "The reported abnormal vibration began after coupling replacement.",
  "uncertainty": [
    "Exact internal condition cannot be confirmed visually.",
    "Internal alignment status requires precision measurement."
  ]
}

SAFETY RULES:
- Never claim "The coupling is misaligned" from the photo alone.
- Never invent asset tags, measurements, failure states, or maintenance history.
- Distinguish visual scene understanding from physical defect confirmation.
- Output ONLY raw valid JSON, no markdown formatting or explanation.
"""


def _encode_image_to_base64(image_path: str) -> str:
    """Read image file and return base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def _get_fallback_scene_analysis(problem: str) -> SceneAnalysis:
    """
    Deterministic fallback scene analysis for industrial equipment.
    Adapts based on problem statement keywords (pumps, exchangers, fans, etc.).
    """
    prob_lower = problem.lower()

    if any(k in prob_lower for k in ("exchanger", "heater", "tube", "bundle", "ea-5601")):
        return SceneAnalysis(
            equipment_type="shell and tube heat exchanger",
            likely_asset_type="static heat transfer equipment",
            visible_components=[
                VisibleComponent(name="tube bundle", category="heat transfer core", relevance="high"),
                VisibleComponent(name="shell cover", category="pressure boundary", relevance="moderate"),
                VisibleComponent(name="channel head", category="flow distribution", relevance="secondary"),
                VisibleComponent(name="floating head", category="expansion joint", relevance="moderate"),
            ],
            relevant_component="tube bundle",
            relevance_reason="Reported thermal duty shortfall and differential pressure deviation indicate tube-side fouling or restriction.",
            uncertainty=[
                "Internal tube-bore deposit thickness cannot be measured from exterior visual inspection.",
                "Impulse-line sensing integrity requires differential pressure transmitter verification.",
            ],
        )
    elif any(k in prob_lower for k in ("fan", "cooling tower", "ct-7801")):
        return SceneAnalysis(
            equipment_type="cooling tower cell fan",
            likely_asset_type="rotating mechanical equipment",
            visible_components=[
                VisibleComponent(name="fan blades", category="aerodynamic", relevance="high"),
                VisibleComponent(name="drive coupling", category="power transmission", relevance="high"),
                VisibleComponent(name="fan gearbox", category="speed reducer", relevance="moderate"),
                VisibleComponent(name="electric motor", category="driver", relevance="secondary"),
            ],
            relevant_component="drive coupling",
            relevance_reason="Vibration following drive-train service requires verifying shaft coupling condition and blade balance.",
            uncertainty=[
                "Blade aerodynamic balance cannot be verified from stationary images.",
                "Gearbox internal backlash requires precision dial measurement.",
            ],
        )
    elif any(k in prob_lower for k in ("compressor", "kc-4501")):
        return SceneAnalysis(
            equipment_type="recycle gas centrifugal compressor",
            likely_asset_type="critical rotating equipment",
            visible_components=[
                VisibleComponent(name="compressor casing", category="pressure containment", relevance="moderate"),
                VisibleComponent(name="dry gas seal", category="shaft sealing", relevance="high"),
                VisibleComponent(name="lube console", category="auxiliary system", relevance="high"),
                VisibleComponent(name="radial bearings", category="rotor support", relevance="moderate"),
            ],
            relevant_component="dry gas seal",
            relevance_reason="Seal leakage and lube pressure anomalies require verifying seal gas differential pressure.",
            uncertainty=[
                "Dynamic seal face condition requires seal gas leakage trend data.",
            ],
        )
    elif any(k in prob_lower for k in ("reactor", "dc-3401")):
        return SceneAnalysis(
            equipment_type="catalyst reduction reactor",
            likely_asset_type="fixed bed catalytic reactor",
            visible_components=[
                VisibleComponent(name="reactor vessel", category="pressure containment", relevance="secondary"),
                VisibleComponent(name="catalyst bed", category="reaction zone", relevance="high"),
                VisibleComponent(name="thermocouple bridle", category="temperature instrumentation", relevance="high"),
                VisibleComponent(name="inlet distributor", category="flow distribution", relevance="moderate"),
            ],
            relevant_component="thermocouple bridle",
            relevance_reason="Bed temperature anomalies require checking sensor loop integrity vs actual reaction bed runaway.",
            uncertainty=[
                "Internal catalyst activity and fines fouling cannot be observed without internal inspection.",
            ],
        )

    # Standard rotating equipment / pump fallback
    if "coupling" in prob_lower:
        relevant = "flexible coupling"
        reason = "The reported incident occurred after coupling replacement, making the coupling the primary focal component."
    elif "bearing" in prob_lower:
        relevant = "bearing housing"
        reason = "Reported symptoms are localized to the bearing housing area."
    elif "motor" in prob_lower:
        relevant = "electric motor"
        reason = "Reported symptoms relate to the driver motor."
    else:
        relevant = "flexible coupling"
        reason = "Rotating power transmission interface is the standard focal point for post-maintenance vibration."

    return SceneAnalysis(
        equipment_type="centrifugal pump assembly",
        likely_asset_type="rotating equipment",
        visible_components=[
            VisibleComponent(name="electric motor", category="driver", relevance="secondary"),
            VisibleComponent(name="flexible coupling", category="power transmission", relevance="high"),
            VisibleComponent(name="centrifugal pump", category="pump", relevance="high"),
            VisibleComponent(name="bearing housing", category="bearing assembly", relevance="moderate"),
        ],
        relevant_component=relevant,
        relevance_reason=reason,
        uncertainty=[
            "Exact internal condition cannot be confirmed visually from photo.",
            "Alignment tolerance compliance requires dial indicator or laser measurement.",
        ],
    )


def analyze_equipment_scene(
    image_path: str,
    problem: str,
) -> SceneAnalysis:
    """
    Analyze an equipment image and problem description with Muse Vision.
    Falls back gracefully to deterministic analysis if LLM is unavailable.
    """
    if not model_is_configured():
        log.info("Model API key not configured; using deterministic scene analysis")
        return _get_fallback_scene_analysis(problem)

    try:
        from src.meta_client import get_client
        client = get_client()
        model = get_model_name()

        # Check if file exists
        img_p = Path(image_path)
        if not img_p.is_file():
            log.warning("Image file %s not found, returning fallback scene analysis", image_path)
            return _get_fallback_scene_analysis(problem)

        b64_image = _encode_image_to_base64(image_path)
        mime_type = "image/jpeg"
        if img_p.suffix.lower() == ".png":
            mime_type = "image/png"
        elif img_p.suffix.lower() == ".webp":
            mime_type = "image/webp"

        user_content = [
            {
                "type": "text",
                "text": f"Industrial Maintenance Incident:\n{problem}\n\nPlease identify the equipment and the relevant physical component.",
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{b64_image}",
                },
            },
        ]

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": MUSE_VISION_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.1,
            max_tokens=2048,
        )

        content = response.choices[0].message.content.strip()
        if "```" in content:
            m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
            if m:
                content = m.group(1).strip()
        json_match = re.search(r"(\{[\s\S]*\})", content)
        if json_match:
            content = json_match.group(1)

        data = json.loads(content)
        return SceneAnalysis(**data)

    except Exception as e:
        log.warning("Muse vision call encountered an error (%s); falling back to deterministic analysis", e)
        return _get_fallback_scene_analysis(problem)

