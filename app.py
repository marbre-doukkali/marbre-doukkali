import streamlit as st
import pandas as pd
import io
from datetime import datetime

# 1. Configuration de la page et sécurité d'accès de base
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

# Initialisation de la base de données interne en mémoire pour stocker l'historique
if "historique_commandes" not in st.session_state:
    st.session_state["historique_commandes"] = []

# Initialisation du tableau dynamique d'édition si vide
if "lignes_commande" not in st.session_state:
    st.session_state["lignes_commande"] = [
        {"designation": "Escalier", "materiau": "marmer", "longueur": 1.00, "largeur": 0.30, "quantite": 1}
    ]

# Fonction pour sauvegarder en interne dans l'application
def sauvegarder_dans_application(panier_items, total_ht, total_ttc, avance, reste, client_nom, nom_fichier, responsable):
    date_actuelle = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for item in panier_items:
        nouvelle_ligne = {
            "Date Commande": date_actuelle,
            "N° Dossier": nom_fichier,
            "Responsable": responsable,
            "Client": client_nom,
            "Désignation / Usage": item["designation"],
            "Matériau": item["materiau"],
            "Dimensions": item["dimensions"],
            "Quantité": item["quantite"],
            "Surface Totale (m2)": item["surface"],
            "Total Ligne HT (DH)": item["total"],
            "Total HT Commande (DH)": total_ht,
            "Total TTC (x1.2) (DH)": total_ttc,
            "Avance (DH)": avance,
            "Reste à Payer (DH)": reste
        }
        st.session_state["historique_commandes"].append(nouvelle_ligne)

# --- NAVIGATION SIDEBAR (Système Multi-pages) ---
st.sidebar.title("Ⓜ️ Menu Marbrerie")
page = st.sidebar.radio("Navigation", ["📝 Saisie des Commandes", "🗂️ Historique & Recherche"])

if st.sidebar.button("🔒 Se déconnecter"):
    st.session_state["authentifie"] = False
    st.rerun()

# ================= PAGE 1 : SAISIE DES COMMANDES =================
if page == "📝 Saisie des Commandes":
    st.title("📝 Gestion et Création des Commandes")

    if st.button("🆕 Nouveau Dossier (Vider le formulaire)"):
        st.session_state["lignes_commande"] = [
            {"designation": "Escalier", "materiau": "marmer", "longueur": 1.00, "largeur": 0.30, "quantite": 1}
        ]
        st.rerun()

    # --- Informations Dossier et Client ---
    st.header("📂 Informations du Dossier actuel")
    col_info1, col_info2, col_info3 = st.columns(3)

    with col_info1:
        label_fichier = st.text_input("N° Dossier / Référence :", "DOS-2026-001")
    with col_info2:
        nom_client = st.text_input("Nom du client :", "Client_Anonyme")
    with col_info3:
        responsable_commande = st.text_input("Responsable du suivi (Vendeur) :", "Nadim Jadoui")

    # --- Tableau des articles type Excel ---
    st.header("📊 Tableau des Articles")
    panier_final = []
    total_ht = 0.0

    for i, ligne in enumerate(st.session_state["lignes_commande"]):
        st.markdown(f"**Ligne N° {i+1} :**")
        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            designation = st.text_input("Désignation / Usage", value=ligne["designation"], key=f"des_{i}")
        with c2:
            materiau = st.selectbox("Matériau", list(prix_materiaux.keys()), index=list(prix_materiaux.keys()).index(ligne["materiau"]) if ligne["materiau"] in prix_materiaux else 0, key=f"mat_{i}")
        with c3:
            longueur = st.number_input("Longueur (m)", min_value=0.01, value=ligne["longueur"], step=0.01, key=f"long_{i}")
        with c4:
            largeur = st.number_input("Largeur (m)", min_value=0.01, value=ligne["largeur"], step=0.01, key=f"larg_{i}")
        with c5:
            quantite = st.number_input("Quantité", min_value=1, value=ligne["quantite"], step=1, key=f"qte_{i}")

        st.session_state["lignes_commande"][i] = {
            "designation": designation, "materiau": materiau,
            "longueur": longueur, "largeur": largeur, "quantite": quantite
        }

        prix_m2 = prix_materiaux[materiau]
        surface_totale = longueur * largeur * quantite
        total_ligne = surface_totale * prix_m2
        total_ht += total_ligne

        panier_final.append({
            "designation": designation,
            "materiau": materiau.upper(),
            "dimensions": f"{longueur}x{largeur}",
            "quantite": quantite,
            "surface": surface_totale,
            "total": total_ligne
        })

        st.caption(f"📐 Surface: {surface_totale:.2f} m² | 💰 Total Ligne HT: {total_ligne:.2f} DH")
        st.markdown("---")

    if st.button("➕ Ajouter une nouvelle ligne (Style Excel)"):
        st.session_state["lignes_commande"].append(
            {"designation": "Nouvel article", "materiau": "marmer", "longueur": 1.00, "largeur": 0.30, "quantite": 1}
        )
        st.rerun()

    # 4. Calculs financiers et validation
    if panier_final:
        st.header("🧮 Synthèse Financière")

        total_ttc = total_ht * 1.2

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.subheader(f"TOTAL HT : {total_ht:.2f} DH")
            st.subheader(f"TOTAL TTC (HT x 1.2) : {total_ttc:.2f} DH")

        col_finance1, col_finance2 = st.columns(2)
        with col_finance1:
            remise = st.number_input("Remise globale (%)", min_value=0.0, max_value=100.0, value=0.0)
        with col_finance2:
            avance = st.number_input("Somme d'avance versée (DH)", min_value=0.0, value=0.0)

        montant_remise = total_ttc * (remise / 100)
        total_net = total_ttc - montant_remise
        reste_a_payer = total_net - avance

        st.markdown(f"**Montant Remise :** {montant_remise:.2f} DH")
        st.subheader(f"TOTAL NET À PAYER : {total_net:.2f} DH")

        if reste_a_payer > 0:
            st.warning(f"Reste à payer : {reste_a_payer:.2f} DH (Facture semi-payée)")
        else:
            st.success("Facture Entièrement Payée")

        # --- أزرار الإجراءات وحفظ البيانات ---
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("💾 Enregistrer la commande dans le système"):
                # نستخدم البيانات الأصلية لحفظها في مصفوفة الجلسة لضمان بقائها وعرضها الفوري
                sauvegarder_dans_application(
                    panier_final, total_ht, total_net, avance, reste_a_payer,
                    nom_client, label_fichier, responsable_commande
                )
                st.success("Commande enregistrée avec succès dans le système !")

        with col_btn2:
            # 🛠️ الحل البرمجي الجذري: توليد ملف XML مندمج كلياً ومسطر بخطوط واضحة ومحاذاة لليسار
            xml_data = '<?xml version="1.0" encoding="utf-8"?><?mso-application progid="Excel.Sheet"?>'
            xml_data += '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">'

            # إعداد الأنماط والتسطير والتلوين داخل إكسيل
            xml_data += '<Styles>'
            xml_data += '<Style ss:ID="logo"><Font ss:FontName="Arial" ss:Size="14" ss:Bold="1" ss:Color="#1f4e78"/><Alignment ss:Horizontal="Left"/></Style>'
            xml_data += '<Style ss:ID="header"><Font ss:FontName="Arial" ss:Bold="1" ss:Color="#FFFFFF"/><Borders><Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1"/><Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1"/><Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1"/><Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1"/></Borders><Interior ss:Color="#1f4e78" ss:Pattern="Solid"/><Alignment ss:Horizontal="Left"/></Style>'
            xml_data += '<Style ss:ID="cell"><Font ss:FontName="Arial"/><Borders><Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1"/><Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1"/><Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1"/><Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1"/></Borders><Alignment ss:Horizontal="Left"/></Style>'
