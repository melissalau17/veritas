import React from "react";
import { cn } from "@/lib/utils";

interface RevisionDiffCardProps {
  documentId?: string;
  oldRevision?: number;
  newRevision?: number;
  oldTolerance?: string;
  newTolerance?: string;
  referencedBy?: string;
  className?: string;
}

export function RevisionDiffCard({
  documentId = "MNT-014",
  oldRevision = 2,
  newRevision = 4,
  oldTolerance = "0.15 mm",
  newTolerance = "0.08 mm",
  referencedBy = "RCA-017.txt",
  className,
}: RevisionDiffCardProps) {
  return (
    <div
      className={cn(
        "border-2 border-red-500/80 bg-red-50/50 p-4 shadow-sm transition-all",
        className
      )}
    >
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-red-200 pb-2.5">
        <div className="flex items-center gap-2">
          <span className="flex h-5 w-5 items-center justify-center bg-red-600 font-mono text-xs font-bold text-white">
            !
          </span>
          <span className="font-mono text-xs font-bold uppercase tracking-wider text-red-900">
            ENGINEERING CRITERION CHANGED — {documentId}
          </span>
        </div>
        <span className="inline-flex items-center border border-red-300 bg-red-100 px-2 py-0.5 text-[10.5px] font-bold uppercase tracking-wide text-red-800">
          Superseded Reference Flagged
        </span>
      </div>

      {/* Main Metric Comparison */}
      <div className="mt-3.5 grid gap-3 md:grid-cols-2">
        {/* Old Revision */}
        <div className="border border-red-300 bg-white p-3 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[11px] font-bold text-muted-foreground">
              REVISION {oldRevision}
            </span>
            <span className="bg-red-100 px-1.5 py-0.5 font-mono text-[10px] font-bold uppercase text-red-700 border border-red-200">
              SUPERSEDED
            </span>
          </div>
          <div className="mt-2 text-[10.5px] uppercase tracking-wider text-muted-foreground">
            Maximum Allowable Offset
          </div>
          <div className="font-mono text-2xl font-black text-red-700 line-through decoration-red-400">
            {oldTolerance}
          </div>
          <div className="mt-1 text-[11px] text-muted-foreground">
            Standard at time of {referencedBy}
          </div>
        </div>

        {/* Current Revision */}
        <div className="border-2 border-emerald-500 bg-white p-3 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[11px] font-bold text-emerald-800">
              REVISION {newRevision}
            </span>
            <span className="bg-emerald-100 px-1.5 py-0.5 font-mono text-[10px] font-bold uppercase text-emerald-800 border border-emerald-300">
              CURRENT APPROVED
            </span>
          </div>
          <div className="mt-2 text-[10.5px] uppercase tracking-wider text-muted-foreground">
            Maximum Allowable Offset
          </div>
          <div className="flex items-baseline gap-2">
            <span className="font-mono text-2xl font-black text-emerald-700">
              {newTolerance}
            </span>
            <span className="font-mono text-[11.5px] font-bold text-emerald-600">
              ↓ 46.7% tighter tolerance
            </span>
          </div>
          <div className="mt-1 text-[11px] text-emerald-700 font-medium">
            Mandatory standard for current investigation
          </div>
        </div>
      </div>

      {/* Code-diff block */}
      <div className="mt-3.5 border border-slate-700 bg-slate-900 p-2.5 font-mono text-[12px] text-slate-100">
        <div className="text-[10px] uppercase tracking-wider text-slate-400 mb-1 font-sans font-semibold">
          Procedure Delta Diff:
        </div>
        <div className="text-red-400 bg-red-950/60 px-2 py-0.5">
          - Maximum allowable offset: {oldTolerance}
        </div>
        <div className="text-emerald-400 bg-emerald-950/60 px-2 py-0.5">
          + Maximum allowable offset: {newTolerance}
        </div>
      </div>

      {/* Engineering Impact Rationale */}
      <div className="mt-3 grid gap-2 text-[12px] text-red-950 md:grid-cols-2">
        <div>
          <span className="font-bold">Referenced by:</span>{" "}
          <span className="font-mono">{referencedBy}</span>
        </div>
        <div>
          <span className="font-bold">Engineering Impact:</span> Historical RCA remains relevant, but
          its original alignment criterion ({oldTolerance}) is no longer current. Current tolerance is
          strictly {newTolerance}.
        </div>
      </div>
    </div>
  );
}

export default RevisionDiffCard;

