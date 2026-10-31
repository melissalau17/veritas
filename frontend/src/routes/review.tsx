import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { reviewQueue } from "@/data/veritas";
import { Btn, Panel, Shell } from "@/components/veritas/Shell";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/review")({
  head: () => ({
    meta: [
      { title: "Knowledge Review Center — VERITAS" },
      {
        name: "description",
        content:
          "Technical authority queue for verifying operational lessons, procedures and troubleshooting paths before they enter the equipment knowledge base.",
      },
      { property: "og:title", content: "Knowledge Review Center — VERITAS" },
      {
        property: "og:description",
        content: "Govern what becomes verified engineering knowledge.",
      },
    ],
  }),
  component: ReviewCenter,
});

const kinds = ["All types", "Operational Lesson", "Procedure", "Troubleshooting Path"];

function ReviewCenter() {
  const [kind, setKind] = useState(kinds[0]);
  const [selected, setSelected] = useState(reviewQueue[0]!.id);
  const [decisions, setDecisions] = useState<Record<string, "approved" | "returned">>({});

  const rows = useMemo(
    () => reviewQueue.filter((r) => kind === kinds[0] || r.kind === kind),
    [kind],
  );
  const active = reviewQueue.find((r) => r.id === selected) ?? reviewQueue[0]!;

  const decide = (id: string, d: "approved" | "returned") =>
    setDecisions((prev) => ({ ...prev, [id]: d }));

  const pending = reviewQueue.filter((r) => !decisions[r.id]).length;

  return (
    <Shell
      breadcrumb={["LLDPE Unit", "Administration", "Knowledge Review Center"]}
      title="Knowledge Review Center"
      subtitle="Nothing becomes verified knowledge until a discipline technical authority signs it off."
      actions={
        <>
          <Btn>Governance settings</Btn>
          <Btn variant="primary">Bulk approve low-risk</Btn>
        </>
      }
    >
      <div className="grid grid-cols-2 gap-px border border-border bg-border lg:grid-cols-5">
        {[
          ["Awaiting review", String(pending), "Across 5 disciplines"],
          ["Decided this session", String(Object.keys(decisions).length), "By Reliability Engineer"],
          ["Median review time", "6.4 d", "Target ≤ 10 d"],
          ["Overdue > 21 days", "1", "Escalate to unit manager"],
          ["Verified this quarter", "112", "+18% vs. Q2"],
        ].map(([l, v, n]) => (
          <div key={l} className="bg-surface px-4 py-3">
            <div className="label-caps text-muted-foreground">{l}</div>
            <div className="mt-1 font-mono text-2xl font-bold">{v}</div>
            <div className="text-[11.5px] text-muted-foreground">{n}</div>
          </div>
        ))}
      </div>

      <div className="mt-5 grid gap-4 xl:grid-cols-[1fr_400px]">
        <Panel
          title="Review queue"
          right={
            <select
              value={kind}
              onChange={(e) => setKind(e.target.value)}
              className="h-7 border border-input bg-background px-2 text-[12.5px]"
            >
              {kinds.map((k) => (
                <option key={k}>{k}</option>
              ))}
            </select>
          }
          className="overflow-hidden"
        >
          <table className="w-full text-[13px]">
            <thead>
              <tr className="border-b border-border text-left">
                {["ID", "Submission", "Asset", "Type", "Author", "Age", "Risk", "Decision"].map((h) => (
                  <th key={h} className="label-caps py-2 text-muted-foreground">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr
                  key={r.id}
                  onClick={() => setSelected(r.id)}
                  className={cn(
                    "cursor-pointer border-b border-border last:border-0 hover:bg-accent/40",
                    selected === r.id && "bg-accent",
                  )}
                >
                  <td className="py-2 font-mono">{r.id}</td>
                  <td className="max-w-[300px] py-2 font-medium">{r.title}</td>
                  <td className="py-2 font-mono">{r.asset}</td>
                  <td className="py-2 text-muted-foreground">{r.kind}</td>
                  <td className="py-2">{r.author}</td>
                  <td className={cn("py-2 font-mono", r.age > 21 && "text-[color:var(--alarm)]")}>{r.age} d</td>
                  <td className="py-2">
                    <span
                      className={cn(
                        "font-semibold",
                        r.risk === "High" && "text-[color:var(--alarm)]",
                        r.risk === "Medium" && "text-[color:var(--warn)]",
                        r.risk === "Low" && "text-muted-foreground",
                      )}
                    >
                      {r.risk}
                    </span>
                  </td>
                  <td className="py-2">
                    {decisions[r.id] ? (
                      <span
                        className={cn(
                          "font-semibold",
                          decisions[r.id] === "approved"
                            ? "text-[color:var(--ok)]"
                            : "text-[color:var(--warn)]",
                        )}
                      >
                        {decisions[r.id] === "approved" ? "Verified" : "Returned"}
                      </span>
                    ) : (
                      <span className="text-muted-foreground">Pending</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>

        <div className="space-y-4">
          <Panel title="Submission detail">
            <div className="font-mono text-[12px] text-muted-foreground">{active.id}</div>
            <h3 className="mt-1 text-[15px] font-semibold">{active.title}</h3>
            <dl className="mt-3 grid grid-cols-2 gap-px border border-border bg-border text-[13px]">
              {[
                ["Asset", active.asset],
                ["Type", active.kind],
                ["Author", active.author],
                ["Submitted", active.submitted],
                ["Risk class", active.risk],
                ["Reviewer", "Reliability Engineer"],
              ].map(([k, v]) => (
                <div key={k} className="bg-surface px-3 py-2">
                  <dt className="label-caps text-muted-foreground">{k}</dt>
                  <dd>{v}</dd>
                </div>
              ))}
            </dl>
            <div className="mt-3">
              <div className="label-caps text-muted-foreground">Verification checklist</div>
              <ul className="mt-1.5 space-y-1.5 text-[13.5px]">
                {[
                  "Claim is supported by data or a documented event",
                  "Does not conflict with an existing verified lesson",
                  "Safety and operating envelope impact assessed",
                  "Correct asset and discipline owner assigned",
                ].map((c) => (
                  <li key={c} className="flex items-start gap-2">
                    <input type="checkbox" className="mt-1" defaultChecked />
                    <span>{c}</span>
                  </li>
                ))}
              </ul>
            </div>
            <textarea
              rows={3}
              placeholder="Reviewer note (recorded in the audit trail)…"
              className="mt-3 w-full border border-input bg-background p-2.5 text-[13.5px] focus:outline-none focus:ring-1 focus:ring-ring"
            />
            <div className="mt-3 flex flex-wrap gap-2">
              <Btn variant="primary" onClick={() => decide(active.id, "approved")}>
                Approve & publish
              </Btn>
              <Btn onClick={() => decide(active.id, "returned")}>Return to author</Btn>
              <Link
                to="/equipment/$tag"
                params={{ tag: active.asset }}
                className="inline-flex h-8 items-center rounded-sm px-3 text-[12.5px] font-semibold text-[color:var(--info)] hover:underline"
              >
                View asset page →
              </Link>
            </div>
          </Panel>

          <Panel title="Governance audit trail">
            <ol className="space-y-2 text-[12.5px] text-muted-foreground">
              {[
                ["09-06 11:02", "OL-4471 verified by R. Okonkwo (Rotating Equipment)"],
                ["09-05 15:20", "DOC-2410 returned — decoke step 7 conflicts with ENG-STD-014"],
                ["09-04 09:45", "TS-0912 escalated to Process Engineering authority"],
                ["09-02 13:31", "Coverage report issued to unit managers"],
              ].map(([t, e]) => (
                <li key={t}>
                  <span className="font-mono text-foreground">{t}</span> — {e}
                </li>
              ))}
            </ol>
          </Panel>
        </div>
      </div>
    </Shell>
  );
}
