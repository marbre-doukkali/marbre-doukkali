import io
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Appel sécurisé et protégé de la bibliothèque XGBoost (optionnelle, non bloquante)
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

# ============================= CONFIGURATION GÉNÉRALE =============================
st.set_page_config(page_title="Marbrerie ERP - Marbre Doukkali", page_icon="Ⓜ️", layout="wide")

# ⚠️ À remplacer par votre propre mot de passe sécurisé (idéalement via st.secrets)
PASSWORD_SECRET = "doukkali2026"

liste_responsables = ["Ahmed", "Youssef", "Sara", "Mohamed", "Autre (كتابة اسم آخر)"]

liste_designations_prefere = [
    "Plan de travail cuisine",
    "Escalier",
    "Marche d'escalier",
    "Contremarche",
    "Revêtement de sol",
    "Revêtement mural",
    "Seuil de porte",
    "Rebord de fenêtre (Appui de fenêtre)",
    "Plan de salle de bain (Vasque)",
    "Douche à l'italienne",
    "Tablette / Console",
    "Colonne décorative",
    "Plinthe",
    "Pierre tombale",
    "Fontaine décorative",
    "Autre (كتابة مخصصة)",
]

liste_options_materiaux = [
    # --- Marbres ---
    "Marbre Blanc Thassos",
    "Marbre Blanc Carrara",
    "Marbre Crema Marfil",
    "Marbre Beige Marfil",
    "Marbre Noir Marquina",
    "Marbre Botticino",
    "Marbre Rose",
    "Marbre Vert",
    "Marbre Doukkali",
    "Marbre d'Agadir",
    "Marbre de Marrakech",
    "Onyx Blanc",
    "Onyx Miel",
    "Travertin Beige",
    "Travertin Noce",
    # --- Granits ---
    "Granit Noir Zimbabwe",
    "Granit Noir Absolu",
    "Granit Gris Sardaigne",
    "Granit Gris Perle",
    "Granit Blanc Royal",
    "Granit Rose Porrino",
    "Granit Jaune Tropical",
    "Granit Bleu Pearl",
]

prix_materiaux = {
    # --- Marbres (DH / m2) ---
    "Marbre Blanc Thassos": 900,
    "Marbre Blanc Carrara": 850,
    "Marbre Crema Marfil": 700,
    "Marbre Beige Marfil": 650,
    "Marbre Noir Marquina": 950,
    "Marbre Botticino": 680,
    "Marbre Rose": 750,
    "Marbre Vert": 800,
    "Marbre Doukkali": 600,
    "Marbre d'Agadir": 620,
    "Marbre de Marrakech": 640,
    "Onyx Blanc": 1300,
    "Onyx Miel": 1400,
    "Travertin Beige": 500,
    "Travertin Noce": 520,
    # --- Granits (DH / m2) ---
    "Granit Noir Zimbabwe": 850,
    "Granit Noir Absolu": 900,
    "Granit Gris Sardaigne": 600,
    "Granit Gris Perle": 620,
    "Granit Blanc Royal": 700,
    "Granit Rose Porrino": 720,
    "Granit Jaune Tropical": 780,
    "Granit Bleu Pearl": 1100,
}

NOM_PAGE_ARCHIVE = "🗂️ الأرشيف والبحث الذكي"  # nom unique utilisé partout (radio + elif)


def construire_recu_html(cmd_info, df_details_cmd):
    """Construit un reçu HTML imprimable (RTL, arabe) pour un dossier donné."""
    lignes_html = "".join(
        f"<tr><td>{r['Désignation']}</td><td>{r['Matériau']}</td><td>{r['Dimensions']}</td>"
        f"<td>{r['Quantité']}</td><td>{r['Surface (m2)']}</td><td>{r['Total HT (DH)']}</td></tr>"
        for _, r in df_details_cmd.iterrows()
    )
    return f"""
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="utf-8">
        <title>فاتورة {cmd_info['N° Dossier']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 25px; color: #0f172a; }}
            h2, h3 {{ text-align: center; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ border: 1px solid #334155; padding: 8px; text-align: right; }}
            th {{ background-color: #0f172a; color: #ffffff; }}
            .totaux p {{ font-size: 16px; margin: 6px 0; }}
        </style>
    </head>
    <body>
        <h2>🧾 فاتورة رخام دكالة - رقم الملف {cmd_info['N° Dossier']}</h2>
        <p>الزبون: <b>{cmd_info['Client']}</b> &nbsp;|&nbsp; المسؤول: <b>{cmd_info['Responsable']}</b> &nbsp;|&nbsp; التاريخ: {cmd_info['Date_H']}</p>
        <table>
            <tr><th>البيان</th><th>المادة</th><th>المقاس</th><th>الكمية</th><th>المساحة (m2)</th><th>الثمن HT (DH)</th></tr>
            {lignes_html}
        </table>
        <div class="totaux">
            <p>💰 المجموع HT: <b>{cmd_info['Total HT (DH)']:,.2f} DH</b></p>
            <p>📈 المجموع TTC: <b>{cmd_info['Total TTC (DH)']:,.2f} DH</b></p>
            <p>📉 التخفيض: <b>{cmd_info['Remise (%)']:,.1f}%</b></p>
            <p>⭐ الصافي: <b>{cmd_info['Total Net (DH)']:,.2f} DH</b></p>
            <p>💵 التسبيق: <b>{cmd_info['Avance (DH)']:,.2f} DH</b></p>
            <p>🚨 الباقي: <b>{cmd_info['Reste à payer (DH)']:,.2f} DH</b></p>
        </div>
    </body>
    </html>
    """

# ============================= CSS PERSONNALISÉ =============================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}
.industrial-marble-m {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 10px;
}
.luxury-marble-text {
    font-size: 90px;
    font-weight: 900;
    background: linear-gradient(135deg, #f8fafc 0%, #cbd5e1 40%, #64748b 60%, #f1f5f9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 2px 10px rgba(0,0,0,0.4);
}
.luxury-marble-text-sidebar {
    font-size: 40px;
}
.industrial-title {
    text-align: center;
    color: #ffffff;
    font-size: 22px;
    margin-bottom: 20px;
}
.marble-panel {
    background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
    padding: 20px;
    border-radius: 12px;
    border-left: 8px solid #15803d;
    margin-top: 15px;
    text-align: right;
    direction: rtl;
}
</style>
""", unsafe_allow_html=True)

# ============================= INITIALISATION DE L'ÉTAT DE SESSION =============================
# (Corrigé : sans cette étape, le premier lancement provoquait une KeyError)
for cle, valeur_defaut in [
    ("authentifie", False),
    ("panier_actuel", []),
    ("historique_commandes", []),
    ("corbeille_commandes", []),
]:
    if cle not in st.session_state:
        st.session_state[cle] = valeur_defaut

# ============================= ÉCRAN DE CONNEXION =============================
if not st.session_state["authentifie"]:
    st.markdown("<div class='industrial-marble-m'><div class='luxury-marble-text'>M</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='industrial-title'>مرحباً بك في نظام إدارة ومبيعات رخام دكالة</div>", unsafe_allow_html=True)
    mot_de_passe = st.text_input("أدخل الرقم السري الخاص بالفريق :", type="password")
    if st.button("تسجيل الدخول للنظام"):
        if mot_de_passe == PASSWORD_SECRET:
            st.session_state["authentifie"] = True
            st.rerun()
        else:
            st.error("كلمة السر غير صحيحة، حاول مجدداً.")
    st.stop()  # Corrigé : empêche l'exécution du reste de l'application avant connexion

# ============================= BARRE LATÉRALE =============================
st.sidebar.markdown(
    "<div class='industrial-marble-m' style='padding:10px; margin-bottom:10px;'>"
    "<div class='luxury-marble-text luxury-marble-text-sidebar'>M</div></div>",
    unsafe_allow_html=True
)
st.sidebar.markdown("<h3 style='text-align: center; color: #ffffff; margin-top:0;'>نظام مبيعات دكالة</h3>", unsafe_allow_html=True)

page = st.sidebar.radio(
    "📋 الانتقال بين الأقسام :",
    ["📝 تسجيل الطلبيات الجديدة", NOM_PAGE_ARCHIVE, "🗑️ سلة المهملات (Corbeille)"]
)

if st.sidebar.button("🔒 تسجيل الخروج"):
    st.session_state["authentifie"] = False
    st.rerun()

# ================= SECTION 1 : ENREGISTREMENT DES NOUVELLES COMMANDES =================
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
        choix_responsable = st.selectbox("المسؤول عن المتابعة (البائع) :", liste_responsables, index=0)
        responsable_commande = (
            st.text_input("اكتب اسم المسؤول :", "")
            if choix_responsable == "Autre (كتابة اسم آخر)" else choix_responsable
        )

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
            "Désignation": input_des,
            "Matériau": input_mat.upper(),
            "Dimensions": f"{input_long}x{input_larg}",
            "Quantité": input_qte,
            "Surface (m2)": round(surf, 2),
            "Total HT (DH)": round(tot_ligne, 2),
        })
        st.toast("تمت الإضافة بنجاح! 💎")

    if st.session_state["panier_actuel"]:
        st.markdown("### 📊 القطع المدرجة بالملف الحالي")
        df_panier = pd.DataFrame(st.session_state["panier_actuel"])
        st.dataframe(df_panier, use_container_width=True)

        st.markdown("##### 🛠️ تعديل محتوى الاستمارة الحالية (حذف قطعة واحدة معينة):")
        index_a_supprimer = st.number_input(
            "أدخل رقم السطر المراد حذفه من الجدول أعلاه (يبدأ من 0) :",
            min_value=0, max_value=len(st.session_state["panier_actuel"]) - 1, step=1
        )
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

        # Le symbole % est isolé dans une variable pour éviter une f-string mal terminée
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
                "Date_H": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Total HT (DH)": round(total_ht, 2),
                "Total TTC (DH)": round(total_ttc, 2),
                "Remise (%)": remise,
                "Total Net (DH)": round(total_net, 2),
                "Avance (DH)": avance,
                "Reste à payer (DH)": round(reste_a_payer, 2),
                "Details": st.session_state["panier_actuel"].copy(),
            }
            st.session_state["historique_commandes"].append(nouvelle_commande)
            st.session_state["panier_actuel"] = []
            st.success(f"تم حفظ الملف {label_fichier} بنجاح في الأرشيف! ✅")
            st.rerun()

# ================= SECTION 2 : ARCHIVE ET RECHERCHE INTELLIGENTE =================
elif page == NOM_PAGE_ARCHIVE:
    st.markdown(
        "<div style='background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%); color: #0f172a; "
        "padding: 25px; border-radius: 12px; border-left: 8px solid #f59e0b; margin-bottom: 25px;'>"
        "<h2 style='color:#0f172a !important; text-align:right; margin:0;'>🗂️ نظام إدارة مبيعات دكالة - الفرز الرخامي الذكي</h2>"
        "<p style='color:#334155 !important; text-align:right;'>هنا تجد كافة الطلبيات المحفوظة منسقة داخل واجهة رخامية "
        "كلاسيكية متباينة الألوان لسهولة تامة في القراءة والبحث البصري والكتابة الواضحة.</p></div>",
        unsafe_allow_html=True
    )

    if not st.session_state["historique_commandes"]:
        st.info("الأرشيف فارغ حالياً، قم بتسجيل وتثبيت طلبية أولاً.")
    else:
        df_hist = pd.DataFrame(st.session_state["historique_commandes"])

        st.markdown("### 🔍 صندوق البحث السريع والموحد (اكتب اسم البائع أو الزبون للفرز الفوري):")
        recherche = st.text_input("ابحث هنا بالكلمة :", key="search_inside_folder")

        if recherche:
            req = recherche.lower().strip()
            cond_dossier = df_hist["N° Dossier"].astype(str).str.lower().str.contains(req, na=False)
            cond_client = df_hist["Client"].astype(str).str.lower().str.contains(req, na=False)
            cond_vendeur = df_hist["Responsable"].astype(str).str.lower().str.contains(req, na=False)
            df_filtered = df_hist[cond_dossier | cond_client | cond_vendeur]
        else:
            df_filtered = df_hist

        df_affichage = df_filtered[["N° Dossier"]].rename(columns={"N° Dossier": "رقم الملف"})
        st.dataframe(df_affichage, use_container_width=True, hide_index=True, height=220)
        st.caption(f"📁 عدد الملفات المطابقة : {len(df_affichage)}")

        # ---- Export Excel du tableau complet de tous les dossiers filtrés ----
        df_export_global = df_filtered.drop(columns=["Details"], errors="ignore")
        buffer_global = None
        erreur_excel_global = None
        for moteur_essai in ("xlsxwriter", "openpyxl"):
            try:
                buffer_essai = io.BytesIO()
                with pd.ExcelWriter(buffer_essai, engine=moteur_essai) as writer:
                    df_export_global.to_excel(writer, sheet_name="قائمة الملفات", index=False)
                buffer_global = buffer_essai
                break
            except Exception as e:
                erreur_excel_global = str(e)
                continue

        if buffer_global:
            st.download_button(
                label="📊 تصدير جدول جميع الملفات إلى Excel",
                data=buffer_global.getvalue(),
                file_name="جدول_جميع_الملفات.xlsx",
                mime="application/vnd.ms-excel",
                key="export_global_excel"
            )
        else:
            st.warning(f"⚠️ تصدير الجدول الكامل غير متوفر حالياً. التفاصيل: {erreur_excel_global}")

        st.markdown("##### 🗑️ حذف سريع (نقل مباشر إلى سلة المهملات) بدون فتح التفاصيل:")
        col_del1, col_del2 = st.columns([3, 1])
        with col_del1:
            dossiers_a_supprimer = st.multiselect(
                "اختر ملفاً أو عدة ملفات لحذفها :",
                df_affichage["رقم الملف"].tolist(),
                key="multiselect_suppression_rapide"
            )
        with col_del2:
            st.write("")
            if st.button("🗑️ حذف المحدد"):
                if dossiers_a_supprimer:
                    for num_dossier in dossiers_a_supprimer:
                        cmd_a_suppr = next(
                            (item for item in st.session_state["historique_commandes"] if item["N° Dossier"] == num_dossier),
                            None
                        )
                        if cmd_a_suppr:
                            st.session_state["corbeille_commandes"].append(cmd_a_suppr.copy())
                            st.session_state["historique_commandes"].remove(cmd_a_suppr)
                    st.success(f"تم نقل {len(dossiers_a_supprimer)} ملف(ات) إلى سلة المهملات! ✅")
                    st.rerun()
                else:
                    st.warning("الرجاء اختيار ملف واحد على الأقل قبل الحذف.")

        st.markdown("### 🖨️ فحص تفاصيل القياسات للملف المحدد وتوليد مستند الـ Excel")
        liste_fichiers_dispo = df_filtered["N° Dossier"].unique()

        if len(liste_fichiers_dispo) == 0:
            st.warning("لا توجد نتائج مطابقة للبحث الحالي.")
        else:
            fichier_selectionne = st.selectbox("اختر رقم الملف لعرض سلعه وطباعته :", liste_fichiers_dispo)

            cmd_info = next(
                (item for item in st.session_state["historique_commandes"] if item["N° Dossier"] == fichier_selectionne),
                None
            )

            if cmd_info:
                st.markdown(f"📄 كشف قياسات وسلع الرخام التابع للملف المحدد: **{fichier_selectionne}**")
                df_details_cmd = pd.DataFrame(cmd_info["Details"])
                st.dataframe(df_details_cmd, use_container_width=True, height=220)

                # Choix automatique du moteur Excel disponible + capture de toute erreur d'exécution
                buffer = None
                erreur_excel = None
                for moteur_essai in ("xlsxwriter", "openpyxl"):
                    try:
                        buffer_essai = io.BytesIO()
                        with pd.ExcelWriter(buffer_essai, engine=moteur_essai) as writer:
                            df_details_cmd.to_excel(writer, sheet_name="تفاصيل القياسات", index=False)
                        buffer = buffer_essai
                        break
                    except Exception as e:
                        erreur_excel = str(e)
                        continue
                col_dl, col_print = st.columns(2)
                with col_dl:
                    if buffer:
                        st.download_button(
                            label="📥 تحميل كشف القياسات بصيغة Excel",
                            data=buffer.getvalue(),
                            file_name=f"كشف_حساب_الملف_{fichier_selectionne}.xlsx",
                            mime="application/vnd.ms-excel"
                        )
                    else:
                        st.warning(f"⚠️ تصدير Excel غير متوفر حالياً (المكتبة معطوبة أو غير متوافقة مع Python الحالي). التفاصيل: {erreur_excel}")
                with col_print:
                    if st.button("🖨️ طباعة الفاتورة"):
                        html_recu = construire_recu_html(cmd_info, df_details_cmd)
                        components.html(
                            f"""
                            <script>
                            var w = window.open('', '_blank');
                            w.document.write(`{html_recu}`);
                            w.document.close();
                            w.focus();
                            setTimeout(function() {{ w.print(); }}, 300);
                            </script>
                            """,
                            height=0
                        )

                st.markdown("---")
                if st.button(f"🗑️ إرسال الملف {fichier_selectionne} بالكامل إلى سلة المهملات (إلغاء الطلبية)"):
                    st.session_state["corbeille_commandes"].append(cmd_info.copy())
                    st.session_state["historique_commandes"].remove(cmd_info)
                    st.success("تم نقل الملف وتأمينه بنجاح داخل سلة المهملات!")
                    st.rerun()

# ================= SECTION 3 : CORBEILLE =================
elif page == "🗑️ سلة المهملات (Corbeille)":
    st.markdown(
        "<div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: #ffffff; "
        "padding: 20px; border-radius: 12px; border-left: 8px solid #ef4444; margin-bottom: 25px;'>"
        "<h2 style='color:#ffffff !important; text-align:right; margin:0;'>🗑️ سلة المهملات - إدارة المتروكات</h2>"
        "<p style='color:#cbd5e1 !important; text-align:right;'>هنا يمكنك مراجعة واسترجاع الملفات والفواتير الملغاة "
        "لحمايتها من الضياع والتلف التام.</p></div>",
        unsafe_allow_html=True
    )

    if not st.session_state["corbeille_commandes"]:
        st.info("سلة المهملات فارغة ومستقرة تماماً حالياً.")
    else:
        df_corbeille = pd.DataFrame(st.session_state["corbeille_commandes"])
        st.dataframe(df_corbeille.drop(columns=["Details"], errors="ignore"), use_container_width=True, height=250)

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