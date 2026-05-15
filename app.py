import streamlit as st
import json
import html

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
    
    .legend-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-bottom: 30px;
        flex-wrap: wrap;
    }
    .legend-item {
        display: flex;
        align-items: center;
        font-weight: 600;
        font-size: 0.95rem;
        color: #333;
    }
    .legend-box {
        width: 20px;
        height: 20px;
        border-radius: 4px;
        margin-right: 8px;
        border: 2px solid #ccc;
    }
    .spo2-container {
        background: #ffffff;
        border: 2px solid #005eb8;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 40px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .branch-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #003087;
        border-bottom: 3px solid #ffb800;
        padding-bottom: 10px;
        margin-top: 40px;
        margin-bottom: 20px;
        display: inline-block;
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
        <p>Interactive Clinical Decision Tree</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Legend ---
    st.markdown("""
    <div class="legend-container">
        <div class="legend-item"><div class="legend-box" style="background:#e6f7ff; border-color:#1890ff;"></div> Assessment</div>
        <div class="legend-item"><div class="legend-box" style="background:#fff9e6; border-color:#ffb800;"></div> Action</div>
        <div class="legend-item"><div class="legend-box" style="background:#f6ffed; border-color:#52c41a;"></div> Success / Improvement</div>
        <div class="legend-item"><div class="legend-box" style="background:#fff1f0; border-color:#f5222d;"></div> Critical / No Improvement</div>
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
        st.info(f"Displaying {len(ga_groups[selected_ga])} clinical branches.")

    # --- Helper: Text Sanitizer for Mermaid ---
    def sanitize_mermaid(text):
        # Mermaid breaks with special characters, wrap in quotes and escape
        text = str(text).replace('"', "'").replace('_', ' ').replace(' cm h2o', ' cmH₂O').replace(' o2', ' O₂')
        return f'"{text}"'

    # --- Helper: Generate Branch Title ---
    def get_branch_title(path, index):
        title_parts = []
        for step in path:
            if "Breathing" in step: title_parts.append(step['Breathing'].replace('_', ' '))
            if "Case" in step: title_parts.append(step['Case'].replace('_', ' '))
            if "No_improvment" in step: title_parts.append(step['No_improvment'].replace('_', ' '))
            if "Improvement" in step or "improvment" in step: title_parts.append("Improved ✅")
        if not title_parts: return f"Branch {index + 1}"
        return f"Branch {index + 1}: " + " ➡️ ".join(title_parts)

    # --- Extract and Display SpO2 Targets (Global for GA) ---
    # Assuming SpO2 is consistent across paths for the same GA, we take the first occurrence
    spo2_target = next((step["target_spo2_Right_hand"] for path in ga_groups[selected_ga] for step in path if "target_spo2_Right_hand" in step), None)
    
    if spo2_target:
        st.markdown('<div class="spo2-container">', unsafe_allow_html=True)
        st.markdown("#### 📈 Target Pre-Ductal SpO2 (Right Hand)")
        cols = st.columns([2, 2, 2, 2, 2, 2])
        parts = spo2_target.split(', ')
        for i, part in enumerate(parts):
            time, target = part.split(' at ')
            with cols[i]:
                st.metric(label=f"⏱️ {time}", value=target)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Render Flowcharts ---
    st.subheader(f"🩺 Clinical Decision Tree ({ '≥ 32 Weeks' if selected_ga == '>32_weeks' else '< 32 Weeks' })")

    ignore_keys = ["Gestational_age", "target_spo2_Right_hand"]

    for i, path in enumerate(ga_groups[selected_ga]):
        branch_title = get_branch_title(path, i)
        st.markdown(f'<div class="branch-title">{branch_title}</div>', unsafe_allow_html=True)
        
        mermaid_code = "graph TD\n"
        # Define Styles in Mermaid
        mermaid_code += """
            classDef assess fill:#e6f7ff,stroke:#1890ff,stroke-width:2px,color:#000
            classDef action fill:#fff9e6,stroke:#ffb800,stroke-width:2px,color:#000
            classDef critical fill:#fff1f0,stroke:#f5222d,stroke-width:2px,color:#000
            classDef success fill:#f6ffed,stroke:#52c41a,stroke-width:2px,color:#000
        """
        
        nodes = []
        prev_node_id = None
        node_counter = 0
        
        # Generate a unique ID for this branch's nodes (e.g., A1, A2 for Branch 0; B1, B2 for Branch 1)
        branch_letter = chr(65 + i) 
        
        for step in path:
            for key, value in step.items():
                if key in ignore_keys or key == "Birth":
                    if key == "Birth":
                        # Create Start Node
                        start_id = f"{branch_letter}{node_counter}"
                        mermaid_code += f"{start_id}[{sanitize_mermaid(value)}]\n"
                        nodes.append(start_id)
                        prev_node_id = start_id
                        node_counter += 1
                    continue
                
                curr_node_id = f"{branch_letter}{node_counter}"
                node_text = sanitize_mermaid(f"{key.replace('_', ' ')}: {value}")
                
                # Determine Node Shape and Class based on Key
                if key in ["Breathing", "heart_rate", "Normal_chest_movements", "No_chest_movements", "apnoea_or_gasping", "No_apnoea_or_gasping", "Case", "Chest movements assessment"]:
                    # Diamond for assessment
                    mermaid_code += f"{curr_node_id}{{{node_text}}}\n"
                    if "No_chest" in key or "No_apnoea" in key.lower() or key == "Case":
                        mermaid_code += f"class {curr_node_id} critical;\n"
                    else:
                        mermaid_code += f"class {curr_node_id} assess;\n"
                        
                elif key.startswith("Action") or key == "consideration":
                    # Rectangle for actions
                    mermaid_code += f"{curr_node_id}[{node_text}]\n"
                    mermaid_code += f"class {curr_node_id} action;\n"
                    
                elif key in ["improvment", "Improvement"]:
                    # Stadium (Rounded) for success
                    mermaid_code += f"{curr_node_id}([{node_text}])\n"
                    mermaid_code += f"class {curr_node_id} success;\n"
                    
                elif key == "No_improvment":
                    # Diamond for critical failure
                    mermaid_code += f"{curr_node_id}{{{node_text}}}\n"
                    mermaid_code += f"class {curr_node_id} critical;\n"
                else:
                    mermaid_code += f"{curr_node_id}[{node_text}]\n"
                    mermaid_code += f"class {curr_node_id} action;\n"

                # Draw Edge from previous node
                if prev_node_id:
                    mermaid_code += f"{prev_node_id} --> {curr_node_id}\n"
                
                nodes.append(curr_node_id)
                prev_node_id = curr_node_id
                node_counter += 1

        # Render the Mermaid Chart in Streamlit
        st.markdown(mermaid_code)
        st.divider()

    # Footer
    st.caption("Disclaimer: This tool is for educational and reference purposes only. Always follow your institutional protocols and latest AAP/European guidelines for Neonatal Resuscitation.")
