import streamlit as st
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="Neonatal Resuscitation Algorithm",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Professional Medical UI ---
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #005eb8 0%, #003087 100%);
        padding: 20px 30px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: 1px;
    }
    .main-header p {
        margin: 5px 0 0 0;
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Streamlit Expander Styling */
    .streamlit-expanderHeader {
        font-size: 1.1rem;
        font-weight: 600;
        background-color: #f0f4f8;
        border-radius: 8px;
        padding: 10px;
    }
    
    .step-card {
        background-color: #ffffff;
        border-left: 6px solid #005eb8;
        padding: 15px 20px;
        margin-bottom: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .step-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .action-card {
        background-color: #fff9e6;
        border-left: 6px solid #ffb800;
    }
    .assessment-card {
        background-color: #e6f7ff;
        border-left: 6px solid #1890ff;
    }
    .critical-card {
        background-color: #fff1f0;
        border-left: 6px solid #f5222d;
    }
    .success-card {
        background-color: #f6ffed;
        border-left: 6px solid #52c41a;
    }
    .step-key {
        font-weight: 700;
        font-size: 0.85rem;
        color: #555;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .step-value {
        font-size: 1.05rem;
        color: #222;
        font-weight: 500;
    }
    .spo2-container {
        background: #f9f9f9;
        border: 1px solid #eaeaea;
        border-radius: 10px;
        padding: 15px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data
def load_data():
    try:
        with open("app.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Error: 'app.json' file not found.")
        return None
    except json.JSONDecodeError:
        st.error("Error: 'app.json' is malformed.")
        return None

data = load_data()

if data:
    # --- Data Processing ---
    ga_groups = {"<32_weeks": [], ">32_weeks": []}
    
    for path in data:
        ga = path[0].get("Gestational_age", "Unknown")
        if ga in ga_groups:
            ga_groups[ga].append(path)

    # --- UI Header ---
    st.markdown("""
    <div class="main-header">
        <h1>👶 Neonatal Resuscitation Algorithm</h1>
        <p>Interactive Clinical Decision Support Tool</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Sidebar Controls (GA Filter ONLY) ---
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/pulse.png", width=80)
        st.title("Navigation")
        
        selected_ga = st.radio(
            "Select Gestational Age:",
            options=[">32_weeks", "<32_weeks"],
            format_func=lambda x: "≥ 32 Weeks" if x == ">32_weeks" else "< 32 Weeks",
            index=0
        )
        
        st.divider()
        st.info(f"Showing {len(ga_groups[selected_ga])} possible clinical scenarios for the selected age.")

    # --- Helper Function to Generate Smart Scenario Titles ---
    def get_scenario_title(path, index):
        title_parts = []
        for step in path:
            if "Breathing" in step:
                title_parts.append(f"Breathing: {step['Breathing'].replace('_', ' ')}")
            if "Case" in step:
                title_parts.append(f"Case: {step['Case'].replace('_', ' ')}")
            if "No_improvment" in step:
                title_parts.append(f"Status: {step['No_improvment'].replace('_', ' ')}")
            if "Improvement" in step or "improvment" in step:
                title_parts.append("Outcome: Improved ✅")
                
        # Fallback if no specific keys found
        if not title_parts:
            return f"Scenario {index + 1}"
            
        return f"Scenario {index + 1}: " + " ➡️ ".join(title_parts)

    # --- Main Content Area: Display all Scenarios as Expanders ---
    st.subheader(f"🩺 Clinical Pathways for { '≥ 32 Weeks' if selected_ga == '>32_weeks' else '< 32 Weeks' }")
    
    for i, path in enumerate(ga_groups[selected_ga]):
        scenario_title = get_scenario_title(path, i)
        
        with st.expander(scenario_title, expanded=(i==0)): # Expand the first scenario by default
            
            # Extract and Display SpO2 targets
            for step in path:
                if "target_spo2_Right_hand" in step:
                    spo2_target = step["target_spo2_Right_hand"]
                    st.markdown("#### 📈 Target Pre-Ductal SpO2 (Right Hand)")
                    st.markdown('<div class="spo2-container">', unsafe_allow_html=True)
                    cols = st.columns([2, 2, 2, 2, 2, 2])
                    parts = spo2_target.split(', ')
                    for j, part in enumerate(parts):
                        time, target = part.split(' at ')
                        with cols[j]:
                            st.metric(label=f"⏱️ {time}", value=target)
                    st.markdown('</div>', unsafe_allow_html=True)
                    break

            # Display Steps
            ignore_keys = ["Gestational_age", "target_spo2_Right_hand", "Birth"]

            for step in path:
                for key, value in step.items():
                    if key in ignore_keys:
                        continue
                        
                    # Determine Card Style
                    card_class = "step-card"
                    icon = "➡️"
                    
                    if key.startswith("Action"):
                        card_class += " action-card"
                        icon = "🛠️"
                    elif key in ["Breathing", "heart_rate", "Normal_chest_movements", "No_chest_movements", "apnoea_or_gasping", "No_apnoea_or_gasping"]:
                        card_class += " assessment-card"
                        icon = "🩺"
                        if "No_chest" in key or "apnoea" in key.lower():
                            icon = "⚠️"
                    elif key in ["Case", "No_improvment"]:
                        card_class += " critical-card"
                        icon = "🚨"
                    elif key in ["improvment", "Improvement"]:
                        card_class += " success-card"
                        icon = "✅"
                    elif key == "consideration":
                        card_class += " critical-card"
                        icon = "💡"

                    # Format text
                    formatted_value = str(value).replace('_', ' ').replace(' cm h2o', ' cmH₂O').replace(' o2', ' O₂')
                    
                    # Render Card
                    st.markdown(
                        f"""
                        <div class="{card_class}">
                            <div class="step-key">{icon} {key.replace('_', ' ')}</div>
                            <div class="step-value">{formatted_value}</div>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )

    # Footer
    st.divider()
    st.caption("Disclaimer: This tool is for educational and reference purposes only. Always follow your institutional protocols and latest AAP/European guidelines for Neonatal Resuscitation.")
