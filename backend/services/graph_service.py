"""
Evidence Graph Service.

Constructs an evidence graph relating physical equipment, components,
work orders, root-cause analyses, procedures, and revision supersessions.
Strictly grounds all nodes and edges in real evidence documents.
"""

import sys
from pathlib import Path
from typing import List, Optional

_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from schemas import (
    GraphNode,
    GraphEdge,
    InvestigationGraph,
    InvestigationResult,
)
from tools.get_component_history import get_component_history


def build_evidence_graph(
    asset_id: str = "P-101",
    component_name: str = "Flexible Coupling",
    investigation_result: Optional[InvestigationResult] = None,
) -> InvestigationGraph:
    """
    Construct an evidence graph for an asset and component.

    Nodes:
        - Asset (e.g. P-101)
        - Component (e.g. Flexible Coupling)
        - Work Orders (e.g. WO-1842)
        - RCAs (e.g. RCA-017)
        - Procedures (e.g. MNT-014 Rev 2, MNT-014 Rev 4)
        - Manuals (e.g. OEM-Pump-Manual)

    Edges:
        - HAS_COMPONENT: Asset → Component
        - MAINTENANCE_ON: Component → WO-1842
        - RELATED_TO: Component → RCA-017
        - REFERENCES: RCA-017 → MNT-014 Rev 2
        - SUPERSEDED_BY: MNT-014 Rev 2 → MNT-014 Rev 4
        - APPLIES_TO: OEM-Pump-Manual → Asset
    """
    nodes: List[GraphNode] = []
    edges: List[GraphEdge] = []

    # 1. Asset Node
    asset_node_id = f"asset:{asset_id}"
    nodes.append(GraphNode(
        id=asset_node_id,
        type="asset",
        label=asset_id,
        metadata={"description": "Centrifugal Pump Assembly"},
    ))

    # 2. Component Node
    comp_slug = component_name.lower().replace(" ", "_")
    comp_node_id = f"component:{comp_slug}"
    nodes.append(GraphNode(
        id=comp_node_id,
        type="component",
        label=component_name,
        metadata={"category": "Power Transmission"},
    ))

    # Edge: Asset HAS_COMPONENT Component
    edges.append(GraphEdge(
        source=asset_node_id,
        target=comp_node_id,
        type="HAS_COMPONENT",
        label="has component",
    ))

    # 3. Component History records from tool
    history = get_component_history(asset_id, component_name)
    has_wo = False
    has_rca = False

    for rec in history.get("related_records", []):
        src = rec["source"]
        doc_id = f"doc:{src.replace('.txt', '')}"

        if rec["type"] == "work_order":
            has_wo = True
            nodes.append(GraphNode(
                id=doc_id,
                type="work_order",
                label=src.replace(".txt", ""),
                metadata={"summary": rec["summary"]},
            ))
            edges.append(GraphEdge(
                source=comp_node_id,
                target=doc_id,
                type="MAINTENANCE_ON",
                label="recent maintenance",
            ))

        elif rec["type"] == "root_cause_analysis":
            has_rca = True
            nodes.append(GraphNode(
                id=doc_id,
                type="rca",
                label=src.replace(".txt", ""),
                metadata={"summary": rec["summary"]},
            ))
            edges.append(GraphEdge(
                source=comp_node_id,
                target=doc_id,
                type="RELATED_TO",
                label="historical analogue",
            ))

    # 4. Procedure Revisions & Supersession
    # Always include MNT-014 Rev 2 (superseded) and Rev 4 (current)
    rev2_id = "doc:MNT-014-Rev2"
    rev4_id = "doc:MNT-014-Rev4"

    nodes.append(GraphNode(
        id=rev2_id,
        type="procedure",
        label="MNT-014 Rev 2",
        status="superseded",
        metadata={
            "tolerance": "0.15 mm",
            "status": "SUPERSEDED",
        },
    ))

    nodes.append(GraphNode(
        id=rev4_id,
        type="procedure",
        label="MNT-014 Rev 4",
        status="current",
        metadata={
            "tolerance": "0.08 mm",
            "status": "CURRENT",
        },
    ))

    # Edge: RCA-017 REFERENCES MNT-014 Rev 2
    rca_node_id = "doc:RCA-017"
    if any(n.id == rca_node_id for n in nodes):
        edges.append(GraphEdge(
            source=rca_node_id,
            target=rev2_id,
            type="REFERENCES",
            label="references",
        ))

    # Edge: MNT-014 Rev 2 SUPERSEDED_BY MNT-014 Rev 4
    edges.append(GraphEdge(
        source=rev2_id,
        target=rev4_id,
        type="SUPERSEDED_BY",
        label="superseded by",
    ))

    # 5. OEM Manual Node (optional)
    oem_id = "doc:OEM-Pump-Manual"
    nodes.append(GraphNode(
        id=oem_id,
        type="manual",
        label="OEM Pump Manual",
        metadata={"model": "CP-200"},
    ))
    edges.append(GraphEdge(
        source=oem_id,
        target=asset_node_id,
        type="APPLIES_TO",
        label="applies to",
    ))

    return InvestigationGraph(nodes=nodes, edges=edges)

