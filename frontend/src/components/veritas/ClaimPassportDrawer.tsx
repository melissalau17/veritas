import React from "react";
import { cn } from "@/lib/utils";
import type { ClaimPassport } from "@/lib/api";

interface ClaimPassportDrawerProps {
  passport: ClaimPassport | null;
  isOpen: boolean;
  onClose: () => void;
}

export function ClaimPassportDrawer({
  passport,
  isOpen,
  onClose,
}: ClaimPassportDrawerProps) {
  if (!isOpen || !passport) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="relative w-full max-w-xl bg-surface border-l border-border h-full overflow-y-auto p-6 shadow-2xl space-y-5 animate-in slide-in-from-right duration-200">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-border pb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-[13px] font-bold text-signal bg-signal/10 px-2 py-0.5 border border-signal/30">
                {passport.claim_id}
              </span>
              <span className="label-caps font-mono text-[11px] text-muted-foreground">
                {passport.claim_type.replace("_", " ")}
              </span>
            </div>
            <h2 className="mt-1.5 text-lg font-bold tracking-tight">Claim Passport</h2>
            <p className="text-[12px] text-muted-foreground">
              Full provenance audit, revision tracking, and applicability verification
            </p>
          </div>

          <button
            onClick={onClose}
            className="rounded border border-border p-1.5 text-muted-foreground hover:bg-surface-2 hover:text-foreground"
          >
            ✕
          </button>
        </div>

        {/* Claim Text Callout */}
        <div className="border-l-4 border-signal bg-surface-2/60 p-3.5">
          <div className="label-caps text-[10.5px] font-bold text-muted-foreground">
            Formulated Claim
          </div>
          <p className="mt-1 text-[13.5px] font-medium leading-relaxed">{passport.text}</p>
        </div>

        {/* Status & Confirmation State */}
        <div className="grid grid-cols-2 gap-3">
          <div className="border border-border p-2.5 bg-surface-2/30">
            <span className="label-caps text-[10px] text-muted-foreground block">
              Evidence Status
            </span>
            <span
              className={cn(
                "mt-1 inline-block px-2 py-0.5 text-[11px] font-bold uppercase",
                passport.status === "supported" && "bg-emerald-100 text-emerald-800",
                passport.status === "partially_supported" && "bg-amber-100 text-amber-800",
                passport.status === "unsupported" && "bg-gray-100 text-gray-700"
              )}
            >
              {passport.status.replace("_", " ")}
            </span>
          </div>

          <div className="border border-border p-2.5 bg-surface-2/30">
            <span className="label-caps text-[10px] text-muted-foreground block">
              Physical Confirmation
            </span>
            <span className="mt-1 inline-block border border-amber-300 bg-amber-50 px-2 py-0.5 text-[11px] font-bold uppercase text-amber-900">
              {passport.confirmation_state === "confirmed" ? "CONFIRMED" : "HYPOTHESIS · UNCONFIRMED"}
            </span>
          </div>
        </div>

        {/* Supporting Sources */}
        <div>
          <div className="label-caps font-bold text-muted-foreground mb-2">
            Supporting Evidence Sources ({passport.supporting_sources.length})
          </div>
          <div className="space-y-2.5">
            {passport.supporting_sources.map((src, i) => (
              <div key={i} className="border border-border bg-surface p-3">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[12.5px] font-bold text-signal">
                    {src.source}
                  </span>
                  <div className="flex items-center gap-1.5">
                    {src.section && (
                      <span className="font-mono text-[10.5px] text-muted-foreground">
                        {src.section}
                      </span>
                    )}
                    {src.revision_status && (
                      <span
                        className={cn(
                          "px-1.5 py-0.5 text-[9.5px] font-bold uppercase",
                          src.revision_status === "CURRENT"
                            ? "bg-emerald-100 text-emerald-800"
                            : "bg-red-100 text-red-800"
                        )}
                      >
                        {src.revision_status}
                      </span>
                    )}
                  </div>
                </div>
                {src.snippet && (
                  <p className="mt-2 text-[12px] font-mono text-muted-foreground bg-surface-2/40 p-2 border border-border/50">
                    "{src.snippet}"
                  </p>
                )}
                {src.applicability && (
                  <div className="mt-2 text-[11px] text-muted-foreground">
                    <strong>Applicability:</strong>{" "}
                    <span
                      className={cn(
                        "font-semibold",
                        src.applicability === "APPLICABLE" && "text-emerald-700",
                        src.applicability === "APPLICABLE WITH WARNING" && "text-amber-700",
                        src.applicability === "ANALOGOUS ONLY" && "text-blue-700"
                      )}
                    >
                      {src.applicability}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Applicability Checks Breakdown */}
        {passport.applicability_checks.length > 0 && (
          <div>
            <div className="label-caps font-bold text-muted-foreground mb-2">
              Multi-Factor Applicability Audit
            </div>
            <div className="border border-border divide-y divide-border text-[12px]">
              {passport.applicability_checks.map((chk, i) => (
                <div key={i} className="flex items-start justify-between p-2.5 bg-surface">
                  <div>
                    <span className="font-mono font-bold capitalize text-foreground">
                      {chk.criterion.replace("_", " ")}
                    </span>
                    {chk.message && (
                      <p className="mt-0.5 text-[11px] text-muted-foreground">{chk.message}</p>
                    )}
                  </div>
                  <span
                    className={cn(
                      "px-2 py-0.5 text-[10px] font-bold uppercase font-mono",
                      chk.status === "match" && "bg-emerald-100 text-emerald-800",
                      chk.status === "warning" && "bg-amber-100 text-amber-800",
                      chk.status === "mismatch" && "bg-red-100 text-red-800",
                      chk.status === "unknown" && "bg-gray-100 text-gray-700"
                    )}
                  >
                    {chk.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Revision Context */}
        {passport.revision_context.length > 0 && (
          <div>
            <div className="label-caps font-bold text-muted-foreground mb-2">
              Revision History & Status
            </div>
            <div className="space-y-2">
              {passport.revision_context.map((rev, i) => (
                <div
                  key={i}
                  className="border border-amber-300 bg-amber-50/60 p-3 text-[12px] text-amber-950"
                >
                  <div className="flex items-center justify-between font-mono font-bold">
                    <span>{rev.document_id}</span>
                    <span
                      className={cn(
                        "px-1.5 py-0.5 text-[10px] uppercase",
                        rev.status === "CURRENT"
                          ? "bg-emerald-100 text-emerald-800"
                          : "bg-red-100 text-red-800"
                      )}
                    >
                      {rev.status}
                    </span>
                  </div>
                  {rev.warning && <p className="mt-1.5 leading-relaxed">{rev.warning}</p>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Missing Evidence */}
        {passport.missing_information.length > 0 && (
          <div>
            <div className="label-caps font-bold text-amber-900 mb-2">
              Unverified Assumptions & Missing Field Data
            </div>
            <ul className="space-y-1.5 border border-border bg-surface p-3 text-[12px] text-muted-foreground">
              {passport.missing_information.map((m, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-amber-500 font-bold">•</span>
                  <span>{m}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Close Button */}
        <div className="border-t border-border pt-4">
          <button
            onClick={onClose}
            className="w-full bg-navy text-navy-foreground py-2 text-[13px] font-bold hover:opacity-90"
          >
            Close Claim Passport
          </button>
        </div>
      </div>
    </div>
  );
}

