import streamlit as st
import pandas as pd
import io
import os
import random
from datetime import datetime

# 1. إعدادات وتأمين التطبيق مع إضافة لمسة جمالية للعنوان والشعار
st.set_page_config(page_title="Marbrerie ERP - Marbre Doukkali", page_icon="Ⓜ️", layout="wide")

PASSWORD_SECRET = "2017@2026"

if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False

if not st.session_state["authentifie"]:
    st.markdown("<h2 style='text-align: center; color: #1f4e78;'>Ⓜ️ نظام إدارة ورشة رخام دكالة</h2>", unsafe_allow_html=True)
    st.title("🔒 الوصول آمن - تسجيل الدخول")
    mot_de_passe = st.text_input("أدخل الرقم السري الخاص بالفريق :", type="password")
    if st.button("تسجيل الدخول"):
        if mot_de_passe == PASSWORD_SECRET:
            st.session_state["authentifie"] = True
            st.rerun()
        else:
            st.error("الرقم السري غير صحيح. يرجى المحاولة مرة أخرى.")
    st.stop()

# 2. إعداد قاعدة البيانات الصلبة (CSV) لحماية الملفات من الضياع
DB_FILE = "database_marbre.csv"
TRASH_FILE = "database_trash.csv"

def charger_depot(chemin):
    if os.path.exists(chemin):
        try:
            return pd.read_csv(chemin).to_dict(orient="records")
        except:
            return []
    return []

def sauvegarder_depot(donnees, chemin):
    df = pd.DataFrame(donnees)
    df.to_csv(chemin, index=False)

if "historique_commandes" not in st.session_state:
    st.session_state["historique_commandes"] = charger_depot(DB_FILE)

if "corbeille_commandes" not in st.session_state:
    st.session_state["corbeille_commandes"] = charger_depot(TRASH_FILE)

if "panier_actuel" not in st.session_state:
    st.session_state["panier_actuel"] = []

# قاعدة بيانات الرخام والجرانيت
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

# قائمة ديزاينات وخيارات شائعة للتسهيل الميكانيكي على المستخدم عند كتابة الـ Désignation
liste_designations_prefere = ["Escalier (درج)", "Plan de cuisine (مطبخ)", "Revêtement de sol (أرضية)", "Plinthe (حزام)", "Façade (حائط خارجي)", "Seuil de porte (عتبة)", "Autre (كتابة مخصصة)"]

# القائمة الجانبية (Sidebar) المنسقة برمجياً وبصرياً
st.sidebar.markdown("<h2 style='text-align: center; color: #1f4e78;'>Ⓜ️ رخام دكالة</h2>", unsafe_allow_html=True)
st.sidebar.write("---")
page = st.sidebar.radio("📋 الانتقال بين الأقسام :", ["📝 تسجيل الطلبيات الجديدة", "🗂️ الأرشيف والبحث الذكي", "🗑️ سلة المهملات (Corbeille)"])

st.sidebar.write("---")
if st.sidebar.button("🔒 تسجيل الخروج"):
    st.session_state["authentifie"] = False
    st.rerun()

# ================= القسم 1 : تسجيل الطلبيات الجديدة =================
if page == "📝 تسجيل الطلبيات الجديدة":
    st.markdown("<h1 style='color: #1f4e78;'>📝 إدارة وتدوين الطلبيات الجديدة</h1>", unsafe_allow_html=True)
    st.write("قم بملء البيانات أدناه وتدوين تفاصيل الرخام لحساب المساحة والمبالغ المتبقية للزبون تلقائياً.")

    if st.button("🆕 ملف جديد (تفريغ الاستمارة بالكامل)"):
        st.session_state["panier_actuel"] = []
        st.rerun()

    st.markdown("<h3 style='color: #2e75b6;'>📂 1. معلومات الملف والزبون</h3>", unsafe_allow_html=True)
    col_info1, col_info2, col_info3 = st.columns(3)

    with col_info1:
        label_fichier = st.text_input("N° Dossier / رقم الملف المرتبط :", "DOS-2026-001")
    with col_info2:
        nom_client = st.text_input("اسم الزبون الحالي :", "Client_Anonyme")
    with col_info3:
        responsable_commande = st.text_input("المسؤول عن البيع والمتابعة (البائع) :", "الطوسي")

    st.markdown("<h3 style='color: #2e75b6;'>🧱 2. تفاصيل ومقاسات الرخام أو الجرانيت</h3>", unsafe_allow_html=True)
    col_in1, col_in2, col_in3, col_in4 = st.columns(4)

    with col_in1:
        choix_des = st.selectbox("Désignation (البيان المسبق) :", liste_designations_prefere)
        if choix_des == "Autre (كتابة مخصصة)":
            input_des = st.text_input("اكتب البيان الخاص بك باليد :", "Élément sur mesure")
        else:
            input_des = choix_des

    with col_in2:
        input_mat = st.selectbox("Matériau (نوع الرخام أو الجرانيت) :", liste_options_materiaux)
    with col_in3:
        input_long = st.number_input("الطول بالمتر (Longueur) :", min_value=0.01, value=1.00, step=0.01)
    with col_in4:
        input_larg = st.number_input("العرض بالمتر (Largeur) :", min_value=0.01, value=0.30, step=0.01)

    input_qte = st.number_input("الكمية / عدد القطع (Quantité) :", min_value=1, value=1, step=1)

    if st.button("➕ إضافة هذه القطعة إلى جدول الحسابات"):
        p_m2 = prix_materiaux.get(input_mat, 600)
        surf = input_long * input_larg * input_qte
        tot_ligne = surf * p_m2

        st.session_state["panier_actuel"].append({
            "Désignation": input_des,
            "Matériau": input_mat.upper(),
            "Dimensions": f"{input_long}x{input_larg}",
            "Quantité": input_qte,
            "Surface (m2)": round(surf, 2),
            "Total HT (DH)": round(tot_ligne, 2)
        })
        st.toast("تمت إضافة القطعة للجدول بنجاح! 🎉")

    # عرض جدول السلع الحالية بتصميم منسق
    if st.session_state["panier_actuel"]:
        st.markdown("<h3 style='color: #2e75b6;'>📊 قائمة المواد المدرجة بالملف الحالي</h3>", unsafe_allow_html=True)
        df_panier = pd.DataFrame(st.session_state["panier_actuel"])
        st.dataframe(df_panier, use_container_width=True)

        total_ht = df_panier["Total HT (DH)"].sum()
        total_ttc = total_ht * 1.2

        st.markdown("<h3 style='color: #2e75b6;'>🧮 التلخيص المالي المباشر للملف</h3>", unsafe_allow_html=True)

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            remise = st.number_input("نسبة التخفيض الإجمالية (%) Remise :", min_value=0.0, max_value=100.0, value=0.0)
        with col_f2:
            avance = st.number_input("مبلغ التسبيق المدفوع مسبقاً (DH) Avance :", min_value=0.0, value=0.0)

        montant_remise = total_ttc * (remise / 100)
        total_net = total_ttc - montant_remise
        reste_a_payer = total_net - avance

        # ديزاين بطاقات العرض المالي الجذابة
        c_m1, c_m2, c_m3 = st.columns(3)
        c_m1.metric(label="إجمالي المبلغ قبل التخفيض (TTC)", value=f"{total_ttc:.2f} DH")
        c_m2.metric(label="الصافي المطلوب دفعه بعد التخفيض", value=f"{total_net:.2f} DH")
        c_m3.metric(label="المبلغ المتبقي بذمة الزبون", value=f"{reste_a_payer:.2f} DH")

        if reste_a_payer > 0:
            st.warning(f"⚠️ متبقي بذمة الزبون مبلغ وقدره : {reste_a_payer:.2f} درهم مغربي.")
        else:
            st.success("✅ هذه الفاتورة مدفوعة بالكامل بالكامل ولا يوجد أي متبقي.")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("💾 حفظ الفاتورة وتثبيتها نهائياً في الأرشيف الأمني"):
                date_actuelle = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                id_commande = f"CMD-{random.randint(10000, 99999)}"

                historique_total = charger_depot(DB_FILE)

                for item in st.session_state["panier_actuel"]:
                    historique_total.append({
                        "ID unique": id_commande,
                        "Date Commande": date_actuelle,
                        "N° Dossier": label_fichier,
                        "Client": nom_client,
                        "Responsable": responsable_commande,
                        "Désignation": item["Désignation"],
                        "Matériau": item["Matériau"],
                        "Dimensions": item["Dimensions"],
                        "Quantité": item["Quantité"],
                        "Surface (m2)": item["Surface (m2)"],
                        "Total Ligne HT (DH)": item["Total HT (DH)"],
                        "Total HT Commande (DH)": round(total_ht, 2),
                        "Total TTC (DH)": round(total_net, 2),
                        "Avance (DH)": round(avance, 2),
                        "Reste (DH)": round(reste_a_payer, 2)
                    })

                sauvegarder_depot(historique_total, DB_FILE)
                st.session_state["historique_commandes"] = historique_total
                st.session_state["panier_actuel"] = []
                st.success("✅ تم حفظ الملف بنجاح وتثبيته في الأرشيف الموحد للورشة!")
                st.rerun()

# ================= القسم 2 : الأرشيف والبحث الذكي الموحد =================
elif page == "🗂️ الأرشيف والبحث الذكي":
    st.markdown("<h1 style='color: #1f4e78;'>🗂️ أرشيف المبيعات والبحث المتقدم عن الملفات</h1>", unsafe_allow_html=True)

    st.session_state["historique_commandes"] = charger_depot(DB_FILE)

    if not st.session_state["historique_commandes"]:
        st.info("الأرشيف فارغ حالياً، لا توجد طلبيات مسجلة بملف الورشة.")
    else:
        df_hist = pd.DataFrame(st.session_state["historique_commandes"])

        # ديزاين لوحة الإحصائيات الشاملة للأرباح والمداخيل في أعلى الأرشيف
        st.markdown("<h3 style='color: #2e75b6;'>📈 ملخص أداء ومبيعات ورشة دكالة</h3>", unsafe_allow_html=True)
        total_ventes_ttc = df_hist["Total TTC (DH)"].unique().sum()
        total_avances = df_hist["Avance (DH)"].unique().sum()
        total_restes = df_hist["Reste (DH)"].unique().sum()

        card1, card2, c_card3 = st.columns(3)
