import streamlit as st
import streamlit.components.v1 as components
import json
from pathlib import Path

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NLS Interactive Guideline",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Load data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    p = Path(__file__).parent / "nls_guideline.json"
    with open(p, encoding="utf-8") as f:
        return json.load(f)

data = load_data()

# ── Session State Logic ────────────────────────────────────────────────────────
def get_state(tab_id):
    if tab_id not in st.session_state:
        st.session_state[tab_id] = {"queue": [], "counter": 0}
    return st.session_state[tab_id]

# ── Interactive Tree Engine ────────────────────────────────────────────────────

def process_branch(branches, state):
    valid_ids = [b.get("id") for b in branches]
    
    for q_id in state["queue"]:
        if q_id in valid_ids:
            chosen = next((b for b in branches if b.get("id") == q_id), None)
            if chosen:
                return render_node(chosen, state)
    
    st.markdown("---")
    st.subheader("⚕️ Clinical Assessment Required - Make a Choice")
    
    # علامة مرجعية لنزول الصفحة عليها بعد الكبس
    st.markdown('<div id="latest-step"></div>', unsafe_allow_html=True)
    
    cols = st.columns(len(branches))
    clicked = False
    
    for i, b in enumerate(branches):
        cond = b.get("condition", "Choose option")
        btn_type = "primary" if "✅" in cond or "improved" in cond.lower() else "secondary"
        
        with cols[i]:
            if st.button(cond, key=f"btn_{b.get('id', i)}_{state['counter']}", use_container_width=True, type=btn_type):
                state["queue"].append(b["id"])
                # تفعيل أمر النزول التلقائي
                st.session_state["scroll_to_bottom"] = True 
                clicked = True
                
    if clicked:
        st.rerun()
        
    return False

def render_node(node, state):
    if node.get("outcome") == "routine_care":
        st.success(f"✅ OUTCOME: {node.get('outcome_label', 'Baby Care (Routine)')}")
        return True

    if "note" in node:
        st.warning(f"↩️ NOTE: {node['note']}")
        return True

    if "condition" in node:
        cond = node["condition"]
        if "✅" in cond: st.success(f"🔀 FINDING: {cond}")
        elif "No_" in cond or "< 60" in cond: st.error(f"🔀 FINDING: {cond}")
        else: st.warning(f"🔀 FINDING: {cond}")
        st.markdown("<div style='text-align:center; color:gray;'>⬇️</div>", unsafe_allow_html=True)

    if node.get("type") == "decision" and "label" in node:
        st.markdown(f"### 🔀 {node.get('label', '').upper()}")
        st.markdown("<div style='text-align:center; color:gray;'>⬇️</div>", unsafe_allow_html=True)

    if "action" in node:
        state["counter"] += 1
        with st.container():
            st.info(f"🛠️ ACTION {state['counter']}")
            lines = node["action"].split("\n")
            for line in lines:
                if line.strip(): st.markdown(f"- {line.strip()}")
        st.markdown("<div style='text-align:center; color:gray;'>⬇️</div>", unsafe_allow_html=True)

    if "considerations" in node:
        with st.expander("🔍 CONSIDER / EXCLUDE"):
            for c in node["considerations"]:
                st.markdown(f"- ⚠️ {c}")
        st.markdown("<div style='text-align:center; color:gray;'>⬇️</div>", unsafe_allow_html=True)

    if "steps" in node:
        for step in node["steps"]:
            if not render_node(step, state): 
                return False
        return True

    if "next" in node:
        nxt = node["next"]
        st.markdown(f"### 🔄 {nxt.get('label', '').upper()}")
        st.markdown("<div style='text-align:center; color:gray;'>⬇️</div>", unsafe_allow_html=True)
        
        if "branches" in nxt:
            return process_branch(nxt["branches"], state)

    if "branches" in node:
        return process_branch(node["branches"], state)

    return True

def render_pathway(pathway, state):
    st.header(f"{'🟠' if pathway['color']=='orange' else '🔵'} {pathway['label']}")
    st.caption(f"Gestational age: **{pathway['gestational_age']}**")
    
    with st.expander("⚡ Initial Actions at Birth", expanded=True):
        for a in pathway["initial_actions"]:
            st.markdown(f"- ✦ {a}")
            
    st.markdown("### 🩺 Assess at Birth")
    st.caption("Start the clock at birth")
    st.markdown("<div style='text-align:center; color:gray;'>⬇️</div>", unsafe_allow_html=True)
    
    render_node(pathway["assessment"], state)

# ── Main Application UI ───────────────────────────────────────────────────────

with st.sidebar:
    st.title("🫁 NLS Guideline")
    st.caption("Neonatal Life Support")
    st.markdown("---")
    
    st.subheader("Filter by Gestational Age")
    ga_options = ["Both Pathways"] + [p["label"] for p in data["pathways"]]
    selected_ga = st.selectbox("Select pathway:", ga_options, label_visibility="collapsed")
    
    st.markdown("---")
    if st.button("🔄 Reset Algorithm", use_container_width=True):
        st.session_state.clear()
        st.rerun()
        
    st.markdown("---")
    st.subheader("🎯 Target SpO₂ (Right Hand)")
    for v in data["target_spo2"]["values"]:
        st.markdown(f"**{v['time']}**: {v['range']}")

st.title("Neonatal Life Support — Interactive Guideline")
st.markdown("Interactive decision-tree guideline for neonatal resuscitation at birth")

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Start clock", "At birth")
with col2: st.metric("Good HR", "> 100 bpm")
with col3: st.metric("CC threshold", "< 60 bpm")
with col4: st.metric("Epinephrine", "0.01–0.03 mg/kg")

st.markdown("---")

pathways_to_show = [p for p in data["pathways"] if selected_ga == "Both Pathways" or p["label"] == selected_ga]

if len(pathways_to_show) == 2:
    tab1, tab2 = st.tabs([f"🔵 {data['pathways'][0]['label']}", f"🟠 {data['pathways'][1]['label']}"])
    with tab1: render_pathway(data["pathways"][0], get_state("tab1"))
    with tab2: render_pathway(data["pathways"][1], get_state("tab2"))
else:
    render_pathway(pathways_to_show[0], get_state("single"))

# ── الكود السحري لحل مشكلة تصعد الصفحة للأعلى ──────────────────────────────
if st.session_state.get("scroll_to_bottom", False):
    st.session_state["scroll_to_bottom"] = False
    # استخدام JavaScript لفرض الصفحة على النزول لآخر عنصر
    components.html("""
        <script>
            const mainElement = window.parent.document.querySelector('[data-testid="stMain"]');
            if(mainElement) {
                setTimeout(() => {
                    mainElement.scrollTo({ top: mainElement.scrollHeight, behavior: 'smooth' });
                }, 100);
            }
        </script>
    """, height=0, width=0)
