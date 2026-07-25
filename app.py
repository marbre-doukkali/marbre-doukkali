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

# تخصيص الـ CSS وتعديل أطوال الأعمدة (الـ Pillars) لتشكيل حرف M هندسي متناسق
st.markdown("""
<style>
.stApp {
    background-color: #030712;
    background-image: radial-gradient(#ffffff 0.7px, transparent 1px);
    background-size: 35px 35px;
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
}
.industrial-marble-m {
    display: flex;
    justify-content: center;
    align-items: flex-end;
    gap: 20px;
    padding: 40px;
    background: linear-gradient(180deg, #1f2937 0%, #030712 100%);
    border: 2px solid #4b5563;
    border-radius: 12px;
    margin-bottom: 30px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.8);
}
.iron-pillar {
    width: 50px;
    background: linear-gradient(90deg, #e2e8f0 0%, #94a3b8 50%, #475569 100%);
    border: 2px solid #64748b;
    border-radius: 3px;
    box-shadow: 5px 5px 15px rgba(0,0,0,0.6), inset -3px -3px 6px rgba(0,0,0,0.4);
}
/* تعديل الارتفاعات لترتيب الأعمدة على شكل حرف M */
.col-1 { height: 140px; }
.col-2 { height: 55px; background: linear-gradient(90deg, #94a3b8 0%, #475569 100%); }
.col-3 { height: 95px; background: linear-gradient(90deg, #64748b 0%, #1e293b 100%); }
.col-4 { height: 55px; background: linear-gradient(90deg, #94a3b8 0%, #475569 100%); }
.col-5 { height: 140px; }
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

# بوابة حماية الدخول بالأعمدة الصناعية المبيانية المترتبة على شكل حرف M
if not st.session_state["authentifie"]:
    st.markdown("<div class='industrial-marble-m'><div class='iron-pillar col-1'></div><div class='iron-pillar col-2'></div><div class='iron-pillar col-3'></div><div class='iron-pillar col-4'></div><div class='iron-pillar col-5'></div></div>", unsafe_allow_html=True)
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

# قائمة الانتقال الجانبية مع الأعمدة الهندسية المصغرة على شكل حرف M أيضاً
st.sidebar.markdown("<div class='industrial-marble-m' style='padding:12px; margin-bottom:10px; gap:6px;'><div class='iron-pillar col-1' style='width:12px; height:45px;'></div><div class='iron-pillar col-2' style='width:12px; height:15px;'></div><div class='iron-pillar col-3' style='width:12px; height:30px;'></div><div class='iron-pillar col-4' style='width:12px; height:15px;'></div><div class='iron-pillar col-5' style='width:12px; height:45px;'></div></div>", unsafe_allow_html=True)
st.sidebar.markdown("<h3 style='text-align: center; color: #ffffff; margin-top:0;'>نظام مبيعات دكالة</h3>", unsafe_allow_html=True)
page = st.sidebar.radio("Navigation", ["📝 Saisie des Commandes", "🗂️ Historique & Recherche", "🗑️ Corbeille (سلة المهملات)"])

if st.sidebar.button("🔒 Se déconnecter"):
    st.session_state["authentifie"] = False
    st.rerun()

# ================= القسم 1 : تسجيل ومتابعة الطلبيات والتركيبات المطور =================
if page == "📝 Saisie des Commandes":
    st.title("📝 Gestion et Création des Commandes")

    if st.button("🆕 Nouveau Dossier (Vider le formulaire)"):
        st.session_state["lignes_commande"] = [
            {"Désignation": "Escalier", "Matériau": "marmer", "Longueur (m)": 1.00, "Largeur (m)": 0.30, "Quantité": 1}
        ]
        st.rerun()

    st.header("📂 Informations du Dossier actuel")
    col_info1, col_info2, col_info3 = st.columns(3)

    with col_info1:
        label_fichier = st.text_input("N° Dossier / Référence :", "DOS-2026-001")
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

    # معالجة وحساب أسطر الجدول بدقة تامة وضمان عدم اختفائها وحساب الأمتار المربعة والتكلفة
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

    st.header("🧮 Synthèse Financière")
    total_ttc = total_ht * 1.2

    col_finance1, col_finance2 = st.columns(2)
    with col_finance1:
        remise = st.number_input("Remise globale (%)", min_value=0.0, max_value=100.0, value=0.0)
    with col_finance2:
        avance = st.number_input("Somme d'avance versée (DH)", min_value=0.0, value=0.0)

    montant_remise = total_ttc * (remise / 100)
    total_net = total_ttc - montant_remise
    reste_a_payer = total_net - avance

    # لوحة الفاتورة والحسابات المالية
    st.markdown(f"""
    <div class='marble-panel'>
        <h3 style='color:#0f172a !important; border-bottom:2px solid #0f172a;'>🧾 الملخص المالي والتركيب الفني</h3>
        <p>💰 TOTAL HT : <b>{total_ht:,.2f} DH</b></p>
        <p>📈 TOTAL TTC (HT x 1.2) : <b>{total_ttc:,.2f} DH</b></p>
        <p>📉 Montant Remise : <b>{montant_remise:,.2f} DH ({remise}%)</b></p>
        <p>⭐ TOTAL NET À PAYER : <span style='font-size:18px; color:#15803d;'><b>{total_net:,.2f} DH</b></span></p>
        <p>💵 Avance : <b>{avance:,.2f} DH</b></p>
        <p>🚨 Reste à payer : <span style='font-size:18px; color:#b91c1c;'><b>{reste_a_payer:,.2f} DH</b></span></p>
    </div>
    """, unsafe_allow_html=True)

    if reste_a_payer <= 0:
        st.success("Facture Entièrement Payée")

