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
    with open(p, encoding="utf-8") as f:
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
.spo2-row { display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; margin-top: 10px; }
.spo2-chip { background:#1e3a5f; border:1px solid #3b82f6; border-radius:8px; padding:6px 14px; text-align:center; min-width:80px; }
.spo2-chip .time { font-size:0.7rem; color:#93c5fd; }
.spo2-chip .val  { font-size:0.9rem; font-weight:700; color:#dbeafe; }

/* Pathway header */
.pathway-header { background: linear-gradient(135deg,#1e3a5f 0%,#1e293b 100%); border-radius:12px; padding:20px 24px; margin-bottom:20px; border:1px solid #3b82f6; }
.pathway-header-orange { background: linear-gradient(135deg,#431407 0%,#1e293b 100%); border-color:#f97316; }

/* Interactive Branch Container */
.branch-container { background: #0f172a; border: 2px dashed #475569; border-radius: 12px; padding: 25px; margin: 20px 0; }
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


# ── Interactive Tree Logic ────────────────────────────────────────────────────

def handle_branches(branches, queue):
    """Renders buttons for branching. Returns False to stop auto-advance."""
    st.markdown('<div class="branch-container">', unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#94a3b8; margin-bottom:15px; font-weight:600;'>⚕️ CLINICAL ASSESSMENT REQUIRED</p>", unsafe_allow_html=True)
    
    cols = st.columns(len(branches))
    choice_made = False
    
    for i, b in enumerate(branches):
        cond = b.get("condition", b.get("label", "Choose option"))
        # Determine button color
        btn_type = "primary" if "✅" in cond or "improved" in cond.lower() else "secondary"
        
        with cols[i]:
            if st.button(cond, key=f"btn_{b.get('id', i)}", use_container_width=True, type=btn_type):
                st.session_state.selected_path.append(b["id"])
                choice_made = True
                
    st.markdown('</div>', unsafe_allow_html=True)
    
    if choice_made:
        st.rerun()
        
    return False # Signal to stop rendering further down


def render_interactive_tree(node, queue):
    """Recursively renders the tree based on the user's selected queue."""
    
    # Handle Lists (e.g., 'steps' array)
    if isinstance(node, list):
        for item in node:
            if not render_interactive_tree(item, queue):
                return False # Stop if a branch paused the flow
        return True

    # 1. Handle Terminal Outcomes
    if node.get("outcome") == "routine_care":
        st.markdown(card(badge('outcome','✅ OUTCOME') + 
                         f"<p style='margin:4px 0 0;font-size:1.1rem;font-weight:700;color:#4ade80;'>{node.get('outcome_label','Baby Care (Routine)')}</p>", 
                         "green"), unsafe_allow_html=True)
        return True

    # 2. Handle Notes (e.g., cross references)
    if "note" in node:
        st.markdown(card(badge('decision','↩ NOTE') + 
                         f"<p style='margin:4px 0 0;color:#fde68a;font-size:0.9rem;'>{node['note']}</p>", 
                         "yellow"), unsafe_allow_html=True)
        return True

    # 3. Render Self (Action / Condition)
    if "action" in node:
        st.session_state.step_counter += 1
        st.markdown(card(badge('action',f"ACTION {st.session_state.step_counter}") + render_action_text(node["action"]), "blue"), unsafe_allow_html=True)
        st.markdown(connector(), unsafe_allow_html=True)
        
    if "condition" in node:
        col = "green" if "✅" in node.get("condition","") else "yellow"
        st.markdown(card(badge('decision','🔀 FINDING') + 
                         f"<p style='margin:4px 0 0;font-weight:600;color:#f1f5f9;font-size:0.95rem;'>{node['condition']}</p>", 
                         col), unsafe_allow_html=True)
        st.markdown(connector(), unsafe_allow_html=True)

    # 4. Render Considerations (e.g., differential diagnosis)
    if "considerations" in node:
        items = "".join(f"<li style='color:#c4b5fd;font-size:0.85rem;'>⚠ {c}</li>" for c in node["considerations"])
        st.markdown(card(badge('consider','🔍 CONSIDER / EXCLUDE') + 
                         f"<ul style='margin:6px 0 0 12px;padding:0;'>{items}</ul>", 
                         "purple"), unsafe_allow_html=True)
        st.markdown(connector(), unsafe_allow_html=True)

    # 5. Process Sequential Steps Array
    if "steps" in node:
        return render_interactive_tree(node["steps"], queue)

    # 6. Process Next Node (Reassessment)
    if "next" in node:
        nxt = node["next"]
        ntype = nxt.get("type","")
        icon = "🔄" if ntype == "reassessment" else "🔀"
        
        st.markdown(card(badge('reassess', f'{icon} {ntype.upper()}') + 
                         f"<p style='margin:4px 0 0;font-weight:600;font-size:0.95rem;color:#e2e8f0;'>{nxt.get('label','')}</p>", 
                         "yellow"), unsafe_allow_html=True)
        st.markdown(connector(), unsafe_allow_html=True)

        if "branches" in nxt:
            return handle_branches(nxt["branches"], queue)

    # 7. Process Direct Branches
    if "branches" in node:
        return handle_branches(node["branches"], queue)

    return True


def render_pathway(pathway):
    color = pathway["color"]
    header_cls = "pathway-header-orange" if color == "orange" else ""
    icon = "🟠" if color == "orange" else "🔵"
    
    st.markdown(f"""
    <div class='pathway-header {header_cls}'>
        <h2 style='margin:0;color:#f8fafc;'>{icon} {pathway["label"]}</h2>
        <p style='margin:4px 0 0;color:#94a3b8;font-size:0.9rem;'>Gestational age: <strong style='color:#e2e8f0;'>{pathway["gestational_age"]}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    render_initial_actions(pathway["initial_actions"], color)
    
    st.markdown(card(badge('decision','🩺 ASSESS AT BIRTH') + 
                     "<p style='margin:4px 0 0;color:#94a3b8;font-size:0.85rem;'>Start the clock at birth</p>", 
                     color), unsafe_allow_html=True)
    st.markdown(connector(), unsafe_allow_html=True)

    # Start Interactive Walkthrough
    assessment = pathway["assessment"]
    render_interactive_tree(assessment, st.session_state.selected_path)


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

    st.markdown("### 🔍 Filter by Gestational Age")
    ga_options = ["Both Pathways"] + [p["label"] for p in data["pathways"]]
    selected_ga = st.selectbox("Select pathway:", ga_options, label_visibility="collapsed")

    show_spo2_sidebar()

    st.markdown("---")
    if st.button("🔄 Reset Algorithm", use_container_width=True):
        st.session_state.clear()
        st.rerun()
        
    st.markdown("""
    <div style='font-size:0.75rem;color:#475569;text-align:center;'>
        Based on NLS / ILCOR 2021 Guidelines<br>
        For educational use only
    </div>
    """, unsafe_allow_html=True)

# ── Session State Initialization ───────────────────────────────────────────────
if "current_ga" not in st.session_state or st.session_state.current_ga != selected_ga:
    st.session_state.current_ga = selected_ga
    st.session_state.selected_path = [] # Queue of branch IDs chosen by user
    st.session_state.step_counter = 0   # Tracks action numbers

# ── Main content ───────────────────────────────────────────────────────────────

st.markdown("""
<div style='padding:8px 0 20px;'>
    <h1 style='margin:0;font-size:1.8rem;'>🫁 Neonatal Life Support — Interactive Guideline</h1>
    <p style='color:#64748b;margin:4px 0 0;'>Interactive decision-tree guideline for neonatal resuscitation at birth</p>
</div>
""", unsafe_allow_html=True)

# Quick reference strip
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""<div class='card card-blue' style='text-align:center;padding:12px;'><div style='font-size:1.4rem;'>⏱️</div><div style='font-size:0.75rem;color:#94a3b8;'>Start clock</div><div style='font-weight:700;color:#e2e8f0;font-size:0.85rem;'>At birth</div></div>""", unsafe_allow_html=True)
with col2:
    st.markdown("""<div class='card card-green' style='text-align:center;padding:12px;'><div style='font-size:1.4rem;'>💓</div><div style='font-size:0.75rem;color:#94a3b8;'>Good HR</div><div style='font-weight:700;color:#4ade80;font-size:0.85rem;'>&gt; 100 bpm</div></div>""", unsafe_allow_html=True)
with col3:
    st.markdown("""<div class='card card-red' style='text-align:center;padding:12px;'><div style='font-size:1.4rem;'>🚨</div><div style='font-size:0.75rem;color:#94a3b8;'>CC threshold</div><div style='font-weight:700;color:#fca5a5;font-size:0.85rem;'>&lt; 60 bpm</div></div>""", unsafe_allow_html=True)
with col4:
    st.markdown("""<div class='card card-orange' style='text-align:center;padding:12px;'><div style='font-size:1.4rem;'>💊</div><div style='font-size:0.75rem;color:#94a3b8;'>Epinephrine</div><div style='font-weight:700;color:#fed7aa;font-size:0.85rem;'>0.01–0.03 mg/kg</div></div>""", unsafe_allow_html=True)

st.markdown("---")

with st.expander("🎯 Target SpO₂ Reference (Right Hand) — Click to expand", expanded=False):
    render_spo2(data["target_spo2"])

st.markdown("<br>", unsafe_allow_html=True)

# Render selected pathway(s)
pathways_to_show = [p for p in data["pathways"] if selected_ga == "Both Pathways" or p["label"] == selected_ga]

if len(pathways_to_show) == 2:
    tab1, tab2 = st.tabs([f"🔵 {data['pathways'][0]['label']}", f"🟠 {data['pathways'][1]['label']}"])
    with tab1:
        # Isolate state per tab to avoid mixing up queues if user switches tabs rapidly
        if "tab1_queue" not in st.session_state: st.session_state.tab1_queue = []
        if "tab1_counter" not in st.session_state: st.session_state.tab1_counter = 0
        
        # Temporarily override session state for rendering
        orig_queue, orig_counter = st.session_state.selected_path, st.session_state.step_counter
        st.session_state.selected_path, st.session_state.step_counter = st.session_state.tab1_queue, st.session_state.tab1_counter
        render_pathway(data["pathways"][0])
        st.session_state.tab1_queue, st.session_state.tab1_counter = st.session_state.selected_path, st.session_state.step_counter
        st.session_state.selected_path, st.session_state.step_counter = orig_queue, orig_counter

    with tab2:
        if "tab2_queue" not in st.session_state: st.session_state.tab2_queue = []
        if "tab2_counter" not in st.session_state: st.session_state.tab2_counter = 0
        
        orig_queue, orig_counter = st.session_state.selected_path, st.session_state.step_counter
        st.session_state.selected_path, st.session_state.step_counter = st.session_state.tab2_queue, st.session_state.tab2_counter
        render_pathway(data["pathways"][1])
        st.session_state.tab2_queue, st.session_state.tab2_counter = st.session_state.selected_path, st.session_state.step_counter
        st.session_state.selected_path, st.session_state.step_counter = orig_queue, orig_counter
else:
    render_pathway(pathways_to_show[0])

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#334155;font-size:0.8rem;padding:10px 0;'>
    NLS Interactive Guideline • For educational & training purposes only • Not for direct clinical use
</div>
""", unsafe_allow_html=True)
