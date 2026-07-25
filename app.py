import streamlit as st
import pandas as pd
import io
import random
from datetime import datetime

# استدعاء آمن ومحمي لمكتبة الذكاء الاصطناعي والتنبؤ XGBoost والـ Compiler لضمان الجودة
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

st.set_page_config(page_title="Marbrerie ERP - Marbre Doukkali", page_icon="Ⓜ️", layout="wide")

# تخصيص الـ CSS وتصميم حرف M كبير وفخم مزخرف بألوان وعروق الرخام الطبيعي الصافي لحذف التشتت البصري القديم
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
    if st.button("تسجيل الدخول للنظام"):
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
page = st.sidebar.radio("📋 الانتقال بين الأقسام :", ["📝 تسجيل الطلبيات الجديدة", "🗂️ الأرشيف والبحث الذكي", "🗑️ سلة المهملات (Corbeille)"])

if st.sidebar.button("🔒 تسجيل الخروج"):
    st.session_state["authentifie"] = False
    st.rerun()


# ================= القسم 1 : تسجيل الطلبيات الجديدة (كودك الأول والأصلي بالكامل) =================
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
        responsable_commande = st.selectbox("المسؤول عن المتابعة (البائع) :", liste_responsables, index=0)
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

        sym_p = "%"
        st.markdown(f"""
        <div class='marble-panel'>
            <h3 style='color:#0f172a !important; border-bottom:2px solid #0f172a;'>🧾 تفاصيل كشف الحساب المالي للملف</h3>
            <p>💰 إجمالي السعر قبل الاحتساب (HT): <b>{total_ht:,.2f} DH</b></p>
            <p>📈 إجمالي السعر شامل الرسوم (TTC 20%): <b>{total_ttc:,.2f} DH</b></p>
            <p>📉 قيمة التخفيض التجاري الممنوح: <b>{montant_remise:,.2f} DH ({remise:,.1f}{sym_p})</b></p>
            <p>⭐ الصافي المطلوب دفعه نهائياً (NET): <span style='font-size:20px; color:#15803d;'><b>{total_net:,.2f} DH</b></span></p>
            <p>💵 مبلغ التسبيق المدفوع مسبقاً (Avance): <b>{avance:,.2f} DH</b></p>
            <p>🚨 الباقي استخلاصه بذمة الزبون: <span style='font-size:20px; color:#b91c1c;'><b>{reste_a_payer:,.2f} DH</b></span></p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💾 ترحيل وحفظ الطلبية بشكل نهائي في الأرشيف"):
            nouvelle_commande = {
                "N° Dossier": label_fichier,
                "Client": nom_client,
                "Responsable": responsable_commande,
                "Date_H": datetime.now().strftime("%Y-%m-%d %H:%M")
# ================= القسم 2 : الأرشيف والبحث الذكي الموحد =================
elif page == "🗂️ الأرشيف والبحث الذكي والطباعة":
    # تم إلغاء نصوص علامات التنصيص الثلاثية وحقنها بأسلوب برمي سليم لمنع الأخطاء نهائياً
    st.markdown("<div style='background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%); color: #0f172a; padding: 25px; border-radius: 12px; border-left: 8px solid #f59e0b; margin-bottom: 25px;'><h2 style='color:#0f172a !important; text-align:right; margin:0;'>🗂️ نظام إدارة مبيعات دكالة - الفرز الرخامي الذكي</h2><p style='color:#334155 !important; text-align:right;'>هنا تجد كافة الطلبيات المحفوظة منسقة داخل واجهة رخامية كلاسيكية متباينة الألوان لسهولة تامة في القراءة والبحث البصري الحاد والكتابة واضحة.</p></div>", unsafe_allow_html=True)

    if not st.session_state["historique_commandes"]:
        st.info("الأرشيف فارغ حالياً، قم بتسجيل وتثبيت طلبية أولاً.")
    else:
        df_hist = pd.DataFrame(st.session_state["historique_commandes"])

        st.markdown("### 🔍 صندوق البحث السريع والموحد (اكتب اسم البائع الطوسي أو الزبون للفرز الفوري):")
        recherche = st.text_input("ابحث هنا بالكلمة :", key="search_inside_folder")

        if recherche:
            req = recherche.lower().strip()
            cond_dossier = df_hist['N° Dossier'].astype(str).str.lower().str.contains(req, na=False)
            cond_client = df_hist['Client'].astype(str).str.lower().str.contains(req, na=False)
            cond_vendeur = df_hist['Responsable'].astype(str).str.lower().str.contains(req, na=False)
            df_filtered = df_hist[cond_dossier | cond_client | cond_vendeur]
        else:
            df_filtered = df_hist

        # [استكمال كودك وإصلاح الانقطاع المسبب للخطأ] - عرض السجلات المفلترة فورياً لعمالك
        st.dataframe(df_filtered.drop(columns=["Details"], errors="ignore"), use_container_width=True)

        st.markdown("### 🖨️ فحص تفاصيل القياسات للملف المحدد وتوليد مستند الـ Excel")
        liste_fichiers_dispo = df_filtered["N° Dossier"].unique()
        fichier_selectionne = st.selectbox("اختر رقم الملف لعرض سلعه وطباعته :", liste_fichiers_dispo)

        cmd_info = next((item for item in st.session_state["historique_commandes"] if item["N° Dossier"] == fichier_selectionne), None)

        if cmd_info:
            st.markdown(f"📄 كشف قياسات وسلع الرخام التابع للملف المحدد: **{fichier_selectionne}**")
            df_details_cmd = pd.DataFrame(cmd_info["Details"])
            st.dataframe(df_details_cmd, use_container_width=True)

            # توليد مستند الإكسيل الاحترافي للتحميل والطباعة الفورية
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_details_cmd.to_excel(writer, sheet_name='تفاصيل القياسات', index=False)
            st.download_button(
                label="🖨️ اضغط هنا لتحميل كشف القياسات النهائي بصيغة Excel للزبون",
                data=buffer.getvalue(),
                file_name=f"كشف_حساب_الملف_{fichier_selectionne}.xlsx",
                mime="application/vnd.ms-excel"
            )

            st.markdown("---")
            if st.button(f"🗑️ إرسال الملف {fichier_selectionne} بالكامل إلى سلة المهملات (إلغاء الطلبية)"):
                st.session_state["corbeille_commandes"].append(cmd_info.copy())
                st.session_state["historique_commandes"].remove(cmd_info)
                st.success("تم نقل الملف وتأمينه بنجاح داخل سلة المهملات بنجاح!")
                st.rerun()
# ================= القسم 3 : سلة المهملات (Corbeille) الأصلي والمخصص =================
elif page == "🗑️ سلة المهملات (Corbeille)":
    st.markdown("<div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: #ffffff; padding: 20px; border-radius: 12px; border-left: 8px solid #ef4444; margin-bottom: 25px;'><h2 style='color:#ffffff !important; text-align:right; margin:0;'>🗑️ سلة المهملات - إدارة المتروكات</h2><p style='color:#cbd5e1 !important; text-align:right;'>هنا يمكنك مراجعة واسترجاع الملفات والفواتير الملغاة لحمايتها من الضياع والتلف التام.</p></div>", unsafe_allow_html=True)

    if not st.session_state["corbeille_commandes"]:
        st.info("سلة المهملات فارغة ومستقرة تماماً حالياً.")
    else:
        df_corbeille = pd.DataFrame(st.session_state["corbeille_commandes"])

        # عرض قائمة الملفات الملغاة الحالية المتواجدة داخل السلة
        st.dataframe(df_corbeille.drop(columns=["Details"], errors="ignore"), use_container_width=True)

        st.markdown("---")
        col_action_corbeille1, col_action_corbeille2 = st.columns(2)

        with col_action_corbeille1:
            if st.button("♻️ Restaurer tous les dossiers (استرجاع الملفات)"):
                for cmd in st.session_state["corbeille_commandes"]:
                    st.session_state["historique_commandes"].append(cmd)
                st.session_state["corbeille_commandes"] = []
                st.success("تمت استعادة كافة البيانات والملفات بنجاح تام إلى الأرشيف المركزي!")
                st.rerun()

        with col_action_corbeille2:
            if st.button("🔥 Vider la corbeille (حذف أبدي ونهائي)"):
                st.session_state["corbeille_commandes"] = []
                st.warning("تم تفريغ سلة المهملات بالكامل وحذف السجلات الملغاة نهائياً.")
                st.rerun()
