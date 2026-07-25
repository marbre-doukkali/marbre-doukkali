import streamlit as st
import pandas as pd
import io
import random
from datetime import datetime

# 1. إعدادات الهوية الروحية البصرية الجديدة لورشة رخام دكالة
st.set_page_config(page_title="Marbrerie ERP - Marbre Doukkali", page_icon="Ⓜ️", layout="wide")

# ديزاين الـ CSS الروحاني المخصص لتغيير اللون الأبيض الكلاسيكي ورسم شعار الحرف M النوراني
st.markdown("""
    <style>
    /* تغيير الخلفية البيضاء الكلاسيكية إلى مظهر روحاني عميق */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    /* تصميم شعار الـ M الأزرق الروحاني محاطاً بالهالة النورانية */
    .spiritual-logo {
        text-align: center;
        padding: 20px;
        background: radial-gradient(circle, rgba(30,58,138,0.6) 0%, rgba(15,23,42,0) 70%);
        border-radius: 50%;
        margin-bottom: 25px;
    }
    .spiritual-m {
        font-family: 'Georgia', serif;
        font-size: 75px;
        font-weight: bold;
        color: #38bdf8;
        text-shadow: 0 0 20px #1d4ed8, 0 0 40px #1e40af, 0 0 60px #60a5fa;
        animation: pulse 3s infinite alternate;
    }
    @keyframes pulse {
        0% { transform: scale(1); text-shadow: 0 0 20px #1d4ed8; }
        100% { transform: scale(1.05); text-shadow: 0 0 40px #60a5fa; }
    }
    /* زخرفة العناوين باللون الذهبي الرخامي */
    h1, h2, h3 {
        color: #f59e0b !important;
        text-shadow: 1px 1px 2px #000;
        text-align: right;
    }
    .stButton>button {
        background-color: #1e3a8a !important;
        color: #f8fafc !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #38bdf8 !important;
        color: #0f172a !important;
    }
    div[data-testid="stSidebar"] {
        background-color: #1e293b !important;
    }
    </style>
""", unsafe_allow_html=True)

PASSWORD_SECRET = "2017@2026"

if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False

if not st.session_state["authentifie"]:
    st.markdown("<div class='spiritual-logo'><div class='spiritual-m'>M</div></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>🔒 نظام رخام دكالة الروحاني - تسجيل الدخول</h2>", unsafe_allow_html=True)
    mot_de_passe = st.text_input("أدخل الرقم السري الخاص بالفريق :", type="password")
    if st.button("تسجيل الدخول للنظام"):
        if mot_de_passe == PASSWORD_SECRET:
            st.session_state["authentifie"] = True
            st.rerun()
        else:
            st.error("الرقم السري غير صحيح.")
    st.stop()

# تفعيل الذاكرة الحية المستقلة بنسبة 100% لضمان عمل الملفات والكوغباي بدون كراش
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

# القائمة الجانبية المنسقة بالنمط الروحاني الداكن
st.sidebar.markdown("<div class='spiritual-logo'><div class='spiritual-m' style='font-size:40px;'>M</div></div>", unsafe_allow_html=True)
st.sidebar.markdown("<h3 style='text-align: center; color: #38bdf8;'>لوحة التحكم والفرز</h3>", unsafe_allow_html=True)
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
        input_des = st.text_input("بيان مخصص (إذا اخترت أخرى) :", "Élément unique") if choix_des == "Autre (كتابة مخصصة)" else choix_des
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
        st.markdown("### 📊 القطع المدرجة بالملف")
        df_panier = pd.DataFrame(st.session_state["panier_actuel"])
        st.dataframe(df_panier, use_container_width=True)

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
                    "ID unique": id_commande, "Date Commande": date_actuelle, "N° Dossier": label_fichier,
                    "Client": nom_client, "Responsable": responsable_commande, "Désignation": item["Désignation"],
                    "Matériau": item["Matériau"], "Dimensions": item["Dimensions"], "Quantité": item["Quantité"],
                    "Surface (m2)": item["Surface (m2)"], "Total HT (DH)": item["Total HT (DH)"],
                    "Total HT Commande (DH)": round(total_ht, 2), "Total TTC (DH)": round(total_net, 2),
                    "Avance (DH)": round(avance, 2), "Reste (DH)": round(reste_a_payer, 2)
                })
            st.session_state["panier_actuel"] = []
            st.success("✅ تم حفظ وتأمين الملف بنجاح في الأرشيف الموحد!")
            st.rerun()

# ================= القسم 2 : الأرشيف والبحث الذكي الموحد =================
elif page == "🗂️ الأرشيف والبحث الذكي":
    st.markdown("<h1>🗂️ أرشيف المبيعات والفرز الذكي</h1>", unsafe_allow_html=True)

    if not st.session_state["historique_commandes"]:
        st.info("الأرشيف فارغ حالياً.")
    else:
        df_hist = pd.DataFrame(st.session_state["historique_commandes"])

        recherche = st.text_input("🔍 صندوق البحث السريع الموحد (اكتب اسم البائع أو الزبون لفرز الملفات فورا):", key="search_inside_folder")
        if recherche:
            req = recherche.lower().strip()
            cond_dossier = df_hist['N° Dossier'].astype(str).str.lower().str.contains(req, na=False)
            cond_client = df_hist['Client'].astype(str).str.lower().str.contains(req, na=False)
            cond_vendeur = df_hist['Responsable'].astype(str).str.lower().str.contains(req, na=False)
            df_filtered = df_hist[cond_dossier | cond_client | cond_vendeur]
        else:
            df_filtered = df_hist

        st.dataframe(df_filtered, use_container_width=True)

        st.markdown("### 🗑️ نقل ملف كامل إلى سلة المهملات (Corbeille)")
        list_docs = sorted(list(df_filtered['N° Dossier'].astype(str).unique()))
        dossier_a_supprimer = st.selectbox("إختر رقم الملف للنقل :", list_docs)

        if st.button("❌ نقل إلى الكوغباي"):
            # تصفية وفصل الملف المختار بشكل برمي دقيق شغال 100% وبدون اخطاء
            lignes_a_conserver = [c for c in st.session_state["historique_commandes"] if str(c["N° Dossier"]) != str(dossier_a_supprimer)]
