import type { ReactNode } from "react";
import { cn } from "@/lib/utils";
import type { VerifyState } from "@/data/veritas";
import { WorkspaceHeader } from "@/components/veritas/WorkspaceHeader";

export function Shell({
  children,
  breadcrumb,
  title,
  subtitle,
  actions,
}: {
  children: ReactNode;
  breadcrumb: string[];
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <WorkspaceHeader />

      <div className="border-b border-border bg-surface">
        <div className="flex flex-wrap items-end justify-between gap-4 px-6 py-4">
          <div>
            <nav className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
              {breadcrumb.map((b, i) => (
                <span key={b} className="flex items-center gap-1.5">
                  {i > 0 && <span className="text-border">/</span>}
                  <span className={i === breadcrumb.length - 1 ? "text-foreground" : ""}>{b}</span>
                </span>
              ))}
            </nav>
            <h1 className="mt-1 text-[22px] font-bold">{title}</h1>
            {subtitle && <p className="mt-0.5 text-[13px] text-muted-foreground">{subtitle}</p>}
          </div>
          {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
        </div>
      </div>

      <main className="px-6 py-5">{children}</main>

      <footer className="mt-8 border-t border-border px-6 py-4 text-[11px] text-muted-foreground">
        VERITAS 4.2 · Knowledge governed under ENG-STD-014 · Records retained 25 years · Internal
        use only
      </footer>
    </div>
  );
}

export function Btn({
  children,
  variant = "default",
  className,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "default" | "primary" | "ghost" }) {
  return (
    <button
      {...props}
      className={cn(
        "inline-flex h-8 items-center gap-1.5 rounded-sm px-3 text-[12.5px] font-semibold transition-colors",
        variant === "primary" && "bg-signal text-signal-foreground hover:brightness-95",
        variant === "default" &&
          "border border-border bg-surface text-foreground hover:bg-secondary",
        variant === "ghost" && "text-muted-foreground hover:bg-secondary hover:text-foreground",
        className,
      )}
    >
      {children}
    </button>
  );
}

export function Panel({
  title,
  right,
  children,
  className,
}: {
  title: string;
  right?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={cn("border border-border bg-surface", className)}>
      <header className="flex items-center justify-between gap-3 border-b border-border bg-surface-2 px-4 py-2.5">
        <h2 className="label-caps text-foreground">{title}</h2>
        {right}
      </header>
      <div className="p-4">{children}</div>
    </section>
  );
}

export function StateTag({ state }: { state: VerifyState }) {
  const map = {
    verified: { label: "Verified", cls: "border-[color:var(--ok)] text-[color:var(--ok)]" },
    review: { label: "In Review", cls: "border-[color:var(--warn)] text-[color:var(--warn)]" },
    draft: { label: "Unverified", cls: "border-border text-muted-foreground" },
  }[state];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 border px-1.5 py-0.5 text-[10.5px] font-semibold uppercase tracking-wide",
        map.cls,
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {map.label}
    </span>
  );
}

export function Crit({ level }: { level: "A" | "B" | "C" }) {
  return (
    <span
      className={cn(
        "inline-flex h-5 w-5 items-center justify-center font-mono text-[11px] font-bold",
        level === "A" && "bg-[color:var(--alarm)] text-white",
        level === "B" && "bg-signal text-signal-foreground",
        level === "C" && "bg-secondary text-secondary-foreground",
      )}
      title={`Criticality ${level}`}
    >
      {level}
    </span>
  );
}

export function Meter({ value }: { value: number }) {
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-20 bg-secondary">
        <div
          className={cn(
            "h-full",
            value >= 80
              ? "bg-[color:var(--ok)]"
              : value >= 55
                ? "bg-[color:var(--warn)]"
                : "bg-[color:var(--alarm)]",
          )}
          style={{ width: `${value}%` }}
        />
      </div>
      <span className="font-mono text-[11.5px] text-muted-foreground">{value}%</span>
    </div>
  );
}
