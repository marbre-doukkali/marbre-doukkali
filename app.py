import streamlit as st
import pandas as pd
import io
import random
from datetime import datetime

# 1. Configuration et Sécurité de l'application
st.set_page_config(page_title="Marbrerie ERP - Commandes", page_icon="Ⓜ️", layout="wide")

PASSWORD_SECRET = "2017@2026"

if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False

if not st.session_state["authentifie"]:
    st.title("🔒 Accès Sécurisé - Connexion")
    mot_de_passe = st.text_input("Entrez le mot de passe de l'équipe :", type="password")
    if st.button("Se connecter"):
        if mot_de_passe == PASSWORD_SECRET:
            st.session_state["authentifie"] = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect.")
    st.stop()

# 2. Base de données des prix au m² (DH)
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

# قنوات الذاكرة الدائمة المحمية
if "historique_commandes" not in st.session_state:
    st.session_state["historique_commandes"] = []

if "corbeille_commandes" not in st.session_state:
    st.session_state["corbeille_commandes"] = []

if "panier_actuel" not in st.session_state:
    st.session_state["panier_actuel"] = []

# Navigation de l'ERP
st.sidebar.title("Ⓜ️ Menu Marbrerie")
page = st.sidebar.radio("Navigation", ["📝 Saisie des Commandes", "🗂️ Historique & Recherche", "🗑️ Corbeille (سلة المهملات)"])

if st.sidebar.button("🔒 Se déconnecter"):
    st.session_state["authentifie"] = False
    st.rerun()

# ================= PAGE 1 : SAISIE DES COMMANDES (نظام الإدخال المضمون الجديد) =================
if page == "📝 Saisie des Commandes":
    st.title("📝 Gestion et Création des Commandes")

    if st.button("🆕 Nouveau Dossier (Vider tout)"):
        st.session_state["panier_actuel"] = []
        st.rerun()

    st.header("📂 1. Informations du Dossier")
    col_info1, col_info2, col_info3 = st.columns(3)

    with col_info1:
        label_fichier = st.text_input("N° Dossier / Référence :", "DOS-2026-001")
    with col_info2:
        nom_client = st.text_input("Nom du client :", "Client_Anonyme")
    with col_info3:
        responsable_commande = st.selectbox("Responsable du suivi (Vendeur) :", liste_responsables, index=0)

    # حلاً للمشكلة: استمارة إدخال صلبة ومستقلة لإضافة الرخام قطعة قطعة بدون مسح
    st.header("🧱 2. Ajouter un Article (إضافة قطعة رخام أو جرانيت)")
    col_in1, col_in2, col_in3, col_in4 = st.columns(4)

    with col_in1:
        input_des = st.text_input("Désignation (مثال: Escalier, Plan de cuisine) :", "Escalier")
    with col_in2:
        input_mat = st.selectbox("Matériau (إختر نوع الرخام) :", liste_options_materiaux)
    with col_in3:
        input_long = st.number_input("Longueur (m) :", min_value=0.01, value=1.00, step=0.01)
    with col_in4:
        input_larg = st.number_input("Largeur (m) :", min_value=0.01, value=0.30, step=0.01)

    input_qte = st.number_input("Quantité :", min_value=1, value=1, step=1)

    if st.button("➕ Ajouter cet article au dossier (إضافة للجدول)"):
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
        st.success("Article ajouté au tableau !")

    # عرض السلع المضافة حالياً إن وجدت
    if st.session_state["panier_actuel"]:
        st.header("📊 Articles dans ce dossier")
        df_panier = pd.DataFrame(st.session_state["panier_actuel"])
        st.dataframe(df_panier, use_container_width=True)

        total_ht = df_panier["Total HT (DH)"].sum()
        total_ttc = total_ht * 1.2

        st.header("🧮 Synthèse Financière")
        st.subheader(f"TOTAL HT : {total_ht:.2f} DH | TOTAL TTC : {total_ttc:.2f} DH")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            remise = st.number_input("Remise globale (%)", min_value=0.0, max_value=100.0, value=0.0)
        with col_f2:
            avance = st.number_input("Somme d'avance versée (DH)", min_value=0.0, value=0.0)

        montant_remise = total_ttc * (remise / 100)
        total_net = total_ttc - montant_remise
        reste_a_payer = total_net - avance

        st.markdown(f"**Montant Remise :** {montant_remise:.2f} DH")
        st.subheader(f"TOTAL NET À PAYER : {total_net:.2f} DH")

        if reste_a_payer > 0:
            st.warning(f"Reste à payer : {reste_a_payer:.2f} DH")
        else:
            st.success("Facture Entièrement Payée")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("💾 Enregistrer DEFINITIVEMENT dans l'historique"):
                date_actuelle = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                id_commande = f"CMD-{random.randint(10000, 99999)}"

                for item in st.session_state["panier_actuel"]:
                    st.session_state["historique_commandes"].append({
                        "ID unique": id_commande, "Date Commande": date_actuelle, "N° Dossier": label_fichier,
                        "Client": nom_client, "Responsable": responsable_commande, "Désignation": item["Désignation"],
                        "Matériau": item["Matériau"], "Dimensions": item["Dimensions"], "Quantité": item["Quantité"],
                        "Surface (m2)": item["Surface (m2)"], "Total Ligne HT (DH)": item["Total HT (DH)"],
                        "Total HT Commande (DH)": round(total_ht, 2), "Total TTC (DH)": round(total_net, 2),
                        "Avance (DH)": round(avance, 2), "Reste (DH)": round(reste_a_payer, 2)
                    })
                st.success(f"✅ تم تسجيل ملف {nom_client} بنجاح في مجلد {responsable_commande}!")
                st.session_state["panier_actuel"] = [] # تفريغ بعد الحفظ الناجح

        with col_btn2:
            html_invoice = f'<html><body><h2>BON DE COMMANDE - {nom_client}</h2></body></html>'
            buffer = io.BytesIO()
            buffer.write(html_invoice.encode('utf-8'))
            buffer.seek(0)
            st.download_button(
                label="🖨️ Télécharger le Bon (HTML)",
                data=buffer, file_name=f"Bon_{label_fichier}.html",
                mime="text/html", use_container_width=True
            )

# ================= PAGE 2 : HISTORIQUE & RECHERCHE (نظام المجلدات الثابت) =================
elif page == "🗂️ Historique & Recherche":
    st.title("🗂️ Historique & Recherche (Système de Dossiers)")

    st.markdown("### 📂 Choisissez un dossier (إختر مجلد المسؤول):")
    dossier_selectionne = st.radio("مجلدات المسؤولين المتوفرة :", liste_responsables, key="folder_selection_radio", horizontal=True)

    st.markdown(f"#### 📁 Dossier actuel : **{dossier_selectionne}**")

    if not st.session_state["historique_commandes"]:
        st.info("Aucune commande enregistrée dans le système.")
    else:
        df_hist = pd.DataFrame(st.session_state["historique_commandes"])
        df_folder = df_hist[df_hist['Responsable'] == dossier_selectionne]

        if df_folder.empty:
            st.info(f"Le dossier de '{dossier_selectionne}' est vide pour le moment.")
        else:
            st.dataframe(df_folder, use_container_width=True)

            st.subheader("🗑️ Actions / Supprimer")
            list_docs = sorted(list(df_folder['N° Dossier'].unique()))
            dossier_a_supprimer = st.selectbox("Sélectionnez le dossier à supprimer :", list_docs)

            if st.button("❌ Envoyer à la corbeille"):
                lignes_a_conserver = [c for c in st.session_state["historique_commandes"] if c["N° Dossier"] != dossier_a_supprimer]
                lignes_a_supprimer = [c for c in st.session_state["historique_commandes"] if c["N° Dossier"] == dossier_a_supprimer]

                st.session_state["historique_commandes"] = lignes_a_conserver
                st.session_state["corbeille_commandes"].extend(lignes_a_supprimer)
                st.success("Dossier envoyé à la corbeille !")
                st.rerun()

# ================= PAGE 3 : CORBEILLE (سلة المهملات المضمونة) =================
else:
    st.title("🗑️ Corbeille des dossiers supprimés")

    if not st.session_state["corbeille_commandes"]:
        st.info("La corbeille est vide.")
    else:
        df_corb = pd.DataFrame(st.session_state["corbeille_commandes"])
        st.dataframe(df_corb, use_container_width=True)

        list_corb = sorted(list(df_corb['N° Dossier'].unique()))
        dossier_action = st.selectbox("Choisir un dossier :", list_corb)

        if st.button("🔄 Restaurer le dossier"):
            lignes_a_garder = [c for c in st.session_state["corbeille_commandes"] if c["N° Dossier"] != dossier_action]
            lignes_a_restaurer = [c for c in st.session_state["corbeille_commandes"] if c["N° Dossier"] == dossier_action]

