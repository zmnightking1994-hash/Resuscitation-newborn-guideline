import streamlit as st
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
    """يعطي كل تبويب ذاكرة مستقلة لتتبع الخطوات."""
    if tab_id not in st.session_state:
        st.session_state[tab_id] = {"queue": [], "counter": 0}
    return st.session_state[tab_id]

# ── Interactive Tree Engine (The Core Logic) ───────────────────────────────────

def process_branch(branches, state):
    """هذه الدالة مسؤولة فقط عن نقاط التفرع (الأزرار)"""
    valid_ids = [b.get("id") for b in branches]
    
    # هل قام المستخدم بالكبس مسبقاً وتوجد خطوة محفوظة في الطابور؟
    if state["queue"] and state["queue"][0] in valid_ids:
        # نعم، قم بإزالتها من الطابور واكمل المشي في هذا الفرع
        chosen_id = state["queue"].pop(0)
        chosen = next((b for b in branches if b.get("id") == chosen_id), None)
        if chosen:
            return render_node(chosen, state)
    
    # لا، لم يقم بالكبس بعد -> توقف واعرض الأزرار
    st.markdown("---")
    st.subheader("⚕️ Clinical Assessment Required - Make a Choice")
    
    cols = st.columns(len(branches))
    clicked = False
    
    for i, b in enumerate(branches):
        cond = b.get("condition", "Choose option")
        
        # تحديد لون الزر (أخضر للإيجابي، رمادي/عادي للسلبي)
        btn_type = "primary" if "✅" in cond or "improved" in cond.lower() else "secondary"
        
        with cols[i]:
            if st.button(cond, key=f"btn_{b.get('id', i)}_{state['counter']}", use_container_width=True, type=btn_type):
                state["queue"].append(b["id"]) # حفظ الاختيار
                clicked = True
                
    if clicked:
        st.rerun() # تحديث فوري لاستكمال المسار
        
    return False # إشارة للتوقف عن طباعة باقي الشجرة


def render_node(node, state):
    """تقوم بالمشي داخل الشجرة وطباعة الخطوات المتسلسلة"""
    
    # 1. النهاية (Baby Care)
    if node.get("outcome") == "routine_care":
        st.success(f"✅ OUTCOME: {node.get('outcome_label', 'Baby Care (Routine)')}")
        return True

    # 2. ملاحظات إرجاعية
    if "note" in node:
        st.warning(f"↩️ NOTE: {node['note']}")
        return True

    # 3. طباعة الإجراءات (Actions)
    if "action" in node:
        state["counter"] += 1
        with st.container():
            st.info(f"🛠️ ACTION {state['counter']}")
            lines = node["action"].split("\n")
            for line in lines:
                if line.strip(): st.markdown(f"- {line.strip()}")
        st.markdown("<div style='text-align:center; color:gray;'>⬇️</div>", unsafe_allow_html=True)

    # 4. طباعة الحالات (Findings/Conditions)
    if "condition" in node:
        cond = node["condition"]
        if "✅" in cond: 
            st.success(f"🔀 FINDING: {cond}")
        elif "No_" in cond or "< 60" in cond: 
            st.error(f"🔀 FINDING: {cond}")
        else: 
            st.warning(f"🔀 FINDING: {cond}")
        st.markdown("<div style='text-align:center; color:gray;'>⬇️</div>", unsafe_allow_html=True)

    # 5. طباعة التشخيصات التفريقية (Considerations)
    if "considerations" in node:
        with st.expander("🔍 CONSIDER / EXCLUDE"):
            for c in node["considerations"]:
                st.markdown(f"- ⚠️ {c}")
        st.markdown("<div style='text-align:center; color:gray;'>⬇️</div>", unsafe_allow_html=True)

    # 6. معالجة مصفوفة الخطوات (Steps Array)
    if "steps" in node:
        for step in node["steps"]:
            if not render_node(step, state): 
                return False # توقف إذا واجهنا فرع ينتظر الكبس
        return True

    # 7. معالجة العقدة التالية (Next - Reassessment)
    if "next" in node:
        nxt = node["next"]
        st.markdown(f"### 🔄 {nxt.get('label', '').upper()}")
        st.markdown("<div style='text-align:center; color:gray;'>⬇️</div>", unsafe_allow_html=True)
        
        if "branches" in nxt:
            return process_branch(nxt["branches"], state)

    # 8. معالجة التفرعات المباشرة
    if "branches" in node:
        return process_branch(node["branches"], state)

    return True


def render_pathway(pathway, state):
    """واجهة عرض المسار الطبي"""
    st.header(f"{'🟠' if pathway['color']=='orange' else '🔵'} {pathway['label']}")
    st.caption(f"Gestational age: **{pathway['gestational_age']}**")
    
    with st.expander("⚡ Initial Actions at Birth", expanded=True):
        for a in pathway["initial_actions"]:
            st.markdown(f"- ✦ {a}")
            
    st.markdown("### 🩺 Assess at Birth")
    st.caption("Start the clock at birth")
    st.markdown("<div style='text-align:center; color:gray;'>⬇️</div>", unsafe_allow_html=True)
    
    # بدء المشي داخل الشجرة
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

# Page Header
st.title("Neonatal Life Support — Interactive Guideline")
st.markdown("Interactive decision-tree guideline for neonatal resuscitation at birth")

# Quick Reference Strip
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Start clock", "At birth")
with col2: st.metric("Good HR", "> 100 bpm")
with col3: st.metric("CC threshold", "< 60 bpm")
with col4: st.metric("Epinephrine", "0.01–0.03 mg/kg")

st.markdown("---")

# Render Tabs based on selection
pathways_to_show = [p for p in data["pathways"] if selected_ga == "Both Pathways" or p["label"] == selected_ga]

if len(pathways_to_show) == 2:
    tab1, tab2 = st.tabs([f"🔵 {data['pathways'][0]['label']}", f"🟠 {data['pathways'][1]['label']}"])
    with tab1: render_pathway(data["pathways"][0], get_state("tab1"))
    with tab2: render_pathway(data["pathways"][1], get_state("tab2"))
else:
    render_pathway(pathways_to_show[0], get_state("single"))
