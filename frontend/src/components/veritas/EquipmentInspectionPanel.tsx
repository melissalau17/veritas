import React, { useState, useMemo } from "react";
import { cn } from "@/lib/utils";
import { Btn, Panel } from "@/components/veritas/Shell";
import type {
  SceneAnalysis,
  SegmentationResult,
  ComponentHistory,
  VisibleComponent,
} from "@/lib/api";
import type { ComponentConfig } from "@/data/equipmentTroubleshooting";

interface EquipmentInspectionPanelProps {
  imageUrl: string | null;
  sceneAnalysis: SceneAnalysis | null;
  segmentation: SegmentationResult | null;
  allSegmentations?: SegmentationResult[];
  componentHistory: ComponentHistory | null;
  selectedComponent?: string;
  componentConfigs?: ComponentConfig[];
  onSelectComponent: (componentName: string) => void;
  onUploadImage: (file: File) => void;
  onLoadReferenceImage: () => void;
  loading?: boolean;
  className?: string;
}

export function EquipmentInspectionPanel({
  imageUrl,
  sceneAnalysis,
  segmentation,
  allSegmentations = [],
  componentHistory,
  selectedComponent,
  componentConfigs,
  onSelectComponent,
  onUploadImage,
  onLoadReferenceImage,
  loading = false,
  className,
}: EquipmentInspectionPanelProps) {
  const [selectedComp, setSelectedComp] = useState<string>(
    selectedComponent || sceneAnalysis?.relevant_component || componentConfigs?.[0]?.name || "flexible coupling",
  );
  const [showMask, setShowMask] = useState<boolean>(true);

  // Sync with prop when selectedComponent changes externally
  React.useEffect(() => {
    if (selectedComponent && selectedComponent.toLowerCase() !== selectedComp.toLowerCase()) {
      setSelectedComp(selectedComponent);
    }
  }, [selectedComponent]);

  const handleCompClick = (name: string) => {
    setSelectedComp(name);
    onSelectComponent(name);
  };

  // Standard spatial bounding boxes for CP-200 pump assembly (900 x 560)
  const defaultBoxes: Record<string, { left: number; top: number; right: number; bottom: number }> =
    {
      "electric motor": { left: 72, top: 156, right: 387, bottom: 403 },
      "flexible coupling": { left: 387, top: 179, right: 522, bottom: 380 },
      "centrifugal pump": { left: 522, top: 140, right: 828, bottom: 420 },
      "bearing housing": { left: 504, top: 201, right: 630, bottom: 358 },
    };

  const compDescriptions: Record<string, string> = {
    "electric motor":
      "Primary 3-phase AC induction driver motor (45 kW, 2950 RPM) delivering rotational drive torque to the pump via the flexible coupling.",
    "flexible coupling":
      "Mechanical transmission interface connecting motor and pump shafts. Primary focal component for post-coupling-replacement vibration.",
    "centrifugal pump":
      "CP-200 centrifugal pump casing, impeller, and suction/discharge nozzles generating process flow.",
    "bearing housing":
      "Pump drive-end and non-drive-end bearing assembly supporting radial and thrust loads.",
  };

  const fallbackRecordsByComp: Record<
    string,
    Array<{ source: string; type: string; summary: string }>
  > = {
    "electric motor": [
      {
        source: "RCA-017.txt",
        type: "Root Cause Analysis",
        summary:
          "Corrective Action: Realign pump and motor shafts according to approved procedure.",
      },
      {
        source: "OEM-Pump-Manual.txt",
        type: "Technical Manual",
        summary: "Step 4: Verify driver motor mounting bolts, baseplate level, and alignment.",
      },
    ],
    "flexible coupling": [
      {
        source: "WO-1842.txt",
        type: "Work Order",
        summary: "Flexible coupling replaced due to wear (2026-10-27).",
      },
      {
        source: "RCA-017.txt",
        type: "Historical RCA",
        summary:
          "High vibration detected after coupling maintenance; root cause: coupling misalignment.",
      },
      {
        source: "MNT-014-Rev4.txt",
        type: "Approved Standard",
        summary: "Pump Coupling Alignment Procedure (maximum allowable offset: 0.08 mm).",
      },
    ],
    "centrifugal pump": [
      {
        source: "OEM-Pump-Manual.txt",
        type: "Technical Manual",
        summary: "CP-200 Centrifugal Pump operational procedures and baseline vibration envelopes.",
      },
      {
        source: "equipment_register.json",
        type: "Asset Register",
        summary: "Asset P-101: Centrifugal Pump Model CP-200, Process Area A.",
      },
    ],
    "bearing housing": [
      {
        source: "OEM-Pump-Manual.txt",
        type: "Technical Manual",
        summary: "Step 3: Check bearing condition, lubrication quality, and operating temperature.",
      },
      {
        source: "RCA-022.txt",
        type: "Analogous RCA",
        summary:
          "High vibration caused by bearing degradation due to lubricant contamination (CP-100 series).",
      },
    ],
  };

  // Dynamic merged lookups based on componentConfigs
  const activeBoxes = useMemo(() => {
    const map = { ...defaultBoxes };
    if (componentConfigs) {
      for (const c of componentConfigs) {
        map[c.name.toLowerCase()] = c.box;
      }
    }
    return map;
  }, [componentConfigs]);

  const activeDescriptions = useMemo(() => {
    const map = { ...compDescriptions };
    if (componentConfigs) {
      for (const c of componentConfigs) {
        map[c.name.toLowerCase()] = c.description;
      }
    }
    return map;
  }, [componentConfigs]);

  const activeFallbackRecords = useMemo(() => {
    const map = { ...fallbackRecordsByComp };
    if (componentConfigs) {
      for (const c of componentConfigs) {
        map[c.name.toLowerCase()] = c.records;
      }
    }
    return map;
  }, [componentConfigs]);

  // Match segmentation from backend allSegmentations, or single segmentation, or fallback box
  const matchedSeg = allSegmentations.find(
    (s) => s.concept.toLowerCase() === selectedComp.toLowerCase(),
  );

  const activeSegmentation: SegmentationResult =
    matchedSeg ||
    (segmentation && segmentation.concept.toLowerCase() === selectedComp.toLowerCase()
      ? segmentation
      : {
          concept: selectedComp,
          object_id: "0",
          box: activeBoxes[selectedComp.toLowerCase()] || {
            left: 72,
            top: 156,
            right: 387,
            bottom: 403,
          },
          mask_url: null,
          mask_svg: null,
          width: 900,
          height: 560,
          status: "completed",
        });

  const visibleComps = sceneAnalysis?.visible_components || (
    componentConfigs && componentConfigs.length > 0
      ? componentConfigs.map((c) => ({ name: c.name, category: c.category, relevance: c.relevance }))
      : [
          { name: "electric motor", category: "driver", relevance: "secondary" },
          { name: "flexible coupling", category: "power transmission", relevance: "high" },
          { name: "centrifugal pump", category: "pump", relevance: "high" },
          { name: "bearing housing", category: "bearing assembly", relevance: "moderate" },
        ]
  );

  const activeRecords =
    componentHistory?.component.toLowerCase() === selectedComp.toLowerCase() &&
    componentHistory.related_records.length > 0
      ? componentHistory.related_records
      : activeFallbackRecords[selectedComp.toLowerCase()] ||
        activeFallbackRecords["flexible coupling"] ||
        [];

  return (
    <Panel
      title="Equipment Visual Context — Meta Multimodal Grounding"
      right={
        <div className="flex items-center gap-2">
          <span className="hidden sm:inline-block font-mono text-[10px] uppercase font-bold text-sky-700 bg-sky-100 px-2 py-0.5 border border-sky-300">
            Meta Muse + SAM 3.1
          </span>
          <label className="flex items-center gap-1.5 text-[11.5px] text-muted-foreground cursor-pointer">
            <input
              type="checkbox"
              checked={showMask}
              onChange={(e) => setShowMask(e.target.checked)}
            />
            Show SAM 3.1 Mask
          </label>
          <Btn onClick={onLoadReferenceImage} disabled={loading}>
            Reload Reference Visual
          </Btn>
        </div>
      }
      className={cn("overflow-hidden", className)}
    >
      {/* Meta AI Indispensable Pipeline Banner */}
      <div className="mb-3 border border-sky-500/50 bg-sky-500/10 p-2.5 text-[12px] text-sky-950 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-sky-600 font-mono text-[10px] font-bold text-white">
            M
          </span>
          <div>
            <strong>Meta AI Core Architecture:</strong> 1. <strong>Meta Muse</strong> analyzes
            rotating equipment physics to select the fault-critical component &rarr; 2.{" "}
            <strong>Meta SAM 3.1</strong> executes zero-shot spatial grounding.
          </div>
        </div>
        <span className="text-[11px] font-semibold text-sky-800 italic shrink-0">
          Essential to physical-to-evidence graph linkage
        </span>
      </div>
      <div className="grid gap-4 xl:grid-cols-[1fr_320px]">
        {/* Left: Image with SAM 3.1 Overlay */}
        <div className="relative flex flex-col items-center justify-center overflow-hidden rounded border border-border bg-slate-950 p-2 min-h-[360px]">
          {imageUrl ? (
            <div className="relative inline-block w-full max-w-[720px] select-none">
              {/* Main equipment image */}
              <img
                src={imageUrl}
                alt="Industrial Equipment Assembly"
                className="w-full h-auto rounded object-contain block max-h-[460px]"
              />

              {/* SAM 3.1 Overlay Layer */}
              {showMask && activeSegmentation?.box && (
                <div
                  className="absolute inset-0 pointer-events-none transition-all duration-300"
                  style={{ width: "100%", height: "100%" }}
                >
                  {/* If matching SVG mask available, render directly */}
                  {activeSegmentation.mask_svg &&
                  activeSegmentation.concept.toLowerCase() === selectedComp.toLowerCase() ? (
                    <div
                      className="absolute inset-0 w-full h-full pointer-events-none"
                      dangerouslySetInnerHTML={{ __html: activeSegmentation.mask_svg }}
                    />
                  ) : (
                    /* Dynamic SVG Grounding Box */
                    <svg
                      viewBox={`0 0 ${activeSegmentation.width || 900} ${activeSegmentation.height || 560}`}
                      className="w-full h-full pointer-events-none"
                    >
                      <defs>
                        <filter
                          id={`glow-${selectedComp.replace(/\s+/g, "-")}`}
                          x="-20%"
                          y="-20%"
                          width="140%"
                          height="140%"
                        >
                          <feGaussianBlur stdDeviation="3" result="blur" />
                          <feComposite in="SourceGraphic" in2="blur" operator="over" />
                        </filter>
                      </defs>
                      <rect
                        x={activeSegmentation.box.left}
                        y={activeSegmentation.box.top}
                        width={activeSegmentation.box.right - activeSegmentation.box.left}
                        height={activeSegmentation.box.bottom - activeSegmentation.box.top}
                        rx={8}
                        fill="#0ea5e9"
                        fillOpacity="0.25"
                        stroke="#38bdf8"
                        strokeWidth="2.5"
                        strokeDasharray="6,4"
                        filter={`url(#glow-${selectedComp.replace(/\s+/g, "-")})`}
                      />
                      <circle
                        cx={activeSegmentation.box.left}
                        cy={activeSegmentation.box.top}
                        r="4"
                        fill="#38bdf8"
                      />
                      <circle
                        cx={activeSegmentation.box.right}
                        cy={activeSegmentation.box.top}
                        r="4"
                        fill="#38bdf8"
                      />
                      <circle
                        cx={activeSegmentation.box.left}
                        cy={activeSegmentation.box.bottom}
                        r="4"
                        fill="#38bdf8"
                      />
                      <circle
                        cx={activeSegmentation.box.right}
                        cy={activeSegmentation.box.bottom}
                        r="4"
                        fill="#38bdf8"
                      />
                      <g
                        transform={`translate(${activeSegmentation.box.left}, ${Math.max(18, activeSegmentation.box.top - 8)})`}
                      >
                        <rect
                          x="0"
                          y="-14"
                          width={selectedComp.length * 8 + 18}
                          height="18"
                          rx="3"
                          fill="#0f172a"
                          fillOpacity="0.9"
                        />
                        <text
                          x="8"
                          y="-1"
                          fill="#38bdf8"
                          fontFamily="monospace"
                          fontSize="11"
                          fontWeight="bold"
                        >
                          {selectedComp.toUpperCase()}
                        </text>
                      </g>
                    </svg>
                  )}
                </div>
              )}

              {/* Status Pill in Corner */}
              <div className="absolute bottom-2 left-2 flex items-center gap-1.5 rounded bg-slate-900/90 border border-slate-700 px-2 py-1 text-[11px] font-mono text-slate-200">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                SAM 3.1 Active · {selectedComp}
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center p-8 text-center text-slate-400">
              <div className="text-3xl mb-2">📷</div>
              <div className="text-sm font-semibold text-slate-200">No Image Uploaded</div>
              <p className="text-xs text-slate-400 mt-1 max-w-xs">
                Upload an industrial pump photo, or load the P-101 reference image to inspect the
                visual assembly.
              </p>
              <div className="mt-4 flex gap-2">
                <Btn onClick={onLoadReferenceImage}>Use Equipment Reference Visual</Btn>
              </div>
            </div>
          )}

          {/* Interactive Component Chips Toolbar */}
          <div className="mt-3 flex flex-wrap items-center justify-center gap-1.5 w-full border-t border-slate-800 pt-2">
            <span className="text-[11px] font-mono uppercase text-slate-400 mr-1">
              Select Component:
            </span>
            {visibleComps.map((comp) => {
              const isSelected = comp.name.toLowerCase() === selectedComp.toLowerCase();
              return (
                <button
                  key={comp.name}
                  onClick={() => handleCompClick(comp.name)}
                  className={cn(
                    "rounded px-2.5 py-1 text-[11.5px] font-mono font-medium transition-all",
                    isSelected
                      ? "bg-cyan-500 text-slate-950 font-bold shadow-md"
                      : "bg-slate-800 text-slate-300 hover:bg-slate-700",
                  )}
                >
                  {comp.name}
                </button>
              );
            })}
          </div>
        </div>

        {/* Right: Selected Component & Engineering Records Card */}
        <aside className="flex flex-col justify-between space-y-4 rounded border border-border bg-surface-2 p-4 text-[12.5px]">
          <div className="space-y-3">
            <div>
              <span className="label-caps text-muted-foreground text-[10px]">
                Selected Physical Component
              </span>
              <h3 className="font-mono text-lg font-bold text-signal capitalize">{selectedComp}</h3>
              <p className="text-[11.5px] text-muted-foreground mt-0.5">
                {compDescriptions[selectedComp.toLowerCase()] ||
                  sceneAnalysis?.relevance_reason ||
                  "Component identified in equipment assembly."}
              </p>
            </div>

            <div className="border-t border-border pt-3">
              <div className="label-caps text-muted-foreground text-[10px] mb-1.5">
                Linked Maintenance Records ({activeRecords.length})
              </div>
              <div className="space-y-2">
                {activeRecords.map((rec) => (
                  <div
                    key={rec.source}
                    className="rounded border border-border bg-surface p-2 text-xs"
                  >
                    <div className="flex items-center justify-between font-mono font-bold">
                      <span className="text-foreground">{rec.source}</span>
                      <span className="text-[10px] uppercase text-signal">{rec.type}</span>
                    </div>
                    <p className="mt-1 text-[11px] text-muted-foreground">{rec.summary}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Visual Uncertainty note */}
            <div className="rounded border border-amber-300 bg-amber-50/80 p-2 text-[11px] text-amber-900">
              <strong>Visual Safety Principle:</strong> Physical defect (e.g. misalignment) cannot
              be confirmed from photos alone. Verification requires laser alignment readings.
            </div>
          </div>

          {/* Quick upload dropzone */}
          <div className="border-t border-border pt-3">
            <label className="block text-center cursor-pointer rounded border border-dashed border-border bg-surface py-2 text-[11.5px] text-muted-foreground hover:bg-secondary">
              <span>Upload Custom Equipment Photo</span>
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) onUploadImage(file);
                }}
              />
            </label>
          </div>
        </aside>
      </div>
    </Panel>
  );
}

export default EquipmentInspectionPanel;
