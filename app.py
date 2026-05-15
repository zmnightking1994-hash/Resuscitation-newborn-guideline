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

# ── Custom CSS (Ultra-Clear Colors) ───────────────────────────────────────────
st.markdown("""
<style>
/* Base Dark Background */
[data-testid="stAppViewContainer"] { background: #0b1120; }
[data-testid="stSidebar"]          { background: #111827; border-right: 1px solid #1f2937; }
[data-testid="stSidebar"] * { color: #d1d5db !important; }

/* Typography */
h1, h2, h3 { color: #f9fafb !important; }
p, li       { color: #e5e7eb; }

/* Card Panels - High Contrast Borders */
.card {
    background: #111827;
    border: 1px solid #374151;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 14px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
}
.card-blue   { border-left: 6px solid #38bdf8; background: linear-gradient(90deg, #0c2d48 0%, #111827 100%); }
.card-yellow { border-left: 6px solid #fbbf24; background: linear-gradient(90deg, #422006 0%, #111827 100%); }
.card-green  { border-left: 6px solid #4ade80; background: linear-gradient(90deg, #052e16 0%, #111827 100%); }
.card-red    { border-left: 6px solid #f87171; background: linear-gradient(90deg, #450a0a 0%, #111827 100%); }
.card-purple { border-left: 6px solid #c084fc; background: linear-gradient(90deg, #3b0764 0%, #111827 100%); }
.card-orange { border-left: 6px solid #fb923c; background: linear-gradient(90deg, #431407 0%, #111827 100%); }

/* Step badges - Brighter */
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 800;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
}
.badge-action     { background:#0284c7; color:#e0f2fe; }
.badge-decision   { background:#a16207; color:#fef08a; }
.badge-reassess   { background:#15803d; color:#dcfce7; }
.badge-outcome    { background:#16a34a; color:#bbf7d0; }
.badge-alert      { background:#b91c1c; color:#fecaca; }
.badge-consider   { background:#7e22ce; color:#f3e8ff; }
.badge-initial    { background:#0e7490; color:#cffafe; }

/* Connector line */
.connector {
    width: 2px; height: 24px;
    background: #4b5563;
    margin: 0 auto 4px 32px;
}

/* SPO2 table */
.spo2-row { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; margin-top: 10px; }
.spo2-chip { background:#172554; border:2px solid #38bdf8; border-radius:8px; padding:8px 14px; text-align:center; min-width:90px; }
.spo2-chip .time { font-size:0.75rem; color:#7dd3fc; }
.spo2-chip .val  { font-size:1rem; font-weight:800; color:#e0f2fe; }

/* Pathway header */
.pathway-header { background: linear-gradient(135deg,#172554 0%,#111827 100%); border-radius:12px; padding:20px 24px; margin-bottom:20px; border:2px solid #38bdf8; }
.pathway-header-orange { background: linear-gradient(135deg,#431407 0%,#111827 100%); border-color:#fb923c; }

/* INTERACTIVE BRANCH CONTAINER - Attention Grabber */
.branch-container { 
    background: #1f2937; 
    border: 3px solid #fbbf24; 
    border-radius: 16px; 
    padding: 30px; 
    margin: 30px 0; 
    box-shadow: 0 0 25px rgba(251, 191, 36, 0.2); /* Yellow Glow */
}
.branch-container p { color: #fbbf24 !important; font-weight: bold; font-size: 1.1rem;}
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
        return f"<p style='margin:4px 0 0;color:#f3f4f6;font-size:1rem;font-weight:500;'>{lines[0]}</p>"
    items = "".join(f"<li style='color:#e5e7eb;font-size:0.95rem;margin:4px 0;'>{l}</li>" for l in lines)
    return f"<ul style='margin:8px 0 0 16px;padding:0;'>{items}</ul>"

def render_spo2(data_spo2):
    chips = "".join(
        f"<div class='spo2-chip'><div class='time'>{v['time']}</div><div class='val'>{v['range']}</div></div>"
        for v in data_spo2["values"]
    )
    st.markdown(f"""
    <div class='card card-blue'>
        {badge('initial','🎯 TARGET SpO₂ — RIGHT HAND')}
        <div class='spo2-row'>{chips}</div>
    </div>
    """, unsafe_allow_html=True)

def render_initial_actions(actions, color):
    items = "".join(f"<li style='color:#f3f4f6;font-size:0.95rem;margin:5px 0;'>✦ {a}</li>" for a in actions)
    st.markdown(f"""
    <div class='card card-{color}'>
        {badge('initial','⚡ INITIAL ACTIONS AT BIRTH')}
        <ul style='margin:8px 0 0 12px;padding:0;'>{items}</ul>
    </div>
    """, unsafe_allow_html=True)


# ── THE CORE: Interactive Tree Logic (FIXED) ──────────────────────────────────

def process_branches(branches, state):
    """Checks if user made a choice. If yes, routes into it. If no, shows buttons and STOPS."""
    
    # Did the user already make a choice that is sitting in the queue?
    if state["queue"] and state["queue"][0] in [b.get("id") for b in branches]:
        # YES: Consume the choice and continue walking down that branch
        chosen_id = state["queue"].pop(0)
        chosen_branch = next((b for b in branches if b.get("id") == chosen_id), None)
        
        if chosen_branch:
            # Render what was chosen so the user sees the path they took
            cond = chosen_branch.get("condition", "")
            col = "green" if "✅" in cond or "improved" in cond.lower() else "red"
            st.markdown(card(badge('decision','🔀 FINDING') + 
                             f"<p style='margin:4px 0 0;font-weight:700;color:#f9fafb;font-size:1.05rem;'>{cond}</p>", 
                             col), unsafe_allow_html=True)
            st.markdown(connector(), unsafe_allow_html=True)
            
            # Continue recursively down the chosen path
            return render_interactive_tree(chosen_branch, state)
    
    # NO choice made yet -> Pause execution and show buttons
    st.markdown('<div class="branch-container">', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>⚕️ CLINICAL ASSESSMENT REQUIRED — MAKE A CHOICE</p>", unsafe_allow_html=True)
    
    cols = st.columns(len(branches))
    clicked = False
    
    for i, b in enumerate(branches):
        cond = b.get("condition", "Choose option")
        # Green button for good stuff, Secondary (gray/white) for bad stuff to make it distinct
        btn_type = "primary" if "✅" in cond or "improved" in cond.lower() else "secondary"
        
        with cols[i]:
            if st.button(cond, key=f"btn_{b.get('id', i)}_{state['counter']}", use_container_width=True, type=btn_type):
                state["queue"].append(b["id"])
                clicked = True
                
    st.markdown('</div>', unsafe_allow_html=True)
    
    if clicked:
        st.rerun()
        
    return False # CRITICAL: Tells the parent function to STOP rendering further down


def render_interactive_tree(node, state):
    """Recursively renders the tree, pausing at branches."""
    
    # 1. Handle Terminal Outcomes
    if node.get("outcome") == "routine_care":
        st.markdown(card(badge('outcome','✅ OUTCOME') + 
                         f"<p style='margin:4px 0 0;font-size:1.2rem;font-weight:800;color:#4ade80;'>{node.get('outcome_label','Baby Care (Routine)')}</p>", 
                         "green"), unsafe_allow_html=True)
        return True

    # 2. Handle Notes
    if "note" in node:
        st.markdown(card(badge('decision','↩ NOTE') + 
                         f"<p style='margin:4px 0 0;color:#fde68a;font-size:1rem;'>{node['note']}</p>", 
                         "yellow"), unsafe_allow_html=True)
        return True

    # 3. Render Current Node Visuals (Action)
    if "action" in node:
        state["counter"] += 1
        st.markdown(card(badge('action',f"ACTION {state['counter']}") + render_action_text(node["action"]), "blue"), unsafe_allow_html=True)
        st.markdown(connector(), unsafe_allow_html=True)
        
    # 4. Render Considerations
    if "considerations" in node:
        items = "".join(f"<li style='color:#e9d5ff;font-size:0.95rem;font-weight:500;'>⚠ {c}</li>" for c in node["considerations"])
        st.markdown(card(badge('consider','🔍 CONSIDER / EXCLUDE') + 
                         f"<ul style='margin:8px 0 0 12px;padding:0;'>{items}</ul>", 
                         "purple"), unsafe_allow_html=True)
        st.markdown(connector(), unsafe_allow_html=True)

    # 5. Process Sequential Steps Array
    if "steps" in node:
        for step in node["steps"]:
            if not render_interactive_tree(step, state):
                return False # Stop if a branch paused the flow

    # 6. Process Next Node (Reassessment)
    if "next" in node:
        nxt = node["next"]
        ntype = nxt.get("type","")
        icon = "🔄" if ntype == "reassessment" else "🔀"
        
        st.markdown(card(badge('reassess', f'{icon} {ntype.upper()}') + 
                         f"<p style='margin:4px 0 0;font-weight:700;font-size:1rem;color:#fef08a;'>{nxt.get('label','')}</p>", 
                         "yellow"), unsafe_allow_html=True)
        st.markdown(connector(), unsafe_allow_html=True)

        if "branches" in nxt:
            return process_branches(nxt["branches"], state)

    # 7. Process Direct Branches
    if "branches" in node:
        return process_branches(node["branches"], state)

    return True


def render_pathway(pathway, state):
    color = pathway["color"]
    header_cls = "pathway-header-orange" if color == "orange" else ""
    icon = "🟠" if color == "orange" else "🔵"
    
    st.markdown(f"""
    <div class='pathway-header {header_cls}'>
        <h2 style='margin:0;color:#f9fafb;'>{icon} {pathway["label"]}</h2>
        <p style='margin:4px 0 0;color:#9ca3af;font-size:0.9rem;'>Gestational age: <strong style='color:#f3f4f6;'>{pathway["gestational_age"]}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    render_initial_actions(pathway["initial_actions"], color)
    
    st.markdown(card(badge('decision','🩺 ASSESS AT BIRTH') + 
                     "<p style='margin:4px 0 0;color:#9ca3af;font-size:0.9rem;'>Start the clock at birth</p>", 
                     color), unsafe_allow_html=True)
    st.markdown(connector(), unsafe_allow_html=True)

    # Start Interactive Walkthrough passing the isolated state
    render_interactive_tree(pathway["assessment"], state)


# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:10px 0;'>
        <span style='font-size:2.5rem;'>🫁</span>
        <h2 style='margin:4px 0;color:#f9fafb;font-size:1.1rem;'>NLS Guideline</h2>
        <p style='color:#6b7280;font-size:0.8rem;margin:0;'>Neonatal Life Support</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 🔍 Filter by Gestational Age")
    ga_options = ["Both Pathways"] + [p["label"] for p in data["pathways"]]
    selected_ga = st.selectbox("Select pathway:", ga_options, label_visibility="collapsed")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 Target SpO₂ (Right Hand)")
    for v in data["target_spo2"]["values"]:
        st.sidebar.markdown(
            f"<div style='display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #374151;'>"
            f"<span style='color:#7dd3fc;'>{v['time']}</span>"
            f"<span style='color:#e0f2fe;font-weight:800;'>{v['range']}</span></div>",
            unsafe_allow_html=True
        )

    st.markdown("---")
    if st.button("🔄 Reset Algorithm", use_container_width=True):
        st.session_state.clear()
        st.rerun()
        
    st.markdown("""
    <div style='font-size:0.75rem;color:#4b5563;text-align:center;'>
        Based on NLS / ILCOR 2021 Guidelines<br>
        For educational use only
    </div>
    """, unsafe_allow_html=True)

# ── Session State Initialization (Isolated for Tabs) ───────────────────────────
def get_state(tab_id):
    if tab_id not in st.session_state:
        st.session_state[tab_id] = {"queue": [], "counter": 0}
    return st.session_state[tab_id]

# ── Main content ───────────────────────────────────────────────────────────────

st.markdown("""
<div style='padding:8px 0 20px;'>
    <h1 style='margin:0;font-size:1.8rem;'>🫁 Neonatal Life Support — Interactive Guideline</h1>
    <p style='color:#6b7280;margin:4px 0 0;'>Interactive decision-tree guideline for neonatal resuscitation at birth</p>
</div>
""", unsafe_allow_html=True)

# Quick reference strip
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""<div class='card card-blue' style='text-align:center;padding:14px;'><div style='font-size:1.5rem;'>⏱️</div><div style='font-size:0.8rem;color:#9ca3af;'>Start clock</div><div style='font-weight:800;color:#38bdf8;font-size:0.9rem;'>At birth</div></div>""", unsafe_allow_html=True)
with col2:
    st.markdown("""<div class='card card-green' style='text-align:center;padding:14px;'><div style='font-size:1.5rem;'>💓</div><div style='font-size:0.8rem;color:#9ca3af;'>Good HR</div><div style='font-weight:800;color:#4ade80;font-size:0.9rem;'>&gt; 100 bpm</div></div>""", unsafe_allow_html=True)
with col3:
    st.markdown("""<div class='card card-red' style='text-align:center;padding:14px;'><div style='font-size:1.5rem;'>🚨</div><div style='font-size:0.8rem;color:#9ca3af;'>CC threshold</div><div style='font-weight:800;color:#f87171;font-size:0.9rem;'>&lt; 60 bpm</div></div>""", unsafe_allow_html=True)
with col4:
    st.markdown("""<div class='card card-purple' style='text-align:center;padding:14px;'><div style='font-size:1.5rem;'>💊</div><div style='font-size:0.8rem;color:#9ca3af;'>Epinephrine</div><div style='font-weight:800;color:#c084fc;font-size:0.9rem;'>0.01–0.03 mg/kg</div></div>""", unsafe_allow_html=True)

st.markdown("---")

with st.expander("🎯 Target SpO₂ Reference (Right Hand) — Click to expand", expanded=False):
    render_spo2(data["target_spo2"])

st.markdown("<br>", unsafe_allow_html=True)

# Render selected pathway(s)
pathways_to_show = [p for p in data["pathways"] if selected_ga == "Both Pathways" or p["label"] == selected_ga]

if len(pathways_to_show) == 2:
    tab1, tab2 = st.tabs([f"🔵 {data['pathways'][0]['label']}", f"🟠 {data['pathways'][1]['label']}"])
    with tab1:
        render_pathway(data["pathways"][0], get_state("tab1"))
    with tab2:
        render_pathway(data["pathways"][1], get_state("tab2"))
else:
    render_pathway(pathways_to_show[0], get_state("single"))

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#374151;font-size:0.8rem;padding:10px 0;'>
    NLS Interactive Guideline • For educational & training purposes only • Not for direct clinical use
</div>
""", unsafe_allow_html=True)
