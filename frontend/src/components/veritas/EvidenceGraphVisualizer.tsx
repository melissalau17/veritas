import React, { useState } from "react";
import { cn } from "@/lib/utils";
import type { InvestigationGraph, GraphNode, GraphEdge } from "@/lib/api";

interface EvidenceGraphVisualizerProps {
  graph?: InvestigationGraph;
  onNodeClick?: (node: GraphNode) => void;
  className?: string;
}

export function EvidenceGraphVisualizer({
  graph,
  onNodeClick,
  className,
}: EvidenceGraphVisualizerProps) {
  const [selectedNodeId, setSelectedNodeId] = useState<string>("component:flexible_coupling");

  const nodes = graph?.nodes || [];
  const edges = graph?.edges || [];

  const fallbackNode: GraphNode = {
    id: "placeholder:no-data",
    type: "observation",
    label: "No graph data",
  };

  const handleSelect = (node?: GraphNode) => {
    const nextNode = node ?? fallbackNode;
    setSelectedNodeId(nextNode.id);
    if (onNodeClick) onNodeClick(nextNode);
  };

  const selectedNode = nodes.find((n) => n.id === selectedNodeId) ?? nodes[0] ?? fallbackNode;

  return (
    <div className={cn("border border-border bg-surface", className)}>
      <header className="flex items-center justify-between border-b border-border bg-surface-2 px-4 py-2.5">
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs font-bold uppercase tracking-wider text-signal">
            EVIDENCE GRAPH
          </span>
          <span className="text-[11.5px] text-muted-foreground">
            Dynamic Graph Grounded in Engineering Records
          </span>
        </div>
        <div className="flex items-center gap-3 text-[11px] font-mono text-muted-foreground">
          <span>{nodes.length} nodes</span>
          <span>•</span>
          <span>{edges.length} relations</span>
        </div>
      </header>

      <div className="grid gap-4 p-4 lg:grid-cols-[1fr_280px]">
        {/* Interactive Graph Layout Area */}
        <div className="flex flex-col items-center justify-center space-y-4 rounded border border-border bg-slate-950 p-6 text-white min-h-[360px] overflow-x-auto">
          {/* Level 1: Asset Node */}
          <div className="flex items-center justify-center">
            <button
              onClick={() => handleSelect(nodes.find((n) => n.type === "asset") || nodes[0])}
              className={cn(
                "rounded-md border-2 px-4 py-2 font-mono text-xs font-bold transition-all shadow-md",
                selectedNodeId.startsWith("asset")
                  ? "border-sky-400 bg-sky-950/80 text-sky-200 ring-2 ring-sky-400"
                  : "border-slate-700 bg-slate-900 text-slate-200 hover:border-slate-500"
              )}
            >
              <div className="text-[10px] uppercase tracking-wider text-slate-400">Plant Asset</div>
              <div className="text-sm">P-101 · CP-200 Centrifugal Pump</div>
            </button>
          </div>

          {/* Relation: HAS_COMPONENT */}
          <div className="flex flex-col items-center">
            <div className="h-4 w-0.5 bg-slate-600" />
            <span className="rounded bg-slate-800 px-2 py-0.5 font-mono text-[9.5px] uppercase tracking-widest text-slate-400">
              HAS_COMPONENT
            </span>
            <div className="h-4 w-0.5 bg-slate-600" />
            <div className="text-slate-500 -mt-1 text-xs">▼</div>
          </div>

          {/* Level 2: Component Node (Focal Point) */}
          <div className="flex items-center justify-center">
            <button
              onClick={() =>
                handleSelect(nodes.find((n) => n.type === "component") || nodes[0])
              }
              className={cn(
                "rounded-md border-2 px-5 py-2.5 font-mono text-xs font-bold transition-all shadow-lg",
                selectedNodeId.startsWith("component")
                  ? "border-cyan-400 bg-cyan-950/90 text-cyan-200 ring-2 ring-cyan-400 scale-105"
                  : "border-cyan-700/70 bg-slate-900 text-cyan-300 hover:border-cyan-500"
              )}
            >
              <div className="text-[10px] uppercase tracking-wider text-cyan-400 font-sans font-semibold">
                Grounded Physical Component
              </div>
              <div className="text-base text-white">Flexible Coupling</div>
              <div className="text-[10px] text-cyan-300/80 font-normal mt-0.5">
                Segmented via SAM 3.1
              </div>
            </button>
          </div>

          {/* Branch Relations: MAINTENANCE_ON & RELATED_TO */}
          <div className="w-full max-w-md px-8">
            <div className="flex items-center justify-between">
              {/* Left Branch to WO-1842 */}
              <div className="flex flex-col items-center">
                <div className="h-4 w-0.5 bg-slate-600" />
                <span className="rounded bg-blue-950 border border-blue-800 px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-wider text-blue-300">
                  MAINTENANCE_ON
                </span>
                <div className="h-4 w-0.5 bg-slate-600" />
                <div className="text-slate-500 -mt-1 text-xs">▼</div>
              </div>

              {/* Right Branch to RCA-017 */}
              <div className="flex flex-col items-center">
                <div className="h-4 w-0.5 bg-slate-600" />
                <span className="rounded bg-amber-950 border border-amber-800 px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-wider text-amber-300">
                  RELATED_TO
                </span>
                <div className="h-4 w-0.5 bg-slate-600" />
                <div className="text-slate-500 -mt-1 text-xs">▼</div>
              </div>
            </div>
          </div>

          {/* Level 3: WO-1842 & RCA-017 */}
          <div className="grid w-full max-w-lg grid-cols-2 gap-4">
            {/* WO-1842 */}
            <button
              onClick={() =>
                handleSelect(nodes.find((n) => n.id.includes("WO-1842")) || nodes[0])
              }
              className={cn(
                "rounded border-2 p-3 text-left transition-all",
                selectedNodeId.includes("WO-1842")
                  ? "border-blue-400 bg-blue-950/80 text-blue-100 ring-2 ring-blue-400"
                  : "border-slate-700 bg-slate-900 text-slate-300 hover:border-slate-500"
              )}
            >
              <div className="font-mono text-[10px] font-bold text-blue-400">WORK ORDER</div>
              <div className="font-mono text-sm font-bold">WO-1842</div>
              <div className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                Flexible coupling replaced (2026-10-27)
              </div>
            </button>

            {/* RCA-017 */}
            <button
              onClick={() =>
                handleSelect(nodes.find((n) => n.id.includes("RCA-017")) || nodes[0])
              }
              className={cn(
                "rounded border-2 p-3 text-left transition-all",
                selectedNodeId.includes("RCA-017")
                  ? "border-amber-400 bg-amber-950/80 text-amber-100 ring-2 ring-amber-400"
                  : "border-slate-700 bg-slate-900 text-slate-300 hover:border-slate-500"
              )}
            >
              <div className="font-mono text-[10px] font-bold text-amber-400">HISTORICAL RCA</div>
              <div className="font-mono text-sm font-bold">RCA-017</div>
              <div className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                Coupling misalignment vibration
              </div>
            </button>
          </div>

          {/* Connector: RCA-017 REFERENCES MNT-014 Rev 2 */}
          <div className="flex flex-col items-center">
            <div className="h-4 w-0.5 bg-slate-600" />
            <span className="rounded bg-rose-950 border border-rose-800 px-2 py-0.5 font-mono text-[9px] uppercase tracking-wider text-rose-300">
              REFERENCES (SUPERSEDED)
            </span>
            <div className="h-4 w-0.5 bg-slate-600" />
            <div className="text-slate-500 -mt-1 text-xs">▼</div>
          </div>

          {/* Level 4: Procedures Revision Chain */}
          <div className="grid w-full max-w-lg grid-cols-2 gap-4">
            {/* MNT-014 Rev 2 */}
            <button
              onClick={() =>
                handleSelect(nodes.find((n) => n.id.includes("Rev2")) || nodes[0])
              }
              className={cn(
                "rounded border-2 p-3 text-left transition-all",
                selectedNodeId.includes("Rev2")
                  ? "border-red-500 bg-red-950/80 text-red-100 ring-2 ring-red-400"
                  : "border-red-900/80 bg-slate-900 text-slate-300 hover:border-red-700"
              )}
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-[10px] font-bold text-red-400">PROCEDURE</span>
                <span className="bg-red-900/80 px-1 text-[9px] font-mono text-red-300">SUPERSEDED</span>
              </div>
              <div className="font-mono text-xs font-bold text-red-200">MNT-014 Rev 2</div>
              <div className="font-mono text-sm font-black text-red-400 mt-1">0.15 mm</div>
            </button>

            {/* MNT-014 Rev 4 */}
            <button
              onClick={() =>
                handleSelect(nodes.find((n) => n.id.includes("Rev4")) || nodes[0])
              }
              className={cn(
                "rounded border-2 p-3 text-left transition-all",
                selectedNodeId.includes("Rev4")
                  ? "border-emerald-500 bg-emerald-950/80 text-emerald-100 ring-2 ring-emerald-400"
                  : "border-emerald-900/80 bg-slate-900 text-slate-300 hover:border-emerald-700"
              )}
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-[10px] font-bold text-emerald-400">PROCEDURE</span>
                <span className="bg-emerald-900/80 px-1 text-[9px] font-mono text-emerald-300">CURRENT</span>
              </div>
              <div className="font-mono text-xs font-bold text-emerald-200">MNT-014 Rev 4</div>
              <div className="font-mono text-sm font-black text-emerald-400 mt-1">0.08 mm</div>
            </button>
          </div>

          {/* Supersession Arrow between Rev 2 and Rev 4 */}
          <div className="text-[11px] font-mono text-emerald-400">
            MNT-014 Rev 2 ── SUPERSEDED_BY ──▶ MNT-014 Rev 4
          </div>
        </div>

        {/* Selected Node Details Side Panel */}
        <aside className="border border-border bg-surface-2 p-3 text-[12.5px]">
          <div className="label-caps text-muted-foreground">Inspected Graph Entity</div>
          {selectedNode ? (
            <div className="mt-2 space-y-3">
              <div>
                <span className="font-mono text-xs font-bold text-signal block">
                  {selectedNode.type.toUpperCase()}
                </span>
                <h4 className="font-mono text-sm font-bold text-foreground">
                  {selectedNode.label}
                </h4>
              </div>

              {selectedNode.status && (
                <div>
                  <span className="label-caps text-muted-foreground">Status</span>
                  <div className="font-mono font-bold uppercase mt-0.5 text-xs">
                    {selectedNode.status}
                  </div>
                </div>
              )}

              {selectedNode.metadata && (
                <div className="space-y-1.5 border-t border-border pt-2">
                  <span className="label-caps text-muted-foreground">Evidence Attributes</span>
                  {Object.entries(selectedNode.metadata).map(([k, v]) => (
                    <div key={k} className="text-xs">
                      <strong className="text-muted-foreground capitalize">{k}:</strong>{" "}
                      <span className="font-mono">{String(v)}</span>
                    </div>
                  ))}
                </div>
              )}

              <div className="border-t border-border pt-2 text-[11px] text-muted-foreground">
                Click any node in the graph diagram to inspect its engineering provenance.
              </div>
            </div>
          ) : (
            <div className="mt-2 text-muted-foreground">Select a node to inspect provenance.</div>
          )}
        </aside>
      </div>
    </div>
  );
}

export default EvidenceGraphVisualizer;

