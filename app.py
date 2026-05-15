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
        padding: 20px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data
def load_data():
    try:
        with open("app.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Error: 'app.json' file not found. Please ensure it is in the same directory.")
        return None
    except json.JSONDecodeError:
        st.error("Error: 'app.json' is malformed. Please check for missing commas or brackets.")
        return None

data = load_data()

if data:
    # --- Data Processing ---
    # Group scenarios by Gestational Age
    ga_groups = {"<32_weeks": [], ">32_weeks": []}
    
    for path in data:
        ga = path[0].get("Gestational_age", "Unknown")
        if ga in ga_groups:
            ga_groups[ga].append(path)

    # --- UI Header ---
    st.markdown("""
    <div class="main-header">
        <h1>👶 Neonatal Resuscitation Algorithm</h1>
        <p>Interactive Clinical Decision Support Tool based on latest guidelines</p>
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
        
        st.divider()
        st.subheader("Select Scenario Path")
        
        # Generate readable names for scenarios to make selection easier
        scenario_names = []
        for i, path in enumerate(ga_groups[selected_ga]):
            # Try to find a defining characteristic for the path
            name = f"Path {i+1}"
            for step in path:
                if "Breathing" in step:
                    name = f"Breathing: {step['Breathing']}"
                    break
                if "Case" in step:
                    name = f"Case: {step['Case'].replace('_', ' ')}"
                    break
            scenario_names.append(name)
            
        selected_scenario_idx = st.selectbox(
            "Choose a clinical path:",
            options=range(len(scenario_names)),
            format_func=lambda x: scenario_names[x]
        )

    # --- Main Content Area ---
    selected_path = ga_groups[selected_ga][selected_scenario_idx]
    
    # Extract SpO2 targets to display at the top
    spo2_target = ""
    for step in selected_path:
        if "target_spo2_Right_hand" in step:
            spo2_target = step["target_spo2_Right_hand"]
            break

    # Display SpO2 Target Timeline
    if spo2_target:
        st.subheader("📈 Target Pre-Ductal SpO2 (Right Hand)")
        st.markdown('<div class="spo2-container">', unsafe_allow_html=True)
        
        # Parse the string into a visual timeline
        cols = st.columns([2, 2, 2, 2, 2, 2])
        parts = spo2_target.split(', ')
        for i, part in enumerate(parts):
            time, target = part.split(' at ')
            with cols[i]:
                st.metric(label=f"⏱️ {time}", value=target)
        st.markdown('</div>', unsafe_allow_html=True)
        st.divider()

    # Display Steps
    st.subheader("🩺 Algorithm Steps")
    
    # Ignore GA and SpO2 in the step-by-step flow to avoid redundancy
    ignore_keys = ["Gestational_age", "target_spo2_Right_hand", "Birth"]

    for step in selected_path:
        for key, value in step.items():
            if key in ignore_keys:
                continue
                
            # Determine Card Style based on Key
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

            # Format text for better readability
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
