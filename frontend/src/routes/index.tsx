import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { compactIDR, equipment, workOrders } from "@/data/veritas";
import { Btn, Crit, Meter, Shell, StateTag } from "@/components/veritas/Shell";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/")({
  head: () => ({ meta: [
    { title: "Equipment Library — VERITAS Engineering Knowledge" },
    { name: "description", content: "Explore 211 actual maintenance work orders and sequenced Failure Memory evidence across the LLDPE unit." },
    { property: "og:title", content: "Equipment Library — VERITAS" },
    { property: "og:description", content: "Actual maintenance history and reusable failure evidence for LLDPE equipment." },
    { property: "og:type", content: "website" }, { name: "twitter:card", content: "summary" },
  ]}),
  component: Library,
});

const areas = ["All areas", ...Array.from(new Set(equipment.map((e) => e.area)))];

function Library() {
  const [q, setQ] = useState("");
  const [area, setArea] = useState(areas[0]);
  const [memoryOnly, setMemoryOnly] = useState(false);
  const rows = useMemo(() => equipment.filter((e) => {
    const text = `${e.tag} ${e.name} ${e.type} ${e.area}`.toLowerCase();
    return (!q || text.includes(q.toLowerCase())) && (area === areas[0] || e.area === area) && (!memoryOnly || e.memoryCount > 0);
  }), [q, area, memoryOnly]);
  const totalOrders = equipment.reduce((n, e) => n + e.workOrderCount, 0);
  const totalDowntime = equipment.reduce((n, e) => n + e.downtimeHours, 0);
  const totalCost = equipment.reduce((n, e) => n + e.totalCostIDR, 0);

  const handleExportRegister = () => {
    const headers = [
      "Tag",
      "Equipment Name",
      "Type",
      "Area",
      "Criticality",
      "Work Orders",
      "Breakdowns",
      "Recorded Downtime (h)",
      "Recorded Total Cost (IDR)",
      "Failure Memory Links",
      "Coverage %",
    ];
    const csvRows = rows.map((e) => [
      `"${e.tag}"`,
      `"${e.name.replace(/"/g, '""')}"`,
      `"${e.type.replace(/"/g, '""')}"`,
      `"${e.area.replace(/"/g, '""')}"`,
      `"${workOrders.find((w) => w.equipmentTag === e.tag)?.criticality || "NON CRITICAL"}"`,
      e.workOrderCount,
      e.breakdownCount,
      e.downtimeHours,
      e.totalCostIDR,
      e.memoryCount,
      `"${e.coverage}%"`,
    ]);
    const csvContent = [headers.join(","), ...csvRows.map((r) => r.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `veritas_equipment_register_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return <Shell breadcrumb={["LLDPE Unit", "Equipment Library"]} title="Equipment Library" subtitle="Actual work-order sequences and reusable failure evidence from the uploaded maintenance dataset." actions={<><Btn onClick={handleExportRegister}>Export register</Btn><Link to="/equipment/$tag" params={{ tag: "EA-5601" }} className="inline-flex h-8 items-center bg-signal px-3 text-[12.5px] font-semibold text-signal-foreground">Open EA-5601</Link></>}>
    <div className="grid grid-cols-2 gap-px border border-border bg-border lg:grid-cols-4">
      {[["Assets in dataset", equipment.length, "8 tagged equipment records"], ["Work orders", totalOrders, "2024-06 to 2025-12"], ["Recorded downtime", `${totalDowntime} h`, "Across all sequences"], ["Maintenance value", compactIDR(totalCost), "Recorded total cost"]].map(([label,value,note]) => <div key={label} className="bg-surface px-4 py-3"><div className="label-caps text-muted-foreground">{label}</div><div className="mt-1 font-mono text-2xl font-bold">{value}</div><div className="text-[11.5px] text-muted-foreground">{note}</div></div>)}
    </div>
    <div className="mt-5 flex flex-wrap items-center gap-2 border border-border bg-surface px-3 py-2.5">
      <input value={q} onChange={(e)=>setQ(e.target.value)} placeholder="Filter tag, equipment, type or area…" className="h-8 w-80 border border-input bg-background px-2.5 text-[13px] focus:outline-none focus:ring-1 focus:ring-ring" />
      <select value={area} onChange={(e)=>setArea(e.target.value)} className="h-8 max-w-80 border border-input bg-background px-2 text-[13px]">{areas.map((a)=><option key={a}>{a}</option>)}</select>
      <label className="flex items-center gap-2 text-[12.5px] text-muted-foreground"><input type="checkbox" checked={memoryOnly} onChange={(e)=>setMemoryOnly(e.target.checked)} />Failure Memory only</label>
      <span className="ml-auto font-mono text-[12px] text-muted-foreground">{rows.length} / {equipment.length} assets</span>
    </div>
    <div className="mt-3 overflow-x-auto border border-border bg-surface"><table className="w-full border-collapse text-[13px]"><thead><tr className="bg-navy text-navy-foreground">{["Tag","Equipment / Area","Criticality","Work orders","Breakdowns","Recorded downtime","Recorded maintenance cost","Memory","Coverage",""] .map(h=><th key={h} className="label-caps whitespace-nowrap px-3 py-2 text-left font-semibold">{h}</th>)}</tr></thead><tbody>
      {rows.map((e,i)=><tr key={e.tag} className={cn("border-t border-border hover:bg-accent/40",i%2&&"bg-surface-2/60",e.tag==="EA-5601"&&"border-l-4 border-l-signal bg-accent/60")}>
        <td className="px-3 py-2 font-mono font-semibold"><Link to="/equipment/$tag" params={{tag:e.tag}} className="hover:underline">{e.tag}</Link>{e.tag==="EA-5601"&&<div className="mt-1 text-[9px] font-bold uppercase text-[color:var(--warn)]">Focus asset</div>}</td>
        <td className="px-3 py-2"><div className="font-medium">{e.name}</div><div className="text-[11.5px] text-muted-foreground">{e.type} · {e.area}</div></td><td className="px-3 py-2"><span className="whitespace-nowrap text-[11.5px] font-semibold uppercase">{workOrders.find(w=>w.equipmentTag===e.tag)?.criticality}</span></td><td className="px-3 py-2 font-mono">{e.workOrderCount}</td><td className="px-3 py-2 font-mono">{e.breakdownCount}</td><td className="px-3 py-2 font-mono">{e.downtimeHours} h</td><td className="px-3 py-2 font-mono">{compactIDR(e.totalCostIDR)}</td><td className="px-3 py-2"><span className={cn("font-mono font-semibold",e.memoryCount?"text-[color:var(--ok)]":"text-muted-foreground")}>{e.memoryCount}</span></td><td className="px-3 py-2"><Meter value={e.coverage}/></td><td className="px-3 py-2 text-right whitespace-nowrap"><Link to="/equipment/$tag" params={{tag:e.tag}} className="font-semibold text-[color:var(--info)] hover:underline">Open →</Link><Link to="/troubleshooting" search={{ asset: e.tag }} className="ml-3 inline-flex items-center gap-1 font-mono text-[11px] font-semibold text-signal hover:underline">Troubleshoot ⚡</Link></td>
      </tr>)}
    </tbody></table></div>
    <p className="mt-2 text-[11.5px] text-muted-foreground">Source: VERITAS Data by Eve — WO Sequence and Failure Memory. Evidence flags are not savings or addressability claims.</p>
  </Shell>;
}