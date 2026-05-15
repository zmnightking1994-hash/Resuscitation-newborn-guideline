import streamlit as st
import json
from pathlib import Path

st.set_page_config(
    page_title="NLS Guideline",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Load JSON ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    p = Path(__file__).parent / "nls_guideline.json"
    with open(p) as f:
        return json.load(f)

data = load_data()

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

:root {
    --bg:        #0d1b2a;
    --surface:   #112236;
    --surface2:  #162d45;
    --border:    #1f4068;
    --accent:    #00c6be;
    --accent2:   #0a8f8a;
    --gold:      #f0a500;
    --warn:      #e85d04;
    --success:   #2dc653;
    --danger:    #e63946;
    --text:      #d8eaf8;
    --muted:     #6b8caa;
    --font:      'IBM Plex Sans', sans-serif;
    --mono:      'IBM Plex Mono', monospace;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    font-family: var(--font) !important;
    color: var(--text) !important;
}
[data-testid="stHeader"]     { display:none; }
[data-testid="stSidebar"]    { display:none; }
[data-testid="stDecoration"] { display:none; }
footer                       { display:none; }
.block-container { padding: 0 !important; max-width:100% !important; }

/* ── Fixed top bar ── */
.nls-header {
    position: fixed; top:0; left:0; right:0; z-index:999;
    background: linear-gradient(90deg,#0a1624 0%,#112236 60%,#0d2337 100%);
    border-bottom: 1px solid var(--border);
    display: flex; align-items:center; justify-content:space-between;
    padding: 0 28px; height: 60px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.45);
}
.nls-logo { display:flex; align-items:center; gap:12px; }
.nls-logo-icon {
    width:36px; height:36px;
    background: linear-gradient(135deg,var(--accent),var(--accent2));
    border-radius:10px; display:flex; align-items:center;
    justify-content:center; font-size:18px;
}
.nls-logo-text { font-size:1rem; font-weight:700; color:#fff; letter-spacing:0.06em; }
.nls-logo-sub  { font-size:0.6rem; color:var(--muted); font-family:var(--mono);
                  letter-spacing:0.14em; text-transform:uppercase; }
.spo2-strip { display:flex; gap:5px; }
.spo2-chip  {
    background:rgba(0,198,190,0.07);
    border:1px solid rgba(0,198,190,0.2);
    border-radius:6px; padding:3px 8px; text-align:center;
}
.spo2-chip .t { font-size:0.57rem; color:var(--accent); font-family:var(--mono); }
.spo2-chip .v { font-size:0.7rem; font-weight:700; color:#b2ecea; }
.hdr-spo2-label {
    font-family:var(--mono); font-size:0.58rem; color:var(--muted);
    letter-spacing:0.1em; margin-bottom:4px;
}

/* ── Main wrapper ── */
.nls-main {
    margin-top: 60px;
    padding: 32px 40px 80px;
    min-height: calc(100vh - 60px);
    background:
        radial-gradient(ellipse 800px 500px at 8% 18%, rgba(0,198,190,0.045) 0%,transparent 70%),
        radial-gradient(ellipse 600px 400px at 92% 82%, rgba(10,143,138,0.05) 0%,transparent 70%),
        radial-gradient(ellipse 400px 300px at 50% 50%, rgba(15,40,70,0.4) 0%,transparent 100%),
        var(--bg);
}

/* ── Progress ── */
.progress-wrap {
    background: var(--surface2);
    border-radius:4px; height:4px;
    margin-bottom:28px; overflow:hidden;
    max-width:720px; margin-left:auto; margin-right:auto;
}
.progress-fill {
    height:100%; border-radius:4px;
    background: linear-gradient(90deg,var(--accent2),var(--accent));
    transition: width 0.5s ease;
}

/* ── Breadcrumb ── */
.breadcrumb {
    display:flex; align-items:center; gap:7px; flex-wrap:wrap;
    max-width:720px; margin:0 auto 18px;
}
.bc-item {
    font-family:var(--mono); font-size:0.67rem; color:var(--muted);
    background:var(--surface2); border:1px solid var(--border);
    border-radius:5px; padding:3px 8px;
    max-width:155px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
}
.bc-arrow { color:var(--border); font-size:0.65rem; }

/* ── GA selector ── */
.ga-card {
    background:var(--surface); border:1px solid var(--border);
    border-radius:16px; padding:36px 28px; text-align:center;
    position:relative; overflow:hidden;
    transition: transform .25s, box-shadow .25s, border-color .25s;
}
.ga-card:hover {
    transform:translateY(-5px);
    box-shadow: 0 20px 40px rgba(0,0,0,.45);
    border-color: var(--accent);
}
.ga-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:3px;
    border-radius:16px 16px 0 0;
}
.ga-card-term::before    { background:linear-gradient(90deg,#3a7bd5,#00d2ff); }
.ga-card-preterm::before { background:linear-gradient(90deg,#f0a500,#e85d04); }
.ga-card-icon  { font-size:3rem; margin-bottom:12px; }
.ga-card-title { font-size:1.3rem; font-weight:700; color:#fff; margin-bottom:5px; }
.ga-card-sub   { font-size:0.82rem; color:var(--muted); }

/* ── Step cards ── */
.step-card {
    background:var(--surface); border:1px solid var(--border);
    border-radius:16px; padding:24px 26px;
    max-width:720px; margin:0 auto 16px;
    box-shadow: 0 6px 28px rgba(0,0,0,.22);
    position:relative; overflow:hidden;
}
.step-card::before {
    content:''; position:absolute;
    top:0; left:0; bottom:0; width:4px;
}
.sc-action::before   { background:linear-gradient(180deg,#3a7bd5,#00d2ff); }
.sc-decision::before { background:linear-gradient(180deg,#f0a500,#e85d04); }
.sc-outcome::before  { background:linear-gradient(180deg,#2dc653,#00a86b); }
.sc-reassess::before { background:linear-gradient(180deg,#a855f7,#7c3aed); }
.sc-critical::before { background:linear-gradient(180deg,#e63946,#c1121f); }
.sc-info::before     { background:linear-gradient(180deg,#00c6be,#0a8f8a); }

.step-badge {
    display:inline-flex; align-items:center; gap:5px;
    font-family:var(--mono); font-size:0.65rem; font-weight:600;
    letter-spacing:0.13em; text-transform:uppercase;
    padding:3px 10px; border-radius:20px; margin-bottom:10px;
}
.b-action   { background:rgba(58,123,213,.14); color:#74b3fa; border:1px solid rgba(58,123,213,.3); }
.b-decision { background:rgba(240,165,0,.12);  color:#fcd34d; border:1px solid rgba(240,165,0,.28); }
.b-outcome  { background:rgba(45,198,83,.12);  color:#6ee7a0; border:1px solid rgba(45,198,83,.28); }
.b-reassess { background:rgba(168,85,247,.12); color:#d8b4fe; border:1px solid rgba(168,85,247,.28); }
.b-critical { background:rgba(230,57,70,.12);  color:#fca5a5; border:1px solid rgba(230,57,70,.28); }
.b-info     { background:rgba(0,198,190,.1);   color:#99f6e4; border:1px solid rgba(0,198,190,.22); }

.step-title { font-size:1.2rem; font-weight:700; color:#fff; margin-bottom:8px; line-height:1.4; }
.step-body  { font-size:0.9rem; color:#b8d4e8; line-height:1.7; }
.step-body li { margin-bottom:4px; }
.step-body ul { margin-left:16px; padding:0; }

/* ── Choice buttons ── */
.stButton>button {
    font-family:var(--font) !important;
    border-radius:10px !important; border:1px solid var(--border) !important;
    background:var(--surface2) !important; color:var(--text) !important;
    font-size:0.88rem !important; padding:10px 18px !important;
    transition:all .2s ease !important;
    text-align:left !important; width:100% !important;
}
.stButton>button:hover {
    border-color:var(--accent) !important;
    background:rgba(0,198,190,.07) !important;
    color:#fff !important; transform:translateX(4px) !important;
}
.btn-yes>button  { border-color:rgba(45,198,83,.38) !important; background:rgba(45,198,83,.07) !important; color:#6ee7a0 !important; }
.btn-yes>button:hover { background:rgba(45,198,83,.14) !important; border-color:#2dc653 !important; }
.btn-no>button   { border-color:rgba(230,57,70,.38) !important; background:rgba(230,57,70,.07) !important; color:#fca5a5 !important; }
.btn-no>button:hover  { background:rgba(230,57,70,.14) !important; border-color:#e63946 !important; }
.btn-warn>button { border-color:rgba(240,165,0,.35) !important; background:rgba(240,165,0,.07) !important; color:#fcd34d !important; }
.btn-warn>button:hover { background:rgba(240,165,0,.14) !important; }

/* ── Section label ── */
.sec-label {
    font-family:var(--mono); font-size:0.63rem; letter-spacing:0.14em;
    text-transform:uppercase; color:var(--muted); margin-bottom:12px;
    max-width:720px; margin-left:auto; margin-right:auto;
}

/* ── Outcome screen ── */
.outcome-screen {
    text-align:center; padding:44px 28px;
    background:var(--surface); border:1px solid rgba(45,198,83,.3);
    border-radius:20px; max-width:560px; margin:0 auto;
    box-shadow: 0 0 60px rgba(45,198,83,.09);
}
.outcome-icon  { font-size:3.8rem; margin-bottom:14px; }
.outcome-title { font-size:1.55rem; font-weight:700; color:var(--success); }
.outcome-sub   { font-size:0.86rem; color:var(--muted); margin-top:6px; }

/* ── Consideration chips ── */
.consider-grid  { display:flex; flex-wrap:wrap; gap:7px; margin-top:10px; }
.consider-chip  {
    background:rgba(168,85,247,.1); border:1px solid rgba(168,85,247,.28);
    border-radius:20px; padding:3px 11px; font-size:0.78rem; color:#d8b4fe;
}

/* quick-ref strip */
.qr-strip { display:flex; gap:12px; max-width:720px; margin:0 auto 28px; }
.qr-chip {
    flex:1; background:var(--surface); border:1px solid var(--border);
    border-radius:10px; padding:10px 12px; text-align:center;
}
.qr-chip .qi { font-size:1.1rem; }
.qr-chip .ql { font-size:0.58rem; color:var(--muted); font-family:var(--mono);
                letter-spacing:0.09em; text-transform:uppercase; }
.qr-chip .qv { font-size:0.82rem; font-weight:700; margin-top:2px; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
SPO2 = data["target_spo2"]["values"]

def spo2_header():
    chips = "".join(
        f"<div class='spo2-chip'><div class='t'>{v['time']}</div><div class='v'>{v['range']}</div></div>"
        for v in SPO2
    )
    return f"""
    <div style='text-align:right;'>
        <div class='hdr-spo2-label'>TARGET SpO₂ — RIGHT HAND</div>
        <div class='spo2-strip'>{chips}</div>
    </div>"""

def render_breadcrumb():
    hist = st.session_state.history[-6:]
    if not hist: return
    items = ""
    for i, h in enumerate(hist):
        items += f"<span class='bc-item' title='{h}'>{h[:22]}{'…' if len(h)>22 else ''}</span>"
        if i < len(hist)-1: items += "<span class='bc-arrow'>›</span>"
    st.markdown(f"<div class='breadcrumb'>{items}</div>", unsafe_allow_html=True)

def render_progress(pct):
    st.markdown(f"""
    <div class='progress-wrap'>
        <div class='progress-fill' style='width:{int(pct)}%;'></div>
    </div>""", unsafe_allow_html=True)

def reset():
    for k in ["step","ga","node_stack","history"]:
        if k in st.session_state: del st.session_state[k]

def go_back():
    if len(st.session_state.node_stack) > 1:
        st.session_state.node_stack.pop()
        if st.session_state.history: st.session_state.history.pop()
    else:
        reset()

def get_pathway():
    for p in data["pathways"]:
        if (st.session_state.get("ga") == ">32" and p["id"] == "GA_gt32") or \
           (st.session_state.get("ga") == "<32" and p["id"] == "GA_lt32"):
            return p

# State defaults
if "step"       not in st.session_state: st.session_state.step = "start"
if "ga"         not in st.session_state: st.session_state.ga = None
if "node_stack" not in st.session_state: st.session_state.node_stack = []
if "history"    not in st.session_state: st.session_state.history = []

# ── Fixed header ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class='nls-header'>
    <div class='nls-logo'>
        <div class='nls-logo-icon'>🫁</div>
        <div>
            <div class='nls-logo-text'>NLS GUIDELINE</div>
            <div class='nls-logo-sub'>Neonatal Life Support • Interactive Protocol</div>
        </div>
    </div>
    {spo2_header()}
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='nls-main'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# START — Choose gestational age
# ════════════════════════════════════════════════════════════
if st.session_state.step == "start":

    st.markdown("""
    <div style='max-width:720px;margin:0 auto 8px;'>
        <div style='font-family:var(--mono);font-size:0.62rem;color:var(--muted);letter-spacing:0.16em;margin-bottom:10px;'>STEP 1 — TRIAGE</div>
        <h2 style='font-size:1.5rem;color:#fff;margin-bottom:6px;'>Gestational Age?</h2>
        <p style='color:var(--muted);font-size:0.88rem;margin-bottom:32px;'>Select the pathway to start the resuscitation protocol</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick reference strip
    st.markdown("""
    <div class='qr-strip'>
        <div class='qr-chip'><div class='qi'>⏱️</div><div class='ql'>Clock</div><div class='qv' style='color:#74b3fa;'>At birth</div></div>
        <div class='qr-chip'><div class='qi'>💓</div><div class='ql'>Good HR</div><div class='qv' style='color:#6ee7a0;'>&gt;100 bpm</div></div>
        <div class='qr-chip'><div class='qi'>🚨</div><div class='ql'>CC threshold</div><div class='qv' style='color:#fca5a5;'>&lt;60 bpm</div></div>
        <div class='qr-chip'><div class='qi'>💊</div><div class='ql'>Epinephrine</div><div class='qv' style='color:#fcd34d;'>0.01–0.03 mg/kg</div></div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("<div class='ga-card ga-card-term'><div class='ga-card-icon'>👶🏻</div><div class='ga-card-title'>≥ 32 Weeks</div><div class='ga-card-sub'>Term / Near-Term</div></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶  Select  ≥ 32 Weeks — Term / Near-Term", key="ga_gt32", use_container_width=True):
            st.session_state.ga = ">32"
            st.session_state.step = "pathway"
            st.session_state.history = ["GA ≥32 wks"]
            st.rerun()

    with c2:
        st.markdown("<div class='ga-card ga-card-preterm'><div class='ga-card-icon'>🍼</div><div class='ga-card-title'>&lt; 32 Weeks</div><div class='ga-card-sub'>Preterm</div></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶  Select  < 32 Weeks — Preterm", key="ga_lt32", use_container_width=True):
            st.session_state.ga = "<32"
            st.session_state.step = "pathway"
            st.session_state.history = ["GA <32 wks"]
            st.rerun()

# ════════════════════════════════════════════════════════════
# PATHWAY — Show initial actions, then branch selector
# ════════════════════════════════════════════════════════════
elif st.session_state.step == "pathway":
    pw = get_pathway()
    render_progress(12)

    color = "#3a7bd5" if st.session_state.ga == ">32" else "#f0a500"
    st.markdown(f"""
    <div style='max-width:720px;margin:0 auto 18px;display:flex;align-items:center;gap:12px;'>
        <span style='background:{color}1a;border:1px solid {color}44;color:{color};
                     font-family:var(--mono);font-size:0.68rem;font-weight:700;
                     letter-spacing:0.12em;padding:4px 14px;border-radius:20px;'>
            {pw["label"].upper()}
        </span>
        <span style='color:var(--muted);font-size:0.82rem;'>⏱ Start the clock at birth</span>
    </div>""", unsafe_allow_html=True)

    # Initial actions
    items = "".join(f"<li>{a}</li>" for a in pw["initial_actions"])
    st.markdown(f"""
    <div class='step-card sc-action'>
        <div class='step-badge b-action'>⚡ INITIAL ACTIONS</div>
        <div class='step-title'>Perform Immediately at Birth</div>
        <div class='step-body'><ul>{items}</ul></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='sec-label'>→ Assess the newborn:</div>", unsafe_allow_html=True)

    # Assessment branches
    for br in pw["assessment"]["branches"]:
        cond = br["condition"]
        is_good = ("Spontaneous" in cond and "100" in cond)
        btn_cls = "btn-yes" if is_good else "btn-no"
        icon = "✅" if is_good else "⚠️"
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"<div class='{btn_cls}'>", unsafe_allow_html=True)
            if st.button(f"{icon}  {cond}", key=f"assess_{br['id']}", use_container_width=True):
                st.session_state.node_stack = [("assess", br)]
                st.session_state.history.append(cond)
                st.session_state.step = "wizard"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← Back", key="back_pw", use_container_width=True):
            reset(); st.rerun()

# ════════════════════════════════════════════════════════════
# WIZARD — Step-by-step interactive decision tree
# ════════════════════════════════════════════════════════════
elif st.session_state.step == "wizard":
    node_label, node = st.session_state.node_stack[-1]
    depth = len(st.session_state.node_stack)
    render_progress(min(12 + depth * 13, 96))
    render_breadcrumb()

    # ── Terminal: Baby Care outcome ────────────────────────────────────────────
    if node.get("outcome") == "routine_care":
        extra_action = ""
        if "action" in node:
            items = "".join(f"<li>{l.strip()}</li>" for l in node["action"].split("\n") if l.strip())
            extra_action = f"<div class='step-body' style='margin-bottom:18px;'><ul>{items}</ul></div>"
        st.markdown(f"""
        <div class='outcome-screen'>
            {extra_action}
            <div class='outcome-icon'>✅</div>
            <div class='outcome-title'>{node.get("outcome_label","Baby Care (Routine)")}</div>
            <div class='outcome-sub'>Continue standard neonatal monitoring and care</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("↩  Start New Assessment", use_container_width=True, key="restart_oc"):
                reset(); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

    # ── Note / cross-reference ─────────────────────────────────────────────────
    if "note" in node:
        st.markdown(f"""
        <div class='step-card sc-info'>
            <div class='step-badge b-info'>ℹ NOTE</div>
            <div class='step-title'>{node["note"]}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("← Back", use_container_width=True, key="back_note"):
                    go_back(); st.rerun()
            with col_b:
                if st.button("↩ Restart", use_container_width=True, key="rst_note"):
                    reset(); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

    # ── Condition badge ────────────────────────────────────────────────────────
    if "condition" in node:
        cond = node["condition"]
        col = "#2dc653" if ("✅" in cond or "improved" in cond.lower() or "increased" in cond.lower()) else "#e85d04"
        st.markdown(f"""
        <div style='max-width:720px;margin:0 auto 14px;'>
            <span style='background:{col}18;border:1px solid {col}44;color:{col};
                         font-family:var(--mono);font-size:0.7rem;font-weight:700;
                         letter-spacing:0.11em;padding:4px 14px;border-radius:20px;'>
                {cond}
            </span>
        </div>""", unsafe_allow_html=True)

    # ── Action display ─────────────────────────────────────────────────────────
    if "action" in node:
        lines = [l.strip() for l in node["action"].split("\n") if l.strip()]
        action_lower = node["action"].lower()
        if "epinephrine" in action_lower or "compression" in action_lower or "vascular" in action_lower:
            sc, bc, bt = "sc-critical", "b-critical", "🚨 CRITICAL ACTION"
        elif "ppv" in action_lower or "inflation" in action_lower or "ventilation" in action_lower:
            sc, bc, bt = "sc-action", "b-action", "💨 VENTILATION"
        else:
            sc, bc, bt = "sc-action", "b-action", "⚡ ACTION"
        items = "".join(f"<li>{l}</li>" for l in lines)
        consider_html = ""
        if "considerations" in node:
            chips = "".join(f"<span class='consider-chip'>⚠ {c}</span>" for c in node["considerations"])
            consider_html = f"""
            <div style='margin-top:16px;'>
                <div class='step-badge b-critical' style='margin-bottom:8px;'>🔍 CONSIDER / EXCLUDE</div>
                <div class='consider-grid'>{chips}</div>
            </div>"""
        st.markdown(f"""
        <div class='step-card {sc}'>
            <div class='step-badge {bc}'>{bt}</div>
            <div class='step-title'>Perform Now</div>
            <div class='step-body'><ul>{items}</ul></div>
            {consider_html}
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Steps array (for inadequate-breathing branch) ──────────────────────────
    if "steps" in node:
        for step in node["steps"]:
            if step["type"] == "action":
                st.markdown(f"""
                <div class='step-card sc-action'>
                    <div class='step-badge b-action'>⚡ ACTION</div>
                    <div class='step-title'>{step["action"]}</div>
                </div>""", unsafe_allow_html=True)
                st.markdown("<br>")
            elif step["type"] == "decision":
                st.markdown(f"""
                <div class='step-card sc-decision'>
                    <div class='step-badge b-decision'>🔀 DECISION POINT</div>
                    <div class='step-title'>{step["label"]}</div>
                    <div class='step-body'>Assess the newborn and select the finding:</div>
                </div>""", unsafe_allow_html=True)
                st.markdown("<br>")
                for br in step.get("branches", []):
                    cond = br.get("condition","")
                    if "Spontaneous" in cond and "100" in cond:
                        btn_cls = "btn-yes"
                    elif "inadequate" in cond.lower():
                        btn_cls = "btn-no"
                    else:
                        btn_cls = "btn-warn"
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.markdown(f"<div class='{btn_cls}'>", unsafe_allow_html=True)
                        if st.button(cond, key=f"sd_{br['id']}", use_container_width=True):
                            st.session_state.node_stack.append((cond, br))
                            st.session_state.history.append(cond)
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                # stop rendering more steps — wait for choice
                break

    # ── "next" node: reassessment or decision ─────────────────────────────────
    elif "next" in node:
        nxt = node["next"]
        lbl   = nxt.get("label","")
        ntype = nxt.get("type","")

        if ntype == "reassessment":
            sc, bc = "sc-reassess", "b-reassess"
            icon = "🔄 REASSESSMENT"
        else:
            sc, bc = "sc-decision", "b-decision"
            icon = "🔀 DECISION"

        st.markdown(f"""
        <div class='step-card {sc}'>
            <div class='step-badge {bc}'>{icon}</div>
            <div class='step-title'>{lbl}</div>
            <div class='step-body'>Select the clinical result:</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>")

        if "branches" in nxt:
            for br in nxt["branches"]:
                cond = br.get("condition","")
                if "✅" in cond or "improved" in cond.lower() or "increased" in cond.lower():
                    btn_cls = "btn-yes"
                elif "no increase" in cond.lower() or "remains" in cond.lower():
                    btn_cls = "btn-no"
                else:
                    btn_cls = "btn-warn"
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown(f"<div class='{btn_cls}'>", unsafe_allow_html=True)
                    if st.button(cond, key=f"nxt_{br['id']}", use_container_width=True):
                        st.session_state.node_stack.append((cond, br))
                        st.session_state.history.append(cond)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            # terminal reassessment
            st.markdown(f"""
            <div class='step-card sc-reassess' style='text-align:center;'>
                <div class='step-badge b-reassess'>🔄 CONTINUE MONITORING</div>
                <div class='step-title'>Reassess every 30 seconds</div>
            </div>""", unsafe_allow_html=True)
            st.markdown("<br>")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("↩ Start New Assessment", use_container_width=True, key="rst_term"):
                    reset(); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            st.stop()

    # ── Inline branches (no "next", no "steps") ────────────────────────────────
    elif "branches" in node and "steps" not in node:
        for br in node["branches"]:
            cond = br.get("condition","")
            if "✅" in cond or "Spontaneous" in cond:
                btn_cls = "btn-yes"
            elif "inadequate" in cond.lower() or "no " in cond.lower():
                btn_cls = "btn-no"
            else:
                btn_cls = "btn-warn"
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"<div class='{btn_cls}'>", unsafe_allow_html=True)
                if st.button(cond, key=f"inl_{br['id']}", use_container_width=True):
                    st.session_state.node_stack.append((cond, br))
                    st.session_state.history.append(cond)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    # ── Fallback terminal ──────────────────────────────────────────────────────
    elif "next" not in node and "branches" not in node and "steps" not in node and "outcome" not in node:
        st.markdown("""
        <div class='step-card sc-reassess' style='text-align:center;'>
            <div class='step-badge b-reassess'>🔄 CONTINUE MONITORING</div>
            <div class='step-title'>Reassess every 30 seconds and escalate as needed</div>
        </div>""", unsafe_allow_html=True)

    # ── Back / Restart nav ─────────────────────────────────────────────────────
    st.markdown("<br>")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        ca, cb = st.columns(2)
        with ca:
            if st.button("← Back", use_container_width=True, key="back_wiz"):
                go_back(); st.rerun()
        with cb:
            if st.button("↩ Restart", use_container_width=True, key="rst_wiz"):
                reset(); st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
