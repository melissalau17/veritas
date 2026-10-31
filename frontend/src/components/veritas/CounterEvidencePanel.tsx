import React from "react";
import { cn } from "@/lib/utils";
import type { ChallengeResponse } from "@/lib/api";

interface CounterEvidencePanelProps {
  challengeData: ChallengeResponse;
  onClose?: () => void;
  onInspectClaim?: (claimId: string) => void;
}

export function CounterEvidencePanel({
  challengeData,
  onClose,
  onInspectClaim,
}: CounterEvidencePanelProps) {
  const {
    hypothesis_id,
    counter_evidence,
    alternative_hypotheses,
    missing_information,
    updated_assessment,
  } = challengeData;

  return (
    <div className="border-2 border-amber-500 bg-surface shadow-md">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border bg-amber-500/10 px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="flex h-5 w-5 items-center justify-center rounded-full bg-amber-600 text-[11px] font-bold text-white">
            ⚠
          </span>
          <div>
            <h3 className="text-[14px] font-bold tracking-tight text-foreground">
              Counter-Evidence Review & Adversarial Challenge
            </h3>
            <p className="text-[11.5px] text-muted-foreground">
              Adversarial verification testing leading hypothesis{" "}
              <strong className="font-mono text-signal">{hypothesis_id}</strong> against alternative failure mechanisms
            </p>
          </div>
        </div>

        {onClose && (
          <button
            onClick={onClose}
            className="text-[12px] font-semibold text-muted-foreground hover:text-foreground"
          >
            ✕ Dismiss
          </button>
        )}
      </div>

      <div className="p-4 space-y-4">
        {/* Core Principle Banner */}
        <div className="border border-amber-300 bg-amber-50/70 p-3 text-[12px] text-amber-950">
          <strong>Veritas Principle:</strong> The challenge agent does not defend the original answer.
          A lack of contradictory evidence does not prove the hypothesis is correct; root cause remains{" "}
          <strong>NOT CONFIRMED</strong> until physical measurements verify it.
        </div>

        {/* Updated Comparative Assessment */}
        <div className="border border-border bg-surface-2/40 p-3.5">
          <div className="flex items-center justify-between">
            <span className="label-caps font-bold text-muted-foreground">
              Comparative Engineering Assessment
            </span>
            <span className="inline-flex items-center gap-1 border border-emerald-600 bg-emerald-50 px-2 py-0.5 text-[10.5px] font-bold uppercase text-emerald-800">
              Leading Path: {updated_assessment.status}
            </span>
          </div>
          <p className="mt-2 text-[13px] leading-relaxed text-foreground">
            {updated_assessment.assessment}
          </p>
        </div>

        {/* Deterministic Hypothesis Strength Comparison */}
        <div>
          <div className="label-caps mb-2 text-muted-foreground font-bold">
            Deterministic Evidence Strength Comparison
          </div>
          <div className="grid gap-2.5 sm:grid-cols-2 lg:grid-cols-3">
            {updated_assessment.comparison.map((h) => (
              <div
                key={h.id}
                className={cn(
                  "border p-3",
                  h.id === hypothesis_id
                    ? "border-signal bg-signal/5"
                    : "border-border bg-surface-2/30"
                )}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[12px] font-bold text-signal">{h.id}</span>
                  <span
                    className={cn(
                      "px-2 py-0.5 text-[10px] font-bold uppercase",
                      h.strength === "strong" && "bg-emerald-100 text-emerald-800",
                      h.strength === "moderate" && "bg-amber-100 text-amber-800",
                      h.strength === "weak" && "bg-gray-100 text-gray-700",
                      h.strength === "insufficient" && "bg-red-100 text-red-700"
                    )}
                  >
                    {h.strength} evidence
                  </span>
                </div>
                <div className="mt-1 text-[13px] font-bold">{h.title}</div>
                <div className="mt-2 space-y-1 text-[11px] text-muted-foreground font-mono">
                  <div>✓ Supporting: {h.supporting_count} doc(s)</div>
                  <div>✗ Contradicting: {h.contradicting_count}</div>
                  <div>• Missing: {h.missing_count} measurement(s)</div>
                </div>
                {h.rationale && (
                  <p className="mt-2 border-t border-border/60 pt-1.5 text-[11px] text-muted-foreground">
                    {h.rationale}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Counter-Evidence & Alternative Mechanisms */}
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <div className="label-caps mb-2 text-amber-900 font-bold">
              Alternative Failure Mechanisms Located
            </div>
            <div className="space-y-2">
              {counter_evidence.map((ce, idx) => (
                <div key={idx} className="border border-border bg-surface p-2.5">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[11.5px] font-bold text-signal">
                      {ce.source}
                    </span>
                    {ce.section && (
                      <span className="text-[10.5px] text-muted-foreground font-mono">
                        {ce.section}
                      </span>
                    )}
                  </div>
                  <p className="mt-1 text-[12px] text-foreground leading-snug">{ce.text}</p>
                  {ce.applicability_warning && (
                    <div className="mt-1.5 border-l-2 border-amber-500 bg-amber-50/70 pl-2 py-0.5 text-[11px] text-amber-900">
                      ⚠ {ce.applicability_warning}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Missing Information / Unresolved Variables */}
          <div>
            <div className="label-caps mb-2 text-red-900 font-bold">
              Missing Measurements Required to Confirm
            </div>
            <ul className="space-y-1.5 border border-border bg-surface p-3 text-[12px]">
              {missing_information.map((m, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-amber-600 font-bold">•</span>
                  <span className="text-foreground">{m}</span>
                </li>
              ))}
            </ul>

            {/* Recommended Action Sequence */}
            <div className="mt-3">
              <div className="label-caps mb-1.5 text-muted-foreground font-bold">
                Verification Action Sequence
              </div>
              <ol className="space-y-1 border border-border bg-surface p-2.5 text-[11.5px]">
                {updated_assessment.action_items.map((item, idx) => (
                  <li key={idx} className="text-muted-foreground">
                    {item}
                  </li>
                ))}
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

