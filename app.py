import streamlit as st
import pandas as pd
import io
import random
from datetime import datetime

# استدعاء آمن ومحمي لمكتبة الذكاء الاصطناعي والتنبؤ XGBoost والـ Compiler لضمان الجودة الحسابية
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

st.set_page_config(page_title="Marbrerie ERP - Marbre Doukkali", page_icon="Ⓜ️", layout="wide")

# تخصيص الـ CSS وتصميم حرف M كبير وفخم مزخرف بألوان وعروق الرخام الطبيعي الصافي لحذف التشتت البصري
st.markdown("""
<style>
.stApp {
    background-color: #030712;
    background-image: radial-gradient(#ffffff 0.7px, transparent 1px);
    background-size: 35px 35px;
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
}
/* حاوية عرض حرف M الرخامي الفخم */
.industrial-marble-m {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 30px;
    background: linear-gradient(180deg, #111827 0%, #030712 100%);
    border: 2px solid #4b5563;
    border-radius: 12px;
    margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.8);
}
/* زخرفة وتلوين حرف M بألوان تدرجات الرخام الطبيعي وعروقه المصقولة الفخمة */
.luxury-marble-text {
    font-size: 130px;
    font-weight: 900;
    font-family: 'Georgia', serif;
    background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 25%, #f59e0b 50%, #475569 75%, #1e293b 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(4px 4px 15px rgba(255,255,255,0.15));
    text-shadow: 0px 0px 2px rgba(0, 0, 0, 0.8);
    letter-spacing: -5px;
    line-height: 1;
}
/* حجم الحرف المصغر المخصص للقائمة الجانبية */
.luxury-marble-text-sidebar {
    font-size: 65px;
}
.industrial-title {
    font-size: 30px;
    font-weight: bold;
    color: #ffffff;
    text-align: center;
    margin-top: 15px;
    text-shadow: 2px 2px 4px #000000;
}
h1, h2, h3 {
    color: #ffffff !important;
    text-shadow: 1px 1px 3px #000000;
    text-align: right;
    border-bottom: 1px solid #374151;
    padding-bottom: 8px;
}
.stButton>button {
    background-color: #1f2937 !important;
    color: #ffffff !important;
    border: 2px solid #cbd5e1 !important;
    border-radius: 6px;
    font-weight: bold;
    font-size: 16px;
    padding: 8px 20px;
}
.stButton>button:hover {
    background-color: #ffffff !important;
    color: #030712 !important;
    border: 2px solid #ffffff !important;
}
div[data-testid='stSidebar'] {
    background-color: #0f172a !important;
}
.marble-panel {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    color: #0f172a !important;
    padding: 25px;
    border-radius: 12px;
    border-left: 8px solid #475569;
    margin-bottom: 25px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.5);
}
</style>
""", unsafe_allow_html=True)

PASSWORD_SECRET = "2017@2026"

if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False

# بوابة حماية الدخول بحرف M الرخامي الكبير الفخم
if not st.session_state["authentifie"]:
    st.markdown("<div class='industrial-marble-m'><div class='luxury-marble-text'>M</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='industrial-title'>مرحباً بك في نظام إدارة ومبيعات رخام دكالة</div>", unsafe_allow_html=True)
    mot_de_passe = st.text_input("أدخل الرقم السري الخاص بالفريق :", type="password")
    if st.button("تسجيل الدخول للنظام الآمن"):
        if mot_de_passe == PASSWORD_SECRET:
            st.session_state["authentifie"] = True
            st.rerun()
        else:
            st.error("الرقم السري غير صحيح.")
    st.stop()

if "historique_commandes" not in st.session_state:
    st.session_state["historique_commandes"] = []

if "corbeille_commandes" not in st.session_state:
    st.session_state["corbeille_commandes"] = []

if "panier_actuel" not in st.session_state:
    st.session_state["panier_actuel"] = []

prix_materiaux = {
    "marmer": 600, "crema_marfil": 650, "carrara": 1100, "calacatta": 1800,
    "statuario": 2200, "nero_marquina": 750, "emperador_fonce": 800, "emperador_clair": 700,
    "vert_guatemala": 850, "blanc_ibiza": 650, "thassos": 1900, "travertin": 450,
    "marbre_taza": 350, "marbre_khouribga": 280, "kadenza": 400, "halabi": 450,
    "palmoral": 800, "rosavel": 500, "labrador_noir": 1150, "zimbabwe": 1200,
    "gris_moncai": 500, "noir_galaxy": 1050, "gris_espagnol": 520, "mondariz_clair": 500,
    "angola": 1000, "perla": 500, "baltic_brown": 800, "rafaela": 500,
    "labrador_bleu": 1150, "mondariz_fonce": 500, "multicolore": 1400, "rosy": 400
}
liste_options_materiaux = sorted(list(prix_materiaux.keys()))
liste_designations_prefere = ["Escalier (درج)", "Plan de cuisine (مطبخ)", "Revêtement de sol (أرضية)", "Plinthe (حزام)", "Seuil de porte (عتبة)", "Autre (كتابة مخصصة)"]
liste_responsables = ["الطوسي (El Tossi)", "Nadim Jadoui", "Responsable Standard"]

# شريط التنقل الجانبي يظهر في أعلاه حرف M الرخامي بحجم مصغر ومتناسق
st.sidebar.markdown("<div class='industrial-marble-m' style='padding:10px; margin-bottom:10px;'><div class='luxury-marble-text luxury-marble-text-sidebar'>M</div></div>", unsafe_allow_html=True)
st.sidebar.markdown("<h3 style='text-align: center; color: #ffffff; margin-top:0;'>نظام مبيعات دكالة</h3>", unsafe_allow_html=True)
page = st.sidebar.radio("📋 الانتقال بين الأقسام :", ["📝 تسجيل الطلبيات الجديدة", "🗂️ الأرشيف والبحث الذكي والطباعة", "🗑️ سلة المهملات (Corbeille)"])

if st.sidebar.button("🔒 تسجيل الخروج"):
    st.session_state["authentifie"] = False
    st.rerun()

# ================= القسم 1 : تسجيل الطلبيات الجديدة =================
if page == "📝 تسجيل الطلبيات الجديدة":
    st.markdown("<h1>📝 تدوين وتسجيل الطلبيات الجديدة للمصنع</h1>", unsafe_allow_html=True)
    if st.button("🆕 ملف جديد (تفريغ الاستمارة بالكامل)"):
        st.session_state["panier_actuel"] = []
        st.rerun()

    st.markdown("### 📂 1. معلومات الملف والزبون")
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        label_fichier = st.text_input("N° Dossier / رقم الملف الحالي :", "DOS-2026-001")
    with col_info2:
        nom_client = st.text_input("اسم الزبون المعني :", "Client_Anonyme")
    with col_info3:
        responsable_commande = st.selectbox("المسؤول عن المتابعة (البائع) :", liste_responsables, index=0)

    st.markdown("### 🧱 2. مقاسات وأنواع الرخام المطلوبة")
    col_in1, col_in2, col_in3, col_in4 = st.columns(4)
    with col_in1:
        choix_des = st.selectbox("Désignation (البيان ثنائي اللغة) :", liste_designations_prefere)
        input_des = st.text_input("اكتب بيان مخصص :", "Élément unique") if choix_des == "Autre (كتابة مخصصة)" else choix_des
    with col_in2:
        input_mat = st.selectbox("Matériau (نوع الرخام من الخزينة) :", liste_options_materiaux)
    with col_in3:
        input_long = st.number_input("الطول المطلوب (m) :", min_value=0.01, value=1.00, step=0.01)
    with col_in4:
        input_larg = st.number_input("العرض المطلوب (m) :", min_value=0.01, value=0.30, step=0.01)
    input_qte = st.number_input("الكمية العددية (Quantité) :", min_value=1, value=1, step=1)

    if st.button("➕ إضافة هذه القطعة للجدول الحالي"):
        p_m2 = prix_materiaux.get(input_mat, 600)
        surf = input_long * input_larg * input_qte
        tot_ligne = surf * p_m2
        # [إصلاح حاسم] تم تصحيح المتغير التالف ليعمل بـ input_larg كلياً ويمنع خطأ الـ NameError والكراش
        st.session_state["panier_actuel"].append({
            "Désignation": input_des,
            "Matériau": input_mat.upper(),
            "Dimensions": f"{input_long}x{input_larg}",
            "Quantité": input_qte,
            "Surface (m2)": round(surf, 2),
            "Total HT (DH)": round(tot_ligne, 2)
        })
        st.toast("تمت إضافة القطعة بنجاح لسلّة الزبون! 💎")

    if st.session_state["panier_actuel"]:
        st.markdown("### 📊 القطع المدرجة بالملف الحاضر")
        df_panier = pd.DataFrame(st.session_state["panier_actuel"])
        st.dataframe(df_panier, use_container_width=True)

        st.markdown("##### 🛠️ تعديل الاستمارة الحالية (حذف سطر معين):")
        index_a_supprimer = st.number_input("أدخل رقم السطر المراد حذفه (يبدأ من 0) :", min_value=0, max_value=len(st.session_state["panier_actuel"])-1, step=1)
        if st.button("❌ حذف هذه القطعة المحددة فقط"):
            st.session_state["panier_actuel"].pop(index_a_supprimer)
            st.success("تم حذف السلعة المحددة من الجدول الحاضر!")
            st.rerun()

        total_ht = df_panier["Total HT (DH)"].sum()
        total_ttc = total_ht * 1.2
        remise = st.number_input("نسبة التخفيض التجاري الممنوح (%) Remise :", min_value=0.0, max_value=100.0, value=0.0)
        avance = st.number_input("مبلغ التسبيق المستلم نقداً (DH) :", min_value=0.0, value=0.0)

        montant_remise = total_ttc * (remise / 100)
        total_net = total_ttc - montant_remise
        reste_a_payer = total_net - avance

        # [إصلاح حاسم] عزل رمز النسبة المئوية كلياً لمنع حدوث خطأ unterminated f-string وصدمة الواجهة
        sym_p = "%"
        st.markdown(f"""
        <div class='marble-panel'>
            <h3 style='color:#0f172a !important; border-bottom:2px solid #0f172a;'>🧾 تفاصيل كشف الحساب المالي للملف الحالي</h3>
            <p>💰 إجمالي مجموع السعر قبل الاحتساب (HT): <b>{total_ht:,.2f} DH</b></p>
            <p>📈 إجمالي السعر شامل رسوم الضريبة (TTC 20%): <b>{total_ttc:,.2f} DH</b></p>
            <p>📉 قيمة التخفيض التجاري المنفذ: <b>{montant_remise:,.2f} DH ({remise:,.1f}{sym_p})</b></p>
            <p>⭐ الصافي الإجمالي المطلوب دفعه (NET): <span style='font-size:20px; color:#15803d;'><b>{total_net:,.2f} DH</b></span></p>
            <p>💵 مبلغ التسبيق المدفوع بالخزينة (Avance): <b>{avance:,.2f} DH</b></p>
            <p>🚨 الباقي استخلاصه بذمة الزبون الحالي: <span style='font-size:20px; color:#b91c1c;'><b>{reste_a_payer:,.2f} DH</b></span></p>
        </div>
        """, unsafe_allow_html=True)
