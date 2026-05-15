import streamlit as st
import json

# إعداد صفحة التطبيق
st.set_page_config(page_title="Neonatal Life Support (NLS)", layout="wide", page_icon="👶")

# دالة لتحميل البيانات من ملف JSON
@st.cache_data
def load_data():
    # تأكد من أن ملف nls_guideline.json موجود في نفس مسار السكريبت
    with open('nls_guideline.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# دالة عودية (Recursive) لرسم مسار القرارات الطبي بشكل متدفق
def render_node(node, key_prefix):
    # عرض الإجراءات المطلوبة إن وجدت
    if "action" in node:
        st.info(f"⚡ **الإجراء المطلوب (Action):**\n{node['action']}")
    
    # عرض الاعتبارات الطبية الإضافية
    if "considerations" in node:
        st.warning("**اعتبارات إضافية يجب التفكير بها (Considerations):**\n" + 
                   "\n".join([f"- {c}" for c in node['considerations']]))
                   
    # عرض الملاحظات
    if "note" in node:
        st.caption(f"📝 ملاحظة: {node['note']}")

    # إذا كان هناك تفرعات (قرارات يجب اتخاذها)
    if "branches" in node:
        options = {b.get("condition", "متابعة"): b for b in node["branches"]}
        # استخدام st.radio كأداة تفاعلية للتدفق
        choice = st.radio("ما هي حالة الطفل الآن؟", list(options.keys()), key=key_prefix, index=None)
        
        if choice:
            selected_branch = options[choice]
            
            # عرض النتيجة النهائية إذا وصلنا إليها
            if "outcome_label" in selected_branch:
                icon = selected_branch.get('icon', '✅')
                st.success(f"{icon} **القرار النهائي:** {selected_branch['outcome_label']}")
            
            # عرض الإجراء الخاص بالفرع المختار
            if "action" in selected_branch:
                st.info(f"⚡ **الإجراء (Action):** {selected_branch['action']}")
            
            # إذا كان هناك خطوات متسلسلة داخل هذا الفرع
            if "steps" in selected_branch:
                for i, step in enumerate(selected_branch["steps"]):
                    st.markdown("---")
                    if "label" in step:
                        st.subheader(step["label"])
                    render_node(step, key_prefix + f"_step_{i}")
                    
            # إذا كان هناك عقدة تالية (Next) للتقييم
            if "next" in selected_branch:
                st.markdown("---")
                if "label" in selected_branch["next"]:
                    st.subheader(selected_branch["next"]["label"])
                render_node(selected_branch["next"], key_prefix + "_next")

def main():
    data = load_data()
    
    # العنوان الرئيسي
    st.title(data["title"])
    st.caption(f"الإصدار: {data['version']}")

    # الشريط الجانبي لعرض أهداف الإشباع الأكسجيني
    with st.sidebar:
        st.header(data["target_spo2"]["label"])
        for val in data["target_spo2"]["values"]:
            st.write(f"- **{val['time']}**: {val['range']}")

    # 1. فلتر عمر الحمل (Gestational Age)
    st.header("1. تحديد عمر الحمل (Gestational Age)")
    pathways = {p["label"]: p for p in data["pathways"]}
    selected_ga_label = st.radio("اختر الفئة العمرية:", list(pathways.keys()), index=None)

    # 2. التدفق المعتمد على عمر الحمل
    if selected_ga_label:
        pathway = pathways[selected_ga_label]
        
        st.markdown("---")
        st.subheader("الإجراءات الأولية (Initial Actions)")
        for action in pathway["initial_actions"]:
            st.write(f"✅ {action}")
            
        st.markdown("---")
        st.subheader(pathway["assessment"]["label"])
        
        # استدعاء الدالة العودية لبدء التقييم
        render_node(pathway["assessment"], key_prefix="main_assessment")

if __name__ == "__main__":
    main()
