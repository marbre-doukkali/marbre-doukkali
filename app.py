import streamlit as st
import pandas as pd
import io
import random
from datetime import datetime

# 1. إعدادات الهوية البصرية الرخامية المتباينة عالية الوضوح والأعمدة الهندسية
st.set_page_config(page_title="Marbrerie ERP - Marbre Doukkali", page_icon="Ⓜ️", layout="wide")

# تصميم الـ CSS: واجهة الرخام الأبيض الفخم المتباين شديد الوضوح في القراءة والفرز
st.markdown("""
    <style>
    .stApp {
        background-color: #111827;
        color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .marble-logo-box {
        text-align: center;
        padding: 20px;
        background: radial-gradient(circle, rgba(14,116,144,0.3) 0%, rgba(17,24,39,0) 70%);
        border: 2px solid #06b6d4;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .marble-m-text {
        font-size: 75px;
        font-weight: bold;
        color: #22d3ee;
        text-shadow: 2px 2px 4px #000000;
    }
    .marble-panel {
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        background-image: radial-gradient(rgba(148,163,184,0.15) 1px, transparent 0);
        background-size: 24px 24px;
        color: #0f172a !important;
        padding: 25px;
        border-radius: 12px;
        border-left: 8px solid #f59e0b;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        margin-bottom: 25px;
    }
    .marble-panel h2, .marble-panel p {
        color: #0f172a !important;
        font-weight: bold !important;
    }
    h1, h2, h3 {
        color: #f59e0b !important;
        text-shadow: 1px 1px 2px #000000;
        text-align: right;
    }
    .stButton>button {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 2px solid #f59e0b !important;
        border-radius: 6px;
        font-weight: bold;
        font-size: 16px;
        padding: 8px 20px;
    }
    .stButton>button:hover {
        background-color: #f59e0b !important;
        color: #0f172a !important;
        border: 2px solid #ffffff !important;
    }
    div[data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    </style>
""", unsafe_allow_html=True)

PASSWORD_SECRET = "2017@2026"

if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False

if not st.session_state["authentifie"]:
    st.markdown("""
        <div class='marble-logo-box'>
            <div class='marble-m-text'>M</div>
        </div>
        <div style='text-align: center; font-size: 24px; font-weight: bold; color: #ffffff; margin-bottom: 20px;'>Ⓜ️ نظام مبيعات رخام دكالة العصري</div>
    """, unsafe_allow_html=True)

    mot_de_passe = st.text_input("أدخل الرقم السري الخاص بالفريق :", type="password")
    if st.button("تسجيل الدخول للنظام"):
        if mot_de_passe == PASSWORD_SECRET:
            st.session_state["authentifie"] = True
            st.rerun()
        else:
            st.error("الرقم السري غير صحيح.")
    st.stop()

# تفعيل قنوات الذاكرة المستقرة لحماية الملفات والكوغات من التداخل والضياع
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

# اللوحة الجانبية
st.sidebar.markdown("""
    <div class='marble-logo-box' style='padding:10px; margin-bottom:10px;'>
        <div class='marble-m-text' style='font-size:35px;'>M</div>
    </div>
""", unsafe_allow_html=True)
st.sidebar.markdown("<h3 style='text-align: center; color: #22d3ee; margin-top:0;'>نظام مبيعات دكالة</h3>", unsafe_allow_html=True)
page = st.sidebar.radio("📋 الانتقال بين الأقسام :", ["📝 تسجيل الطلبيات الجديدة", "🗂️ الأرشيف والبحث الذكي", "🗑️ سلة المهملات (Corbeille)"])

if st.sidebar.button("🔒 تسجيل الخروج"):
    st.session_state["authentifie"] = False
    st.rerun()

# ================= القسم 1 : تسجيل الطلبيات الجديدة =================
if page == "📝 تسجيل الطلبيات الجديدة":
    st.markdown("<h1>📝 تدوين وتسجيل الطلبيات الجديدة</h1>", unsafe_allow_html=True)

    if st.button("🆕 ملف جديد (تفريغ الاستمارة)"):
        st.session_state["panier_actuel"] = []
        st.rerun()

    st.markdown("### 📂 1. معلومات الملف والزبون")
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        label_fichier = st.text_input("N° Dossier / رقم الملف :", "DOS-2026-001")
    with col_info2:
        nom_client = st.text_input("اسم الزبون الحالي :", "Client_Anonyme")
    with col_info3:
        responsable_commande = st.text_input("المسؤول عن المتابعة (البائع) :", "الطوسي")

    st.markdown("### 🧱 2. مقاسات وأنواع الرخام")
    col_in1, col_in2, col_in3, col_in4 = st.columns(4)
    with col_in1:
        choix_des = st.selectbox("Désignation (البيان) :", liste_designations_prefere)
        input_des = st.text_input("بيان مخصص :", "Élément unique") if choix_des == "Autre (كتابة مخصصة)" else choix_des
    with col_in2:
        input_mat = st.selectbox("Matériau (نوع الرخام) :", liste_options_materiaux)
    with col_in3:
        input_long = st.number_input("الطول (m) :", min_value=0.01, value=1.00, step=0.01)
    with col_in4:
        input_larg = st.number_input("العرض (m) :", min_value=0.01, value=0.30, step=0.01)

    input_qte = st.number_input("الكمية (Quantité) :", min_value=1, value=1, step=1)

    if st.button("➕ إضافة هذه القطعة للطلب الحالي"):
        p_m2 = prix_materiaux.get(input_mat, 600)
        surf = input_long * input_larg * input_qte
        tot_ligne = surf * p_m2

        st.session_state["panier_actuel"].append({
            "Désignation": input_des, "Matériau": input_mat.upper(), "Dimensions": f"{input_long}x{input_larg}",
            "Quantité": input_qte, "Surface (m2)": round(surf, 2), "Total HT (DH)": round(tot_ligne, 2)
        })
        st.toast("تمت الإضافة بنجاح! 💎")

    if st.session_state["panier_actuel"]:
        st.markdown("### 📊 القطع المدرجة بالملف الحالي")
        df_panier = pd.DataFrame(st.session_state["panier_actuel"])
        st.dataframe(df_panier, use_container_width=True)

        st.markdown("##### 🛠️ تعديل محتوى الاستمارة الحالية (حذف قطعة واحدة فقط معينة من الجدول الحاضر):")
        index_a_supprimer = st.number_input("أدخل رقم السطر المراد حذفه من الجدول أعلاه (يبدأ من 0) :", min_value=0, max_value=len(st.session_state["panier_actuel"])-1, step=1)
        if st.button("❌ حذف هذه القطعة المحددة فقط"):
            st.session_state["panier_actuel"].pop(index_a_supprimer)
            st.success("تم حذف السلعة المحددة من الجدول الحاضر!")
            st.rerun()

        total_ht = df_panier["Total HT (DH)"].sum()
        total_ttc = total_ht * 1.2

        remise = st.number_input("نسبة التخفيض (%) Remise :", min_value=0.0, max_value=100.0, value=0.0)
        avance = st.number_input("مبلغ التسبيق المدفوع (DH) :", min_value=0.0, value=0.0)

        montant_remise = total_ttc * (remise / 100)
        total_net = total_ttc - montant_remise
        reste_a_payer = total_net - avance

        st.markdown(f"#### الصافي المطلوب دفعه : {total_net:.2f} DH | المتبقي : {reste_a_payer:.2f} DH")

        if st.button("💾 ENREGISTRER DEFINITIVEMENT DANS L'HISTORIQUE"):
            date_actuelle = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            id_commande = f"CMD-{random.randint(10000, 99999)}"

            for item in st.session_state["panier_actuel"]:
                st.session_state["historique_commandes"].append({
                    "ID unique": id_commande,
                    "Date Commande": date_actuelle,
                    "N° Dossier": str(label_fichier).strip(),
                    "Client": nom_client,
                    "Responsable": responsable_commande,
                    "Désignation": item["Désignation"],
                    "Matériau": item["Matériau"],
                    "Dimensions": item["Dimensions"],
                    "Quantité": item["Quantité"],
                    "Surface (m2)": item["Surface (m2)"],
                    "Total HT (DH)": item["Total HT (DH)"],
                    "Total HT Commande (DH)": round(total_ht, 2),
                    "Total TTC (DH)": round(total_net, 2),
                    "Avance (DH)": round(avance, 2),
                    "Reste (DH)": round(reste_a_payer, 2)
                })
            st.session_state["panier_actuel"] = []
            st.success("✅ تم حفظ وتأمين الملف بنجاح في الأرشيف الموحد!")
            st.rerun()

# ================= القسم 2 : الأرشيف والبحث الذكي الموحد =================
elif page == "🗂️ الأرشيف والبحث الذكي":
    st.markdown("""
        <div class='marble-panel'>
            <h2 style='color:#0f172a !important; text-align:right; margin:0;'>🗂️ نظام إدارة مبيعات دكالة - الفرز الرخامي الذكي</h2>
            <p style='color:#334155 !important; text-align:right;'>هنا تجد كافة الطلبيات المحفوظة منسقة داخل واجهة رخامية كلاسيكية متباينة الألوان لسهولة تامة في القراءة والبحث البصري الحاد.</p>
        </div>
