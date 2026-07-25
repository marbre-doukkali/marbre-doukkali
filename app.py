import streamlit as st
import pandas as pd
import io
import random
from datetime import datetime

# استدعاء آمن ومحمي لمكتبة الذكاء الاصطناعي والتنبؤ XGBoost
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

# 1. إعداد الصفحة وتخصيص المظهر الصناعي لشركة رخام دكالة
st.set_page_config(page_title="Marbrerie ERP - Marbre Doukkali", page_icon="Ⓜ️", layout="wide")

# تخصيص الـ CSS وبناء تصميم هندسي مزخرف وحقيقي لحرف M بألوان متعددة ومتداخلة
st.markdown("""
<style>
.stApp {
    background-color: #030712;
    background-image: radial-gradient(#ffffff 0.7px, transparent 1px);
    background-size: 35px 35px;
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
}
/* حاوية حرف M الهندسية المزخرفة */
.industrial-marble-m {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 180px;
    padding: 20px;
    background: linear-gradient(180deg, #111827 0%, #030712 100%);
    border: 2px solid #4b5563;
    border-radius: 12px;
    margin-bottom: 30px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.8);
}
/* الهيكل البنائي المتصل لرسم الـ M الحقيقي بزوايا مائلة وألوان متعددة */
.m-letter-container {
    display: flex;
    align-items: flex-start;
    height: 140px;
    position: relative;
}
.m-leg {
    width: 24px;
    height: 140px;
    border-radius: 4px;
    box-shadow: 3px 3px 10px rgba(0,0,0,0.5);
}
/* ألوان الطيف الرخامي والجرانيتي المزخرف */
.leg-left {
    background: linear-gradient(180deg, #f59e0b 0%, #d97706 50%, #b45309 100%); /* تدرج ذهبي ملكي */
    border: 1px solid #f59e0b;
}
.leg-right {
    background: linear-gradient(180deg, #3b82f6 0%, #2563eb 50%, #1d4ed8 100%); /* تدرج أزرق Labrador */
    border: 1px solid #3b82f6;
}
.m-diagonal {
    width: 22px;
    height: 110px;
    margin-top: 5px;
    border-radius: 4px;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.4);
}
.diag-left {
    transform: rotate(28deg);
    transform-origin: top left;
    margin-left: 8px;
    background: linear-gradient(180deg, #ef4444 0%, #dc2626 50%, #b91c1c 100%); /* تدرج أحمر عقيق */
    border: 1px solid #ef4444;
}
.diag-right {
    transform: rotate(-28deg);
    transform-origin: top right;
    margin-right: 8px;
    background: linear-gradient(180deg, #10b981 0%, #059669 50%, #047857 100%); /* تدرج أخضر جواتيمالا */
    border: 1px solid #10b981;
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

# إدارة متغيرات الجلسة السحابية والتحقق من الهوية
if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False

if "historique_commandes" not in st.session_state:
    st.session_state["historique_commandes"] = []

if "corbeille_commandes" not in st.session_state:
    st.session_state["corbeille_commandes"] = []

if "lignes_commande" not in st.session_state:
    st.session_state["lignes_commande"] = [
        {"Désignation": "Escalier", "Matériau": "marmer", "Longueur (m)": 1.00, "Largeur (m)": 0.30, "Quantité": 1}
    ]

# شفرة HTML نقية لرسم وتجسيد حرف M المزخرف بـ 4 ألوان فخمة في واجهة الدخول
html_m_rendering = """
<div class='industrial-marble-m'>
    <div class='m-letter-container'>
        <div class='m-leg leg-left'></div>
        <div class='m-diagonal diag-left'></div>
        <div class='m-diagonal diag-right'></div>
        <div class='m-leg leg-right'></div>
    </div>
</div>
"""

# بوابة حماية الدخول بهيكل حرف M المطور والمزخرف بالألوان
if not st.session_state["authentifie"]:
    st.markdown(html_m_rendering, unsafe_allow_html=True)
    st.markdown("<div class='industrial-title'>مرحباً بك في نظام إدارة ومبيعات رخام دكالة</div>", unsafe_allow_html=True)
    mot_de_passe = st.text_input("أدخل الرقم السري الخاص بالفريق المعني :", type="password")
    if st.button("تسجيل الدخول للنظام الآمن"):
        if mot_de_passe == PASSWORD_SECRET:
            st.session_state["authentifie"] = True
            st.rerun()
        else:
            st.error("الرقم السري غير صحيح.")
    st.stop()

# 2. قاعدة بيانات تسعير المواد الخام والجرانيت للمتر المربع (DH)
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
liste_responsables = ["الطوسي (El Tossi)", "Nadim Jadoui", "Responsable Standard"]

# القائمة الجانبية يظهر في أعلاها نفس التصميم المطور والمزخرف لحرف M
st.sidebar.markdown(html_m_rendering.replace("height: 180px;", "height: 110px; padding: 5px;").replace("height: 140px;", "height: 80px;").replace("height: 140px;", "height: 80px;").replace("height: 110px;", "height: 60px;"), unsafe_allow_html=True)
st.sidebar.markdown("<h3 style='text-align: center; color: #ffffff; margin-top:0;'>نظام مبيعات دكالة</h3>", unsafe_allow_html=True)
page = st.sidebar.radio("Navigation", ["📝 Saisie des Commandes", "🗂️ Historique & Recherche", "🗑️ Corbeille (سلة المهملات)"])

if st.sidebar.button("🔒 Se déconnecter"):
    st.session_state["authentifie"] = False
    st.rerun()

# ================= القسم 1 : تسجيل ومتابعة الطلبيات والتركيبات المطور =================
if page == "📝 Saisie des Commandes":
    st.title("📝 Gestion et Creation des Commandes")

    if st.button("🆕 Nouveau Dossier (Vider le formulaire)"):
        st.session_state["lignes_commande"] = [
            {"Désignation": "Escalier", "Matériau": "marmer", "Longueur (m)": 1.00, "Largeur (m)": 0.30, "Quantité": 1}
        ]
        st.rerun()

    st.header("📂 Informations du Dossier actuel")
    col_info1, col_info2, col_info3 = st.columns(3)

    with col_info1:
        label_fichier = st.text_input("N° Dossier / Reference :", "DOS-2026-001")
    with col_info2:
        nom_client = st.text_input("Nom du client :", "Client_Anonyme")
    with col_info3:
        responsable_commande = st.selectbox("Responsable du suivi (Vendeur) :", liste_responsables, index=0)

    st.header("📊 Tableau des Articles (Style Excel)")

    df_form = pd.DataFrame(st.session_state["lignes_commande"])

    edited_df = st.data_editor(
        df_form,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_commande_unique_key",
        column_config={
            "Matériau": st.column_config.SelectboxColumn(
                "Matériau",
                options=liste_options_materiaux,
                required=True
            )
        }
    )

    panier_final = []
    total_ht = 0.0

    for idx, row in edited_df.iterrows():
        des = str(row.get("Désignation", "Nouvel article")).strip()
        if des == "" or pd.isna(row.get("Désignation")): des = "Nouvel article"
        mat = str(row.get("Matériau", "marmer")).strip()
        if mat == "" or pd.isna(row.get("Matériau")): mat = "marmer"

        try:
            long = float(row.get("Longueur (m)", 1.00))
            if long <= 0 or pd.isna(long): long = 1.00
        except: long = 1.00
        try:
            larg = float(row.get("Largeur (m)", 0.30))
            if larg <= 0 or pd.isna(larg): larg = 0.30
        except: larg = 0.30
        try:
            qte = int(row.get("Quantité", 1))
            if qte <= 0 or pd.isna(qte): qte = 1
        except: qte = 1

        p_m2 = prix_materiaux.get(mat.lower(), 600)
        surf = long * larg * qte
        tot_ligne = surf * p_m2
        total_ht += tot_ligne

        panier_final.append({
            "Désignation": des, "Matériau": mat.upper(), "Dimensions": f"{long}x{larg}",
            "Quantité": qte, "Surface (m2)": round(surf, 2), "Total HT (DH)": round(tot_ligne, 2)
        })

    st.header("🧮 Synthese Financiere")
    total_ttc = total_ht * 1.2

    col_finance1, col_finance2 = st.columns(2)
    with col_finance1:
        remise = st.number_input("Remise globale (%)", min_value=0.0, max_value=100.0, value=0.0)
    with col_finance2:
        avance = st.number_input("Somme d'avance versee (DH)", min_value=0.0, value=0.0)

    montant_remise = total_ttc * (remise / 100)
    total_net = total_ttc - montant_remise
    reste_a_payer = total_net - avance

    panel_html = "<div class='marble-panel'>"
    panel_html += "<h3 style='color:#0f172a !important; border-bottom:2px solid #0f172a;'>🧾 الملخص المالي والتركيب الفني</h3>"
    panel_html += f"<p>💰 TOTAL HT : <b>{total_ht:,.2f} DH</b></p>"
    panel_html += f"<p>📈 TOTAL TTC (HT x 1.2) : <b>{total_ttc:,.2f} DH</b></p>"
