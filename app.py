import streamlit as st
import json
from pathlib import Path

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NLS Interactive Guideline",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    p = Path(__file__).parent / "nls_guideline.json"
    with open(p) as f:
        return json.load(f)

data = load_data()

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Base */
[data-testid="stAppViewContainer"] { background: #0f172a; }
[data-testid="stSidebar"]          { background: #1e293b; border-right: 1px solid #334155; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* Typography */
h1, h2, h3 { color: #f8fafc !important; }
p, li       { color: #cbd5e1; }

/* Card panels */
.card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 14px;
}
.card-blue   { border-left: 5px solid #3b82f6; }
.card-orange { border-left: 5px solid #f97316; }
.card-green  { border-left: 5px solid #22c55e; }
.card-red    { border-left: 5px solid #ef4444; }
.card-yellow { border-left: 5px solid #eab308; }
.card-purple { border-left: 5px solid #a855f7; }

/* Step badges */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}
.badge-action     { background:#1d4ed8; color:#bfdbfe; }
.badge-decision   { background:#854d0e; color:#fef08a; }
.badge-reassess   { background:#4d7c0f; color:#d9f99d; }
.badge-outcome    { background:#166534; color:#86efac; }
.badge-alert      { background:#7f1d1d; color:#fca5a5; }
.badge-consider   { background:#5b21b6; color:#ddd6fe; }
.badge-initial    { background:#0e7490; color:#a5f3fc; }

/* Connector line */
.connector {
    width: 2px; height: 28px;
    background: #475569;
    margin: 0 auto 4px 32px;
}

/* SPO2 table */
.spo2-row {
    display: flex; gap: 8px;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 10px;
}
.spo2-chip {
    background:#1e3a5f;
    border:1px solid #3b82f6;
    border-radius:8px;
    padding:6px 14px;
    text-align:center;
    min-width:80px;
}
.spo2-chip .time { font-size:0.7rem; color:#93c5fd; }
.spo2-chip .val  { font-size:0.9rem; font-weight:700; color:#dbeafe; }

/* Pathway header */
.pathway-header {
    background: linear-gradient(135deg,#1e3a5f 0%,#1e293b 100%);
    border-radius:12px;
    padding:20px 24px;
    margin-bottom:20px;
    border:1px solid #3b82f6;
}
.pathway-header-orange {
    background: linear-gradient(135deg,#431407 0%,#1e293b 100%);
    border-color:#f97316;
}

/* Pill button override */
div[data-testid="stSelectbox"] > div > div { background:#1e293b; border-color:#475569; color:#f1f5f9; }

/* Step numbers */
.step-num {
    display:inline-flex; align-items:center; justify-content:center;
    width:26px; height:26px; border-radius:50%;
    background:#3b82f6; color:#fff;
    font-size:0.75rem; font-weight:700;
    margin-right:8px; flex-shrink:0;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

def badge(cls, text):
    return f'<span class="badge badge-{cls}">{text}</span>'

def card(content_html, color="blue"):
    return f'<div class="card card-{color}">{content_html}</div>'

def connector():
    return '<div class="connector"></div>'

def render_action_text(text: str):
    """Format multi-line action strings nicely."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if len(lines) == 1:
        return f"<p style='margin:4px 0 0;color:#e2e8f0;font-size:0.95rem;'>{lines[0]}</p>"
    items = "".join(f"<li style='color:#cbd5e1;font-size:0.9rem;margin:3px 0;'>{l}</li>" for l in lines)
    return f"<ul style='margin:6px 0 0 16px;padding:0;'>{items}</ul>"

def render_spo2(data_spo2):
    chips = "".join(
        f"<div class='spo2-chip'><div class='time'>{v['time']}</div><div class='val'>{v['range']}</div></div>"
        for v in data_spo2["values"]
    )
    st.markdown(f"""
    <div class='card card-blue'>
        {badge('initial','🎯 Target SpO₂ — Right Hand')}
        <div class='spo2-row'>{chips}</div>
    </div>
    """, unsafe_allow_html=True)

def render_initial_actions(actions, color):
    items = "".join(f"<li style='color:#e2e8f0;font-size:0.9rem;margin:4px 0;'>✦ {a}</li>" for a in actions)
    st.markdown(f"""
    <div class='card card-{color}'>
        {badge('initial','⚡ Initial Actions at Birth')}
        <ul style='margin:8px 0 0 12px;padding:0;'>{items}</ul>
    </div>
    """, unsafe_allow_html=True)


# ── Recursive tree renderer ────────────────────────────────────────────────────

def render_node(node, depth=0, step_counter=[0]):
    """Recursively render the decision tree nodes."""
    indent = depth * 20
    margin = f"margin-left:{indent}px;"

    # ── outcome / terminal ───────────────────────────────────────────────────
    if node.get("outcome") == "routine_care":
        st.markdown(f"""
        <div style='{margin}'>
            {connector()}
            <div class='card card-green'>
                {badge('outcome','✅ OUTCOME')}
                <p style='margin:4px 0 0;font-size:1rem;font-weight:700;color:#4ade80;'>
                    {node.get("outcome_label","Baby Care (Routine)")}
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── note / cross-reference ───────────────────────────────────────────────
    if "note" in node:
        st.markdown(f"""
        <div style='{margin}'>
            {connector()}
            <div class='card card-yellow'>
                {badge('decision','↩ NOTE')}
                <p style='margin:4px 0 0;color:#fde68a;font-size:0.9rem;'>{node['note']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── branch with condition label ──────────────────────────────────────────
    if "condition" in node:
        cond = node["condition"]
        color = "green" if "✅" in cond or "improved" in cond.lower() else "yellow"
        st.markdown(f"""
        <div style='{margin}'>
            {connector()}
            <div class='card card-{color}'>
                {badge('decision','🔀 BRANCH')}
                <p style='margin:4px 0 0;font-size:0.95rem;font-weight:600;color:#fef9c3;'>{cond}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        indent += 20
        margin = f"margin-left:{indent}px;"

    # ── action ───────────────────────────────────────────────────────────────
    if "action" in node:
        step_counter[0] += 1
        action_html = render_action_text(node["action"])
        st.markdown(f"""
        <div style='{margin}'>
            {connector()}
            <div class='card card-blue'>
                {badge('action',f"ACTION {step_counter[0]}")}
                {action_html}
            </div>
        </div>
        """, unsafe_allow_html=True)
        indent += 20
        margin = f"margin-left:{indent}px;"

    # ── considerations ───────────────────────────────────────────────────────
    if "considerations" in node:
        items = "".join(f"<li style='color:#c4b5fd;font-size:0.85rem;'>⚠ {c}</li>" for c in node["considerations"])
        st.markdown(f"""
        <div style='{margin}'>
            {connector()}
            <div class='card card-purple'>
                {badge('consider','🔍 CONSIDER / EXCLUDE')}
                <ul style='margin:6px 0 0 12px;padding:0;'>{items}</ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── outcome at leaf ───────────────────────────────────────────────────────
    if "outcome" in node and node.get("outcome") == "routine_care":
        st.markdown(f"""
        <div style='{margin}'>
            {connector()}
            <div class='card card-green'>
                {badge('outcome','✅ OUTCOME')}
                <p style='margin:4px 0 0;font-size:1rem;font-weight:700;color:#4ade80;'>
                    {node.get("outcome_label","Baby Care (Routine)")}
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── recurse into "next" ───────────────────────────────────────────────────
    if "next" in node:
        nxt = node["next"]
        lbl = nxt.get("label","")
        ntype = nxt.get("type","")
        badge_cls = "reassess" if ntype == "reassessment" else "decision"
        icon = "🔄" if ntype == "reassessment" else "🔀"
        st.markdown(f"""
        <div style='margin-left:{indent}px;'>
            {connector()}
            <div class='card card-{'yellow' if ntype=='decision' else 'green'}' style='border-color:#64748b;'>
                {badge(badge_cls, f'{icon} {ntype.upper()}')}
                <p style='margin:4px 0 0;font-weight:600;font-size:0.95rem;color:#e2e8f0;'>{lbl}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if "branches" in nxt:
            for branch in nxt["branches"]:
                render_node(branch, depth + 3, step_counter)
        elif nxt.get("type") == "reassessment":
            # terminal reassessment
            pass

    # ── inline branches (e.g. chest assessment decision) ─────────────────────
    if "branches" in node and "next" not in node:
        for branch in node["branches"]:
            render_node(branch, depth + 2, step_counter)


def render_pathway(pathway):
    color = pathway["color"]

    # Header
    header_cls = "pathway-header-orange" if color == "orange" else ""
    icon = "🟠" if color == "orange" else "🔵"
    st.markdown(f"""
    <div class='pathway-header {header_cls}'>
        <h2 style='margin:0;color:#f8fafc;'>{icon} {pathway["label"]}</h2>
        <p style='margin:4px 0 0;color:#94a3b8;font-size:0.9rem;'>Gestational age: <strong style='color:#e2e8f0;'>{pathway["gestational_age"]}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # Initial actions
    render_initial_actions(pathway["initial_actions"], color)

    # Assessment tree
    st.markdown(f"""
    <div class='card card-{color}'>
        {badge('decision','🩺 ASSESS AT BIRTH')}
        <p style='margin:4px 0 0;color:#94a3b8;font-size:0.85rem;'>Start the clock at birth</p>
    </div>
    """, unsafe_allow_html=True)

    step_counter = [0]
    for branch in pathway["assessment"]["branches"]:
        # Show top-level condition as a tab-like header
        cond = branch.get("condition","")
        icon_b = branch.get("icon","")
        b_color = "green" if "✅" in cond else "red"
        st.markdown(f"""
        <div style='margin-left:20px;'>
            <div class='connector'></div>
            <div class='card card-{b_color}'>
                {badge('decision',f'{icon_b} FINDING')}
                <p style='margin:4px 0 0;font-weight:700;color:#f1f5f9;font-size:1rem;'>{cond}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if branch.get("outcome") == "routine_care":
            # Optional extra action before outcome (e.g. lt32 good branch)
            if "action" in branch:
                act_html = render_action_text(branch["action"])
                st.markdown(f"""
                <div style='margin-left:40px;'>
                    <div class='connector'></div>
                    <div class='card card-blue'>
                        {badge('action','ACTION')}
                        {act_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown(f"""
            <div style='margin-left:40px;'>
                <div class='connector'></div>
                <div class='card card-green'>
                    {badge('outcome','✅ OUTCOME')}
                    <p style='margin:4px 0 0;font-size:1rem;font-weight:700;color:#4ade80;'>
                        {branch.get("outcome_label","Baby Care (Routine)")}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            continue

        # Inadequate branch — render steps
        for step in branch.get("steps", []):
            if step["type"] == "action":
                step_counter[0] += 1
                st.markdown(f"""
                <div style='margin-left:40px;'>
                    <div class='connector'></div>
                    <div class='card card-blue'>
                        {badge('action',f"ACTION {step_counter[0]}")}
                        <p style='margin:4px 0 0;color:#e2e8f0;font-size:0.95rem;'>{step['action']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif step["type"] == "decision":
                st.markdown(f"""
                <div style='margin-left:40px;'>
                    <div class='connector'></div>
                    <div class='card card-yellow'>
                        {badge('decision','🔀 DECISION')}
                        <p style='margin:4px 0 0;font-weight:600;color:#fef9c3;'>{step['label']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                for sub in step.get("branches", []):
                    render_node(sub, depth=3, step_counter=step_counter)


# ── SPO2 Reference modal ───────────────────────────────────────────────────────

def show_spo2_sidebar():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 Target SpO₂ (Right Hand)")
    for v in data["target_spo2"]["values"]:
        st.sidebar.markdown(
            f"<div style='display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #334155;'>"
            f"<span style='color:#93c5fd;'>{v['time']}</span>"
            f"<span style='color:#dbeafe;font-weight:700;'>{v['range']}</span></div>",
            unsafe_allow_html=True
        )

# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:10px 0;'>
        <span style='font-size:2.5rem;'>🫁</span>
        <h2 style='margin:4px 0;color:#f8fafc;font-size:1.1rem;'>NLS Guideline</h2>
        <p style='color:#64748b;font-size:0.8rem;margin:0;'>Neonatal Life Support</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # Gestational age filter
    st.markdown("### 🔍 Filter by Gestational Age")
    ga_options = ["Both Pathways"] + [p["label"] for p in data["pathways"]]
    selected_ga = st.selectbox("Select pathway:", ga_options, label_visibility="collapsed")

    show_spo2_sidebar()

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem;color:#475569;text-align:center;'>
        Based on NLS / ILCOR 2021 Guidelines<br>
        For educational use only
    </div>
    """, unsafe_allow_html=True)

# ── Main content ───────────────────────────────────────────────────────────────

st.markdown("""
<div style='padding:8px 0 20px;'>
    <h1 style='margin:0;font-size:1.8rem;'>
        🫁 Neonatal Life Support — Interactive Guideline
    </h1>
    <p style='color:#64748b;margin:4px 0 0;'>
        Interactive decision-tree guideline for neonatal resuscitation at birth
    </p>
</div>
""", unsafe_allow_html=True)

# Quick reference strip
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""<div class='card card-blue' style='text-align:center;padding:12px;'>
    <div style='font-size:1.4rem;'>⏱️</div>
    <div style='font-size:0.75rem;color:#94a3b8;'>Start clock</div>
    <div style='font-weight:700;color:#e2e8f0;font-size:0.85rem;'>At birth</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown("""<div class='card card-green' style='text-align:center;padding:12px;'>
    <div style='font-size:1.4rem;'>💓</div>
    <div style='font-size:0.75rem;color:#94a3b8;'>Good HR</div>
    <div style='font-weight:700;color:#4ade80;font-size:0.85rem;'>&gt; 100 bpm</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown("""<div class='card card-red' style='text-align:center;padding:12px;'>
    <div style='font-size:1.4rem;'>🚨</div>
    <div style='font-size:0.75rem;color:#94a3b8;'>CC threshold</div>
    <div style='font-weight:700;color:#fca5a5;font-size:0.85rem;'>&lt; 60 bpm</div>
    </div>""", unsafe_allow_html=True)
with col4:
    st.markdown("""<div class='card card-orange' style='text-align:center;padding:12px;'>
    <div style='font-size:1.4rem;'>💊</div>
    <div style='font-size:0.75rem;color:#94a3b8;'>Epinephrine</div>
    <div style='font-weight:700;color:#fed7aa;font-size:0.85rem;'>0.01–0.03 mg/kg</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# SpO2 reference (collapsible)
with st.expander("🎯 Target SpO₂ Reference (Right Hand) — Click to expand", expanded=False):
    render_spo2(data["target_spo2"])

st.markdown("<br>", unsafe_allow_html=True)

# Render selected pathway(s)
pathways_to_show = [p for p in data["pathways"] if
    selected_ga == "Both Pathways" or p["label"] == selected_ga]

if len(pathways_to_show) == 2:
    tab1, tab2 = st.tabs([f"🔵 {data['pathways'][0]['label']}", f"🟠 {data['pathways'][1]['label']}"])
    with tab1:
        render_pathway(data["pathways"][0])
    with tab2:
        render_pathway(data["pathways"][1])
else:
    render_pathway(pathways_to_show[0])

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#334155;font-size:0.8rem;padding:10px 0;'>
    NLS Interactive Guideline • For educational & training purposes only • Not for direct clinical use
</div>
""", unsafe_allow_html=True)
