import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate } from "@tanstack/react-router";
import { ChevronDown, LogOut, Search, UserRound, X } from "lucide-react";
import { equipment, failureMemory, workOrders } from "@/data/veritas";

type SearchResult = {
  id: string;
  title: string;
  detail: string;
  category: string;
  assetTag?: string;
  route: "asset" | "review" | "troubleshooting";
};

type UserProfile = {
  name: string;
  email: string;
  role: string;
};

const SESSION_KEY = "veritas.workspace-profile.v1";

const DEFAULT_PROFILE: UserProfile = {
  name: "Reliability Engineer",
  email: "engineer@veritas.local",
  role: "Reliability Engineer",
};

const roleOptions = [
  "Reliability Engineer",
  "Maintenance Engineer",
  "Operations Engineer",
  "Knowledge Reviewer",
];

function findSearchResults(query: string): SearchResult[] {
  const term = query.trim().toLowerCase();
  const results: SearchResult[] = [];

  for (const asset of equipment) {
    const text = `${asset.tag} ${asset.name} ${asset.type} ${asset.area}`.toLowerCase();
    if (!term || text.includes(term)) {
      results.push({
        id: `asset-${asset.tag}`,
        title: `${asset.tag} · ${asset.name}`,
        detail: `${asset.type} · ${asset.area}`,
        category: "Equipment",
        assetTag: asset.tag,
        route: "asset",
      });
    }
  }

  if (term) {
    for (const order of workOrders) {
      const text = [
        order.woNumber,
        order.notificationNo,
        order.equipmentTag,
        order.equipmentName,
        order.problemDescription,
        order.rootCause,
        order.correctiveAction,
      ]
        .join(" ")
        .toLowerCase();
      if (text.includes(term)) {
        results.push({
          id: `work-order-${order.woNumber}`,
          title: `${order.woNumber} · ${order.problemDescription}`,
          detail: `${order.equipmentTag} · ${order.reportDate} · ${order.status}`,
          category: "Work order",
          assetTag: order.equipmentTag,
          route: "asset",
        });
      }
    }

    for (const memory of failureMemory) {
      const text = [
        memory.equipmentTag,
        memory.repeatedIssuePattern,
        memory.previousWO,
        memory.previousRCA,
        memory.previousCorrectiveAction,
        memory.laterWO,
        memory.laterSimilarRelatedEvent,
        memory.whyFailureMemoryCouldHelp,
      ]
        .join(" ")
        .toLowerCase();
      if (text.includes(term)) {
        results.push({
          id: `failure-memory-${memory.equipmentTag}-${memory.previousWO}-${memory.laterWO}`,
          title: memory.repeatedIssuePattern,
          detail: `${memory.equipmentTag} · ${memory.previousWO} → ${memory.laterWO}`,
          category: "Failure memory",
          route: "review",
        });
      }
    }
  }

  return results.slice(0, 7);
}

function readSession(): UserProfile | null | undefined {
  try {
    const value = window.sessionStorage.getItem(SESSION_KEY);
    if (value === "signed-out") return null;
    if (!value) return undefined;
    const profile: unknown = JSON.parse(value);
    if (
      typeof profile === "object" &&
      profile !== null &&
      "name" in profile &&
      "email" in profile &&
      "role" in profile &&
      typeof profile.name === "string" &&
      typeof profile.email === "string" &&
      typeof profile.role === "string"
    ) {
      return {
        name: profile.name,
        email: profile.email,
        role: profile.role,
      };
    }
    window.sessionStorage.removeItem(SESSION_KEY);
    return undefined;
  } catch (error) {
    console.error("Could not read the Veritas workspace profile.", error);
    return undefined;
  }
}

export function WorkspaceHeader() {
  const [query, setQuery] = useState("");
  const [searchOpen, setSearchOpen] = useState(false);
  const [profile, setProfile] = useState<UserProfile | null>(DEFAULT_PROFILE);
  const [profileOpen, setProfileOpen] = useState(false);
  const [profileEditorOpen, setProfileEditorOpen] = useState(false);
  const [authError, setAuthError] = useState("");
  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [role, setRole] = useState(DEFAULT_PROFILE.role);
  const searchInput = useRef<HTMLInputElement>(null);
  const searchContainer = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  const results = useMemo(() => findSearchResults(query), [query]);

  useEffect(() => {
    const savedProfile = readSession();
    if (savedProfile === null) {
      setProfile(null);
    } else if (savedProfile) {
      setProfile(savedProfile);
    } else {
      window.sessionStorage.setItem(SESSION_KEY, JSON.stringify(DEFAULT_PROFILE));
      setProfile(DEFAULT_PROFILE);
    }
  }, []);

  useEffect(() => {
    const handleShortcut = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        searchInput.current?.focus();
        setSearchOpen(true);
      }
      if (event.key === "Escape") {
        setSearchOpen(false);
        setProfileOpen(false);
        setProfileEditorOpen(false);
      }
    };
    const handleOutsideClick = (event: MouseEvent) => {
      if (searchContainer.current && !searchContainer.current.contains(event.target as Node)) {
        setSearchOpen(false);
      }
    };
    window.addEventListener("keydown", handleShortcut);
    document.addEventListener("mousedown", handleOutsideClick);
    return () => {
      window.removeEventListener("keydown", handleShortcut);
      document.removeEventListener("mousedown", handleOutsideClick);
    };
  }, []);

  const signOut = () => {
    window.sessionStorage.setItem(SESSION_KEY, "signed-out");
    setProfile(null);
    setProfileOpen(false);
  };

  const saveProfile = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const normalizedEmail = email.trim().toLowerCase();
    const normalizedName = displayName.trim();
    if (!normalizedEmail || !normalizedName) {
      setAuthError("Enter your name and work email to save the profile.");
      return;
    }
    const nextProfile = { name: normalizedName, email: normalizedEmail, role };
    window.sessionStorage.setItem(SESSION_KEY, JSON.stringify(nextProfile));
    setProfile(nextProfile);
    setProfileEditorOpen(false);
    setAuthError("");
  };

  const openProfileEditor = () => {
    setProfileOpen(false);
    setAuthError("");
    setEmail(profile?.email ?? "");
    setDisplayName(profile?.name ?? "");
    setRole(profile?.role ?? DEFAULT_PROFILE.role);
    setProfileEditorOpen(true);
  };

  const closeSearch = () => {
    setSearchOpen(false);
    setQuery("");
  };

  return (
    <>
      <header className="sticky top-0 z-30 bg-navy text-navy-foreground">
        <div className="flex min-h-14 items-center gap-3 border-b border-navy-line/60 px-4 md:gap-6 md:px-6">
          <Link to="/" className="flex shrink-0 items-center gap-2.5">
            <span className="flex h-7 w-7 items-center justify-center rounded bg-signal text-signal-foreground shadow-sm">
              <svg viewBox="0 0 24 24" className="h-4 w-4 fill-current">
                <path d="M4 4h4.5l3.5 11 3.5-11H20l-6.5 16h-3z" />
              </svg>
            </span>
            <span className="text-base font-bold tracking-[0.18em]">VERITAS</span>
            <span className="hidden border-l border-navy-line pl-2.5 text-[11px] leading-tight text-navy-foreground/60 lg:block">
              Engineering Verification Platform
              <br />
              Industrial Asset Reliability · Engineering Operations
            </span>
          </Link>

          <nav className="ml-1 hidden h-14 items-stretch lg:flex">
            <Link
              to="/"
              activeOptions={{ exact: true }}
              className="flex items-center border-b-2 border-transparent px-3 text-[13px] font-medium text-navy-foreground/70 hover:text-navy-foreground data-[status=active]:border-signal data-[status=active]:text-navy-foreground"
            >
              Equipment
            </Link>
            <Link
              to="/equipment/$tag"
              params={{ tag: "EA-5601" }}
              className="flex items-center border-b-2 border-transparent px-3 text-[13px] font-medium text-navy-foreground/70 hover:text-navy-foreground data-[status=active]:border-signal data-[status=active]:text-navy-foreground"
            >
              Asset 360
            </Link>
            <Link
              to="/troubleshooting"
              className="flex items-center border-b-2 border-transparent px-3 text-[13px] font-medium text-navy-foreground/70 hover:text-navy-foreground data-[status=active]:border-signal data-[status=active]:text-navy-foreground"
            >
              Troubleshooting
            </Link>
            <Link
              to="/review"
              className="flex items-center border-b-2 border-transparent px-3 text-[13px] font-medium text-navy-foreground/70 hover:text-navy-foreground data-[status=active]:border-signal data-[status=active]:text-navy-foreground"
            >
              Knowledge Review
            </Link>
          </nav>

          <div className="ml-auto flex min-w-0 items-center gap-2 md:gap-3">
            <div className="relative min-w-0" ref={searchContainer}>
              <div className="flex h-9 w-32 items-center border border-navy-line/70 px-2.5 transition-all focus-within:border-signal sm:w-48 md:w-56">
                <Search aria-hidden="true" className="h-4 w-4 shrink-0 text-navy-foreground/50" />
                <input
                  ref={searchInput}
                  aria-label="Search equipment, work orders, and failure memories"
                  aria-expanded={searchOpen}
                  aria-controls="global-search-results"
                  role="combobox"
                  aria-autocomplete="list"
                  value={query}
                  onFocus={() => setSearchOpen(true)}
                  onChange={(event) => {
                    setQuery(event.target.value);
                    setSearchOpen(true);
                  }}
                  onKeyDown={(event) => {
                    if (event.key === "Escape") closeSearch();
                    if (event.key === "Enter" && results[0]) {
                      event.preventDefault();
                      const result = results[0];
                      setSearchOpen(false);
                      setQuery("");
                      if (result.route === "asset" && result.assetTag) {
                        void navigate({ to: "/equipment/$tag", params: { tag: result.assetTag } });
                      } else if (result.route === "review") {
                        void navigate({ to: "/review" });
                      } else {
                        void navigate({ to: "/troubleshooting" });
                      }
                    }
                  }}
                  placeholder="Search equipment or records…"
                  className="ml-2 min-w-0 flex-1 bg-transparent text-[12px] text-navy-foreground placeholder:text-navy-foreground/40 focus:outline-none"
                />
                {query && (
                  <button
                    type="button"
                    onClick={closeSearch}
                    aria-label="Clear search"
                    className="ml-1 text-navy-foreground/50 hover:text-navy-foreground"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                )}
              </div>
              {searchOpen && (
                <div
                  id="global-search-results"
                  role="listbox"
                  className="absolute right-0 top-11 z-50 max-h-[min(70vh,32rem)] w-[min(92vw,26rem)] overflow-y-auto border border-border bg-surface text-foreground shadow-xl"
                >
                  <div className="border-b border-border px-3 py-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                    {query.trim() ? `Search results · ${results.length}` : "Quick access"}
                  </div>
                  {results.length ? (
                    results.map((item) => (
                      <SearchResultLink key={item.id} result={item} onSelect={closeSearch} />
                    ))
                  ) : (
                    <div className="px-3 py-6 text-center text-[12px] text-muted-foreground">
                      No matching equipment or records. Try an asset tag, work order, or symptom.
                    </div>
                  )}
                  <div className="border-t border-border px-3 py-2 text-[10px] text-muted-foreground">
                    Search includes equipment, work orders, and failure memories
                  </div>
                </div>
              )}
            </div>

            {profile ? (
              <div className="relative">
                <button
                  type="button"
                  aria-haspopup="menu"
                  aria-expanded={profileOpen}
                  onClick={() => setProfileOpen((open) => !open)}
                  className="flex items-center gap-2 border-l border-navy-line/60 pl-2.5 text-left hover:text-white md:pl-3"
                >
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-navy-line font-mono text-[11px] font-semibold">
                    {profile.name
                      .split(/\s+/)
                      .map((part) => part[0])
                      .join("")
                      .slice(0, 2)
                      .toUpperCase()}
                  </span>
                  <span className="hidden max-w-36 md:block">
                    <span className="block truncate text-[12px] font-medium">{profile.name}</span>
                    <span className="block text-[10px] text-navy-foreground/50">
                      {profile.role}
                    </span>
                  </span>
                  <ChevronDown className="hidden h-3.5 w-3.5 text-navy-foreground/60 sm:block" />
                </button>
                {profileOpen && (
                  <div
                    role="menu"
                    className="absolute right-0 top-11 z-50 w-64 border border-border bg-surface p-2 text-foreground shadow-xl"
                  >
                    <div className="border-b border-border px-2 pb-3 pt-1">
                      <div className="font-semibold">{profile.name}</div>
                      <div className="mt-0.5 truncate text-[11px] text-muted-foreground">
                        {profile.email}
                      </div>
                      <div className="mt-2 inline-flex items-center gap-1 rounded-sm bg-amber-50 px-1.5 py-1 text-[10px] font-medium text-amber-800">
                        Browser-tab profile
                      </div>
                    </div>
                    <button
                      type="button"
                      role="menuitem"
                      onClick={openProfileEditor}
                      className="mt-1 flex w-full items-center gap-2 px-2 py-2 text-left text-[12px] hover:bg-secondary"
                    >
                      <UserRound className="h-4 w-4" /> Edit workspace profile
                    </button>
                    <button
                      type="button"
                      role="menuitem"
                      onClick={signOut}
                      className="flex w-full items-center gap-2 px-2 py-2 text-left text-[12px] text-red-700 hover:bg-red-50"
                    >
                      <LogOut className="h-4 w-4" /> Clear profile
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <button
                type="button"
                onClick={openProfileEditor}
                className="h-9 shrink-0 border border-signal px-3 text-[12px] font-semibold text-navy-foreground hover:bg-signal hover:text-signal-foreground"
              >
                Set profile
              </button>
            )}
          </div>
        </div>
      </header>

      {profileEditorOpen && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/55 p-4"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) setProfileEditorOpen(false);
          }}
        >
          <section
            aria-labelledby="workspace-profile-title"
            aria-modal="true"
            role="dialog"
            className="w-full max-w-md border border-border bg-surface p-6 text-foreground shadow-2xl"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-navy text-navy-foreground">
                  <UserRound className="h-5 w-5" />
                </div>
                <h2 id="workspace-profile-title" className="mt-4 text-xl font-bold">
                  Workspace profile
                </h2>
                <p className="mt-1 text-[12px] text-muted-foreground">
                  Set the name and role shown in this workspace.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setProfileEditorOpen(false)}
                aria-label="Close workspace profile"
                className="p-1 text-muted-foreground hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={saveProfile} className="mt-5 space-y-3">
              <label className="block text-[12px] font-medium">
                Display name
                <input
                  type="text"
                  autoComplete="name"
                  required
                  value={displayName}
                  onChange={(event) => setDisplayName(event.target.value)}
                  placeholder="Your name"
                  className="mt-1.5 h-10 w-full border border-input bg-background px-3 text-[13px] font-normal outline-none focus:border-signal focus:ring-1 focus:ring-signal"
                />
              </label>
              <label className="block text-[12px] font-medium">
                Work email
                <input
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="name@company.com"
                  className="mt-1.5 h-10 w-full border border-input bg-background px-3 text-[13px] font-normal outline-none focus:border-signal focus:ring-1 focus:ring-signal"
                />
              </label>
              <label className="block text-[12px] font-medium">
                Workspace role
                <select
                  value={role}
                  onChange={(event) => setRole(event.target.value)}
                  className="mt-1.5 h-10 w-full border border-input bg-background px-3 text-[13px] font-normal outline-none focus:border-signal"
                >
                  {roleOptions.map((option) => (
                    <option key={option}>{option}</option>
                  ))}
                </select>
              </label>
              {authError && (
                <p role="alert" className="text-[12px] text-red-700">
                  {authError}
                </p>
              )}
              <button
                type="submit"
                className="mt-1 inline-flex h-10 w-full items-center justify-center bg-signal px-4 text-[13px] font-semibold text-signal-foreground hover:brightness-95"
              >
                Save profile
              </button>
            </form>

            <div className="mt-4 border border-amber-200 bg-amber-50 p-3 text-[11px] leading-relaxed text-amber-950">
              Profile details stay in this browser tab and personalize the interface only. No
              account credentials are requested or stored.
            </div>
          </section>
        </div>
      )}
    </>
  );
}

function SearchResultLink({ result, onSelect }: { result: SearchResult; onSelect: () => void }) {
  const className =
    "block w-full border-b border-border/70 px-3 py-2.5 text-left last:border-0 hover:bg-secondary focus:bg-secondary focus:outline-none";
  const content = (
    <>
      <span className="flex items-center justify-between gap-3">
        <span className="line-clamp-1 text-[12px] font-medium">{result.title}</span>
        <span className="shrink-0 text-[9px] font-semibold uppercase tracking-wider text-muted-foreground">
          {result.category}
        </span>
      </span>
      <span className="mt-0.5 block truncate text-[10.5px] text-muted-foreground">
        {result.detail}
      </span>
    </>
  );

  if (result.route === "asset" && result.assetTag) {
    return (
      <Link
        role="option"
        aria-selected="false"
        to="/equipment/$tag"
        params={{ tag: result.assetTag }}
        onClick={onSelect}
        className={className}
      >
        {content}
      </Link>
    );
  }
  if (result.route === "review") {
    return (
      <Link
        role="option"
        aria-selected="false"
        to="/review"
        onClick={onSelect}
        className={className}
      >
        {content}
      </Link>
    );
  }
  return (
    <Link
      role="option"
      aria-selected="false"
      to="/troubleshooting"
      onClick={onSelect}
      className={className}
    >
      {content}
    </Link>
  );
}
