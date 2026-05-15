import streamlit as st
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="Neonatal Resuscitation Algorithm",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #005eb8 0%, #003087 100%);
        padding: 25px 30px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .main-header h1 { margin: 0; font-size: 2.5rem; font-weight: 800; }
    .main-header p { margin: 5px 0 0 0; font-size: 1.1rem; opacity: 0.9; }
    
    .step-card {
        background-color: #ffffff;
        border-left: 6px solid #005eb8;
        padding: 18px 25px;
        margin-bottom: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        animation: fadeIn 0.4s ease-in-out;
    }
    .action-card { background-color: #fff9e6; border-left-color: #ffb800; }
    .assessment-card { background-color: #e6f7ff; border-left-color: #1890ff; }
    .critical-card { background-color: #fff1f0; border-left-color: #f5222d; }
    .success-card { background-color: #f6ffed; border-left-color: #52c41a; }
    
    .step-key { font-weight: 700; font-size: 0.85rem; color: #555; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
    .step-value { font-size: 1.1rem; color: #222; font-weight: 500; }
    
    .branch-container {
        background-color: #f0f2f5;
        border: 2px dashed #005eb8;
        border-radius: 10px;
        padding: 30px;
        margin: 30px 0;
        text-align: center;
    }
    .branch-title { font-size: 1.3rem; font-weight: 700; color: #003087; margin-bottom: 20px; }
    
    .btn-container { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; }
    
    .spo2-container {
        background: #ffffff; border: 2px solid #005eb8; border-radius: 12px; padding: 20px; margin-top: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    @keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
</style>
""", unsafe_allow_html=True)

# --- Medical Logic: Priority Sorting for Steps ---
# To ensure branching works, we force a strict chronological order regardless of JSON key order
def get_step_weight(item):
    k, v = list(item.items())[0]
    kv_str = f"{k} {v}".lower()
    if "clock" in kv_str: return 0
    if "dcc" in kv_str or "plastic" in kv_str: return 1
    if "breathing" in k: return 2
    if ">100" in v: return 3
    if "ppv" in kv_str and "spontaneous" not in kv_str: return 4 # For <32 weeks initial PPV
    if "open_airway" in v: return 5
    if "apnoea" in k or "gasping" in k: return 6
    if "5 inflations" in v or "25 cm" in v or "30 cm" in v: return 7
    if "reasessment_after_5" in v: return 8
    if "no_increase" in v: return 9
    if "chest movements assessment" in v: return 10
    if "normal_chest" in k: return 11
    if "no_chest" in k: return 12
    if "increase pressure" in v: return 13
    if "repeat 5" in v: return 14
    if "increase_in_heart" in v: return 15
    if "continue ppv" in v: return 16
    if "reasessment_after_30" in v: return 17
    if "no_improvment" in k: return 18
    if "compression" in v: return 19
    if "epinephrine" in v: return 20
    if "pneumothorax" in v or "hypovolemia" in v: return 21
    if "spo2" in k: return 99
    if "baby care" in v: return 98
    return 50

def sort_path_medically(path):
    return sorted(path, key=get_step_weight)

# --- Load Data ---
@st.cache_data
def load_data():
    try:
        with open("app.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except: return None

data = load_data()

if data:
    ga_groups = {"<32_weeks": [], ">32_weeks": []}
    for path in data:
        ga = path[0].get("Gestational_age", "Unknown")
        if ga in ga_groups:
            ga_groups[ga].append(sort_path_medically(path)) # Sort upon loading

    # --- UI Header ---
    st.markdown("""
    <div class="main-header">
        <h1>👶 Neonatal Resuscitation Algorithm</h1>
        <p>Interactive Step-by-Step Clinical Pathway</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Sidebar Controls ---
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/pulse.png", width=80)
        st.title("Navigation")
        selected_ga = st.radio(
            "Select Gestational Age:",
            options=[">32_weeks", "<32_weeks"],
            format_func=lambda x: "≥ 32 Weeks" if x == ">32_weeks" else "< 32 Weeks",
            index=0
        )
        if st.button("🔄 Reset Algorithm", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # --- Initialize Session State for Wizard ---
    if "active_paths" not in st.session_state or st.session_state.get("current_ga") != selected_ga:
        st.session_state.current_ga = selected_ga
        st.session_state.active_paths = ga_groups[selected_ga]
        st.session_state.depth = 0
        
    # --- Extract Global SpO2 ---
    spo2_target = next((step["target_spo2_Right_hand"] for path in ga_groups[selected_ga] for step in path if "target_spo2_Right_hand" in step), None)

    # --- Helper to render a single step card ---
    def render_step(step, delay=0):
        key, value = list(step.items())[0]
        if key in ["Gestational_age", "target_spo2_Right_hand"]: return
        
        card_class = "step-card"
        icon = "➡️"
        if key.startswith("Action") or key == "consideration":
            card_class += " action-card"; icon = "🛠️"
        elif key in ["Breathing", "heart_rate", "Normal_chest_movements", "No_chest_movements", "apnoea_or_gasping"]:
            card_class += " assessment-card"; icon = "🩺"
            if "No_chest" in key or "apnoea" in key.lower(): icon = "⚠️"
        elif key in ["Case", "No_improvment"]:
            card_class += " critical-card"; icon = "🚨"
        elif key in ["improvment", "Improvement"]:
            card_class += " success-card"; icon = "✅"

        formatted_value = str(value).replace('_', ' ').replace(' cm h2o', ' cmH₂O').replace(' o2', ' O₂')
        st.markdown(f"""
        <div class="{card_class}" style="animation-delay: {delay}s">
            <div class="step-key">{icon} {key.replace('_', ' ')}</div>
            <div class="step-value">{formatted_value}</div>
        </div>
        """, unsafe_allow_html=True)

    # --- Main Wizard Logic ---
    st.subheader(f"🩺 Pathway Execution: { '≥ 32 Weeks' if selected_ga == '>32_weeks' else '< 32 Weeks' }")
    
    active = st.session_state.active_paths
    depth = st.session_state.depth

    # 1. Display the common steps up to the current depth
    for i in range(depth):
        if i < len(active[0]): # Safe check
            render_step(active[0][i], delay=i*0.1)

    # 2. Check for divergence (Branching point)
    # Get steps at current depth for paths that haven't ended yet
    valid_paths = [p for p in active if depth < len(p)]
    
    if valid_paths:
        current_steps = [p[depth] for p in valid_paths]
        unique_steps = set(tuple(sorted(s.items())) for s in current_steps)
        
        # If there's more than 1 unique step, it's a BRANCH!
        if len(unique_steps) > 1:
            st.markdown("""
            <div class="branch-container">
                <div class="branch-title">⚕️ Clinical Assessment Required</div>
                <div class="btn-container">
            """, unsafe_allow_html=True)
            
            cols = st.columns(len(unique_steps))
            for i, step_tuple in enumerate(unique_steps):
                step_dict = dict(step_tuple)
                key, value = list(step_dict.items())[0]
                btn_text = str(value).replace('_', ' ').replace(' cm h2o', ' cmH₂O')
                
                with cols[i]:
                    # Determine button color based on context
                    btn_type = "primary"
                    if "No_" in key or "No_" in value: btn_type = "secondary"
                    if "Normal" in key or "increase" in value or "improvment" in value.lower(): btn_type = "primary"
                    
                    if st.button(btn_text, key=f"btn_{depth}_{i}", use_container_width=True, type=btn_type):
                        # Filter paths to keep only those matching this choice
                        st.session_state.active_paths = [p for p in valid_paths if tuple(sorted(p[depth].items())) == step_tuple]
                        st.session_state.depth += 1
                        st.rerun()
            
            st.markdown("</div></div>", unsafe_allow_html=True)
            
            # Handle paths that ended before this branch (Implicit Success)
            ended_paths = [p for p in active if depth >= len(p)]
            if ended_paths:
                with st.expander("✅ Or did the baby improve spontaneously?"):
                    if st.button("Yes, Baby is Stable", key=f"btn_ended_{depth}", use_container_width=True, type="primary"):
                        st.session_state.active_paths = ended_paths
                        st.session_state.depth = 999 # Push to end
                        st.rerun()

    # 3. If no divergence, check if we reached the end
    else:
        # We reached the end of the active paths
        last_path = active[0]
        if "improvment" not in str(last_path[-2].keys()).lower() and "baby care" not in str(last_path[-2].values()).lower():
            render_step(last_path[-1])
        
        st.markdown("""
        <div class="step-card success-card" style="margin-top: 30px; text-align: center;">
            <div class="step-key">🏁 END OF PATHWAY</div>
            <div class="step-value">Scenario Completed Successfully</div>
        </div>
        """, unsafe_allow_html=True)
        
        if spo2_target:
            st.markdown('<div class="spo2-container">', unsafe_allow_html=True)
            st.markdown("#### 📈 Target Pre-Ductal SpO2 Reference")
            cols = st.columns([2, 2, 2, 2, 2, 2])
            parts = spo2_target.split(', ')
            for i, part in enumerate(parts):
                time, target = part.split(' at ')
                with cols[i]:
                    st.metric(label=f"⏱️ {time}", value=target)
            st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.divider()
    st.caption("Disclaimer: This tool is for educational purposes only. Follow your institutional protocols.")
