import html
from datetime import datetime

import streamlit as st

from src.ingest import load_documents
from src.investigator import investigate
from src.meta_client import model_is_configured, get_model_name
from src.verifier import get_document_statuses


# ---------------------------------------------------------
# Page config
# ---------------------------------------------------------
st.set_page_config(
    page_title="Veritas — Engineering Verification",
    page_icon="V",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------
# Styling
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --vm-bg: #f6f7f9;
        --vm-card: #ffffff;
        --vm-text: #15181d;
        --vm-muted: #68707d;
        --vm-border: #e3e6ea;
        --vm-accent: #b42318;
        --vm-accent-soft: #fff2f0;
        --vm-success: #16794a;
        --vm-success-soft: #eef9f3;
        --vm-warning: #9a6700;
        --vm-warning-soft: #fff8e6;
        --vm-dark: #191d22;
    }

    html, body, [class*="css"] {
        font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .stApp {
        background: var(--vm-bg);
        color: var(--vm-text);
    }

    /* Reduce Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    .block-container {
        max-width: 1460px;
        padding-top: 1rem;
        padding-bottom: 3rem;
    }

    /* Header */
    .vm-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #fff;
        border: 1px solid var(--vm-border);
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 16px;
        box-shadow: 0 1px 2px rgba(16,24,40,.03);
    }

    .vm-brand-wrap {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .vm-logo {
        width: 36px;
        height: 36px;
        border-radius: 9px;
        background: var(--vm-dark);
        color: #fff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        letter-spacing: -.5px;
    }

    .vm-brand {
        font-size: 18px;
        font-weight: 750;
        line-height: 1.05;
    }

    .vm-subbrand {
        font-size: 11px;
        color: var(--vm-muted);
        margin-top: 2px;
        letter-spacing: .04em;
        text-transform: uppercase;
    }

    .vm-header-meta {
        font-size: 12px;
        color: var(--vm-muted);
        text-align: right;
    }

    .vm-breadcrumb {
        color: var(--vm-muted);
        font-size: 12px;
        margin: 6px 0 6px 2px;
    }

    .vm-title-row {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        margin-bottom: 14px;
    }

    .vm-title {
        font-size: 31px;
        font-weight: 760;
        letter-spacing: -.025em;
        margin: 0;
    }

    .vm-subtitle {
        color: var(--vm-muted);
        font-size: 14px;
        margin-top: 5px;
    }

    /* Cards */
    .vm-card {
        background: var(--vm-card);
        border: 1px solid var(--vm-border);
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 1px 2px rgba(16,24,40,.025);
    }

    .vm-card-title {
        font-size: 13px;
        font-weight: 720;
        color: var(--vm-text);
        margin-bottom: 10px;
    }

    .vm-card-muted {
        color: var(--vm-muted);
        font-size: 12px;
    }

    .vm-metric {
        background: #fff;
        border: 1px solid var(--vm-border);
        border-radius: 12px;
        padding: 14px 15px;
        min-height: 86px;
    }

    .vm-metric-label {
        color: var(--vm-muted);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: .06em;
        font-weight: 650;
    }

    .vm-metric-value {
        font-size: 23px;
        font-weight: 760;
        margin-top: 8px;
        letter-spacing: -.02em;
    }

    .vm-metric-foot {
        font-size: 11px;
        color: var(--vm-muted);
        margin-top: 2px;
    }

    /* Badges */
    .vm-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        border-radius: 999px;
        padding: 5px 9px;
        font-size: 11px;
        font-weight: 700;
        border: 1px solid transparent;
    }

    .vm-badge-success {
        color: var(--vm-success);
        background: var(--vm-success-soft);
        border-color: #ccebd9;
    }

    .vm-badge-warning {
        color: var(--vm-warning);
        background: var(--vm-warning-soft);
        border-color: #f2dfae;
    }

    .vm-badge-danger {
        color: var(--vm-accent);
        background: var(--vm-accent-soft);
        border-color: #f0c7c2;
    }

    .vm-badge-neutral {
        color: #49515b;
        background: #f5f6f7;
        border-color: #e1e4e8;
    }

    /* Stepper */
    .vm-stepper {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin: 8px 0 16px;
    }

    .vm-step {
        background: #fff;
        border: 1px solid var(--vm-border);
        border-radius: 10px;
        padding: 11px 12px;
        color: var(--vm-muted);
        font-size: 12px;
        font-weight: 650;
    }

    .vm-step-active {
        color: var(--vm-text);
        border-color: #b9bec5;
        box-shadow: inset 0 -2px 0 var(--vm-dark);
    }

    .vm-step-done {
        color: var(--vm-success);
        background: var(--vm-success-soft);
        border-color: #ccebd9;
    }

    /* Evidence table-like rows */
    .vm-evidence-row {
        display: grid;
        grid-template-columns: 1.2fr .9fr .7fr .55fr;
        gap: 10px;
        align-items: center;
        padding: 11px 0;
        border-top: 1px solid var(--vm-border);
        font-size: 12px;
    }

    .vm-evidence-head {
        color: var(--vm-muted);
        text-transform: uppercase;
        letter-spacing: .05em;
        font-size: 10px;
        font-weight: 700;
        border-top: 0;
        padding-top: 2px;
    }

    .vm-source {
        font-weight: 700;
        color: var(--vm-text);
    }

    /* Conflict panel */
    .vm-conflict {
        border: 1px solid #efc5bf;
        background: #fff9f8;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
    }

    .vm-conflict-title {
        color: var(--vm-accent);
        font-size: 12px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .06em;
        margin-bottom: 7px;
    }

    .vm-conflict-body {
        color: #3a3f45;
        font-size: 13px;
        line-height: 1.55;
    }

    .vm-delta {
        display: grid;
        grid-template-columns: 1fr 36px 1fr;
        gap: 8px;
        align-items: center;
        margin-top: 12px;
    }

    .vm-delta-box {
        background: #fff;
        border: 1px solid var(--vm-border);
        border-radius: 10px;
        padding: 10px;
    }

    .vm-delta-label {
        color: var(--vm-muted);
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: .05em;
    }

    .vm-delta-value {
        font-size: 18px;
        font-weight: 760;
        margin-top: 3px;
    }

    /* Activity */
    .vm-activity {
        display: grid;
        grid-template-columns: 78px 1fr;
        gap: 10px;
        padding: 10px 0;
        border-top: 1px solid var(--vm-border);
        font-size: 12px;
    }

    .vm-activity:first-child {border-top: 0;}
    .vm-activity-time {color: var(--vm-muted);}

    /* Streamlit components */
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stTextInput"] input {
        border-radius: 10px !important;
        border-color: var(--vm-border) !important;
        background: #fff !important;
    }

    .stButton > button {
        border-radius: 9px;
        font-weight: 700;
        min-height: 40px;
    }

    .stButton > button[kind="primary"] {
        background: var(--vm-dark);
        border-color: var(--vm-dark);
    }

    div[data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid var(--vm-border);
    }

    button[data-baseweb="tab"] {
        padding-left: 0 !important;
        padding-right: 0 !important;
        font-size: 13px !important;
        font-weight: 650 !important;
    }

    /* Hide colored Streamlit alert feel where possible */
    .stAlert {border-radius: 10px;}

    @media (max-width: 900px) {
        .vm-stepper {grid-template-columns: 1fr 1fr;}
        .vm-evidence-row {grid-template-columns: 1fr; gap: 3px;}
        .vm-title-row {display: block;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def esc(value):
    return html.escape(str(value))


def metric_card(label, value, foot=""):
    st.markdown(
        f"""
        <div class="vm-metric">
            <div class="vm-metric-label">{esc(label)}</div>
            <div class="vm-metric-value">{esc(value)}</div>
            <div class="vm-metric-foot">{esc(foot)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(text, kind="neutral"):
    return f'<span class="vm-badge vm-badge-{kind}">{esc(text)}</span>'


def infer_asset(problem):
    p = problem.upper()
    return "P-101" if "P-101" in p else "Unspecified asset"


def render_header():
    model_label = get_model_name() if model_is_configured() else "Deterministic verification mode"
    st.markdown(
        f"""
        <div class="vm-header">
            <div class="vm-brand-wrap">
                <div class="vm-logo">V</div>
                <div>
                    <div class="vm-brand">Veritas</div>
                    <div class="vm-subbrand">Engineering Verification Platform</div>
                </div>
            </div>
            <div class="vm-header-meta">
                Industrial Maintenance Demo<br/>
                {esc(model_label)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stepper(has_result=False):
    if has_result:
        classes = ["vm-step-done", "vm-step-done", "vm-step-done", "vm-step-active"]
    else:
        classes = ["vm-step-active", "", "", ""]

    labels = [
        "1 · Define problem",
        "2 · Gather evidence",
        "3 · Verify context",
        "4 · Review recommendation",
    ]
    boxes = "".join(
        f'<div class="vm-step {classes[i]}">{labels[i]}</div>' for i in range(4)
    )
    st.markdown(f'<div class="vm-stepper">{boxes}</div>', unsafe_allow_html=True)


def render_evidence_table(evidence, statuses):
    status_by_source = {s["source"]: s for s in statuses}

    st.markdown(
        """
        <div class="vm-evidence-row vm-evidence-head">
            <div>Source</div><div>Type / Context</div><div>Status</div><div>Relevance</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for doc in evidence:
        meta = status_by_source.get(doc["source"], {})
        doc_type = (meta.get("document_type") or "engineering reference").replace("_", " ").title()
        revision = meta.get("revision")
        status = meta.get("status")

        if status == "CURRENT":
            badge = status_badge("Current", "success")
        elif status == "SUPERSEDED":
            badge = status_badge("Superseded", "danger")
        elif revision:
            badge = status_badge(f"Rev {revision}", "neutral")
        else:
            badge = status_badge("Evidence", "neutral")

        st.markdown(
            f"""
            <div class="vm-evidence-row">
                <div class="vm-source">{esc(doc['source'])}</div>
                <div>{esc(doc_type)}</div>
                <div>{badge}</div>
                <div>{esc(doc['score'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_conflicts(conflicts):
    if not conflicts:
        st.markdown(status_badge("No revision conflicts detected", "success"), unsafe_allow_html=True)
        return

    for conflict in conflicts:
        old_t = conflict.get("old_tolerance") or "Not found"
        new_t = conflict.get("current_tolerance") or "Not found"
        st.markdown(
            f"""
            <div class="vm-conflict">
                <div class="vm-conflict-title">Revision conflict detected</div>
                <div class="vm-conflict-body">
                    <strong>{esc(conflict['source'])}</strong> references
                    <strong>{esc(conflict['document_id'])} Revision {esc(conflict['referenced_revision'])}</strong>,
                    while the current approved revision is
                    <strong>Revision {esc(conflict['current_revision'])}</strong>.
                </div>
                <div class="vm-delta">
                    <div class="vm-delta-box">
                        <div class="vm-delta-label">Historical tolerance</div>
                        <div class="vm-delta-value">{esc(old_t)}</div>
                    </div>
                    <div style="text-align:center;color:#8a919b;font-weight:700;">→</div>
                    <div class="vm-delta-box">
                        <div class="vm-delta-label">Current tolerance</div>
                        <div class="vm-delta-value">{esc(new_t)}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------
if "vm_result" not in st.session_state:
    st.session_state.vm_result = None

if "vm_problem" not in st.session_state:
    st.session_state.vm_problem = (
        "Pump P-101 has abnormal vibration after its coupling was replaced. "
        "What should the engineer investigate?"
    )


# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
render_header()

st.markdown(
    '<div class="vm-breadcrumb">LLDPE Unit / Rotating Equipment / P-101 / Troubleshooting</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="vm-title-row">
        <div>
            <div class="vm-title">Troubleshooting Workspace</div>
            <div class="vm-subtitle">Evidence-backed investigation with revision and applicability verification.</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

result = st.session_state.vm_result
render_stepper(has_result=result is not None)

# Top status metrics
try:
    all_docs = load_documents()
    statuses = get_document_statuses(all_docs)
except Exception:
    all_docs = []
    statuses = []

current_count = sum(1 for s in statuses if s.get("status") == "CURRENT")
superseded_count = sum(1 for s in statuses if s.get("status") == "SUPERSEDED")

m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card("Asset", infer_asset(st.session_state.vm_problem), "Rotating equipment")
with m2:
    metric_card("Evidence sources", len(all_docs), "Local engineering records")
with m3:
    metric_card("Current procedures", current_count, "Approved references")
with m4:
    metric_card("Superseded references", superseded_count, "Require verification")

st.write("")

# Workspace tabs
workspace_tab, evidence_tab, verification_tab, audit_tab = st.tabs(
    ["Investigation", "Evidence", "Verification", "Audit Trail"]
)

with workspace_tab:
    left, right = st.columns([1.55, 0.85], gap="large")

    with left:
        st.markdown('<div class="vm-card-title">Problem statement</div>', unsafe_allow_html=True)
        problem = st.text_area(
            "Observed deviation",
            value=st.session_state.vm_problem,
            height=145,
            label_visibility="collapsed",
            placeholder="Describe the abnormal condition, recent maintenance, and any known operating changes...",
        )

        upload = st.file_uploader(
            "Attach equipment image (optional)",
            type=["png", "jpg", "jpeg"],
            help="Image upload is ready for the multimodal phase; current verification uses the text evidence set.",
        )
        if upload is not None:
            st.image(upload, caption="Attached equipment image", width=320)

        run_col, clear_col = st.columns([0.35, 0.65])
        with run_col:
            run_clicked = st.button("Run verification", type="primary", use_container_width=True)
        with clear_col:
            if st.button("Reset workspace", use_container_width=True):
                st.session_state.vm_result = None
                st.session_state.vm_problem = (
                    "Pump P-101 has abnormal vibration after its coupling was replaced. "
                    "What should the engineer investigate?"
                )
                st.rerun()

        if run_clicked:
            if not problem.strip():
                st.warning("Enter an equipment problem first.")
            else:
                st.session_state.vm_problem = problem.strip()
                with st.spinner("Building evidence chain and checking revision context..."):
                    st.session_state.vm_result = investigate(problem.strip())
                st.rerun()

        st.write("")
        st.markdown('<div class="vm-card-title">Investigation recommendation</div>', unsafe_allow_html=True)

        if result:
            if result.get("used_model"):
                st.markdown(status_badge("Muse synthesis active", "success"), unsafe_allow_html=True)
            else:
                st.markdown(status_badge("Deterministic fallback", "warning"), unsafe_allow_html=True)

            st.markdown(result["recommendation"])

            if result.get("model_error"):
                with st.expander("Model connection detail"):
                    st.code(result["model_error"])
        else:
            st.markdown(
                """
                <div class="vm-card">
                    <div class="vm-card-muted">
                        Run verification to generate an evidence-backed investigation recommendation.
                        Veritas will retrieve the most relevant records, check revision status, flag conflicts,
                        and preserve source traceability.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.markdown('<div class="vm-card-title">Asset context</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="vm-card">
                <div style="font-size:18px;font-weight:760;">P-101</div>
                <div class="vm-card-muted" style="margin-top:3px;">Centrifugal Pump · Process Area A</div>
                <div style="margin-top:14px;display:flex;gap:7px;flex-wrap:wrap;">
                    {status_badge('In service', 'success')}
                    {status_badge('Verification demo', 'neutral')}
                </div>
                <div style="margin-top:15px;font-size:12px;line-height:1.8;color:#4c535c;">
                    <strong>Recent maintenance</strong><br/>Coupling replacement<br/>
                    <strong>Reported symptom</strong><br/>Abnormal vibration<br/>
                    <strong>Historical analogue</strong><br/>RCA-017
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        st.markdown('<div class="vm-card-title">Evidence shortlist</div>', unsafe_allow_html=True)

        shortlist = (result or {}).get("evidence", [])[:4]
        if shortlist:
            shortlist_html = "".join(
                f"<div style='padding:9px 0;border-top:1px solid #e3e6ea;font-size:12px;'>"
                f"<strong>{esc(d['source'])}</strong><br/>"
                f"<span style='color:#68707d;'>Relevance score {esc(d['score'])}</span></div>"
                for d in shortlist
            )
        else:
            shortlist_html = (
                "<div class='vm-card-muted'>Evidence will appear here after verification.</div>"
            )

        st.markdown(f'<div class="vm-card">{shortlist_html}</div>', unsafe_allow_html=True)


with evidence_tab:
    st.markdown("### Evidence register")
    st.caption("Source-backed records considered during the investigation.")

    evidence = (result or {}).get("evidence", all_docs)
    if evidence:
        # Ensure score exists for non-investigation state
        normalized = []
        for d in evidence:
            nd = dict(d)
            nd.setdefault("score", "—")
            normalized.append(nd)
        render_evidence_table(normalized, statuses)

        st.write("")
        st.markdown("#### Source detail")
        for doc in normalized:
            with st.expander(doc["source"]):
                st.text(doc["content"])
    else:
        st.info("No evidence files were found in the data directory.")


with verification_tab:
    st.markdown("### Verification results")
    st.caption("Deterministic checks are shown separately from model-generated synthesis.")

    if result:
        render_conflicts(result.get("conflicts", []))

        st.write("")
        st.markdown("#### Verification principles")
        p1, p2, p3 = st.columns(3)
        with p1:
            metric_card("Provenance", "Required", "Every material claim should trace to a source")
        with p2:
            metric_card("Revision context", "Checked", "Current references take precedence")
        with p3:
            metric_card("Decision authority", "Human", "AI supports investigation, not authorization")
    else:
        st.info("Run an investigation first to populate the verification panel.")


with audit_tab:
    st.markdown("### Audit trail")
    st.caption("A lightweight trace of what the system did during this session.")

    now = datetime.now().strftime("%H:%M")
    activities = [
        (now, f"Loaded {len(all_docs)} engineering evidence files"),
        (now, "Parsed procedure revision and status metadata"),
    ]

    if result:
        activities.extend(
            [
                (now, f"Retrieved {len(result.get('evidence', []))} relevant evidence sources"),
                (now, f"Detected {len(result.get('conflicts', []))} revision conflict(s)"),
                (now, "Generated investigation recommendation" if result.get("used_model") else "Generated deterministic fallback recommendation"),
            ]
        )

    activity_html = "".join(
        f'<div class="vm-activity"><div class="vm-activity-time">{esc(t)}</div><div>{esc(msg)}</div></div>'
        for t, msg in activities
    )
    st.markdown(f'<div class="vm-card">{activity_html}</div>', unsafe_allow_html=True)


st.write("")
st.markdown(
    """
    <div style="border-top:1px solid #e3e6ea;padding-top:14px;color:#7a828d;font-size:11px;display:flex;justify-content:space-between;gap:16px;">
        <span>Veritas 0.1 · Engineering evidence verification prototype</span>
        <span>Decision support only · Human engineering review required</span>
    </div>
    """,
    unsafe_allow_html=True,
)
