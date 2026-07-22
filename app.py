import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# 1. Configuration de la page et sécurité d'accès de base
st.set_page_config(page_title="Marbrerie - Commandes Privées", page_icon="Ⓜ️", layout="wide")

# Injection de code CSS pour optimiser l'impression directe depuis le navigateur
st.markdown("""
    <style>
    @media print {
        /* Masquer la barre latérale, les boutons et les formulaires de saisie */
        [data-testid="stSidebar"],
        .stButton,
        div.row-widget.stRadio,
        data-testid="stHeader",
        iframe,
        header,
        .block-container div:has(> .stNumberInput),
        .block-container div:has(> .stTextInput),
        div[data-testid="stForm"] {
            display: none !important;
        }
        /* Ajuster le tableau pour qu'il prenne toute la largeur à l'impression */
        .main .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            max-width: 100% !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

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

# 2. Base de données des prix
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

# Initialisation de l'historique et des compteurs
if "historique_commandes" not in st.session_state:
    st.session_state["historique_commandes"] = []

if "compteur_dossier" not in st.session_state:
    st.session_state["compteur_dossier"] = 1

def reinitialiser_nouvelle_commande():
    st.session_state["compteur_dossier"] += 1
    st.session_state["lignes_commande"] = [
        {"designation": "Escalier", "materiau": "marmer", "longueur": 1.00, "largeur": 0.30, "quantite": 1}
    ]
    st.session_state["client_nom_input"] = "Client_Anonyme"

def sauvegarder_dans_application(panier_items, total_net, avance, reste, client_nom, nom_fichier, responsable):
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
            "Total Ligne (DH)": item["total"],
            "Total Net Commande (DH)": total_net,
            "Avance (DH)": avance,
            "Reste à Payer (DH)": reste
        }
        st.session_state["historique_commandes"].append(nouvelle_ligne)

st.title("Ⓜ️ Système de Gestion des Commandes - Marbre & Granit")

if st.sidebar.button("🔒 Se déconnecter"):
    st.session_state["authentifie"] = False
    st.rerun()

if st.sidebar.button("✨ Créer Nouveau Dossier (Vider Table)", type="primary"):
    reinitialiser_nouvelle_commande()
    st.rerun()

if "lignes_commande" not in st.session_state:
    st.session_state["lignes_commande"] = [
        {"designation": "Escalier", "materiau": "marmer", "longueur": 1.00, "largeur": 0.30, "quantite": 1}
    ]

st.header("📂 Informations et Classification du Dossier")
col_info1, col_info2, col_info3 = st.columns(3)

annee_actuelle = datetime.now().year
num_dossier_auto = f"DOS-{annee_actuelle}-{st.session_state['compteur_dossier']:03d}"

with col_info1:
    label_fichier = st.text_input("N° Dossier / Référence (Auto) :", num_dossier_auto)
with col_info2:
    if "client_nom_input" not in st.session_state:
        st.session_state["client_nom_input"] = "Client_Anonyme"
    nom_client = st.text_input("Nom du client :", key="client_nom_input")
with col_info3:
    responsable_commande = st.text_input("Responsable du suivi (Vendeur) :", "Nadim Jadoui")

st.header("📊 Tableau des Articles de la Commande (Saisie)")

panier_final = []
total_brut = 0.0
indices_a_supprimer = []

for i, ligne in enumerate(st.session_state["lignes_commande"]):
    c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 1, 1, 1, 0.5])

    with c1:
        designation = st.text_input("Désignation / Usage", value=ligne["designation"], key=f"des_{i}")
    with c2:
        materiau = st.selectbox("Matériau", list(prix_materiaux.keys()), index=list(prix_materiaux.keys()).index(ligne["materiau"]) if ligne["materiau"] in prix_materiaux else 0, key=f"mat_{i}")
    with c3:
        longueur = st.number_input("Longueur (m)", min_value=0.01, value=float(ligne["longueur"]), step=0.01, key=f"long_{i}")
    with c4:
        largeur = st.number_input("Largeur (m)", min_value=0.01, value=float(ligne["largeur"]), step=0.01, key=f"larg_{i}")
    with c5:
        quantite = st.number_input("Qté", min_value=1, value=int(ligne["quantite"]), step=1, key=f"qte_{i}")
    with c6:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️", key=f"suppr_{i}", help="Supprimer cette ligne"):
            indices_a_supprimer.append(i)

    st.session_state["lignes_commande"][i] = {
        "designation": designation, "materiau": materiau, "longueur": longueur, "largeur": largeur, "quantite": quantite
    }

    prix_m2 = prix_materiaux[materiau]
    surface_totale = longueur * largeur * quantite
    total_ligne = surface_totale * prix_m2
    total_brut += total_ligne

    panier_final.append({
        "designation": designation, "materiau": materiau.upper(), "dimensions": f"{longueur}x{largeur}", "quantite": quantite, "surface": surface_totale, "total": total_ligne
    })

    st.caption(f"📐 Ligne {i+1} : Surface = {surface_totale:.2f} m² | Prix Unit. = {prix_m2} DH | Total Ligne = {total_ligne:.2f} DH")
    st.markdown("---")

if indices_a_supprimer:
    for index in sorted(indices_a_supprimer, reverse=True):
        st.session_state["lignes_commande"].pop(index)
    st.rerun()

if st.button("➕ Ajouter une nouvelle ligne (Style Excel)"):
    st.session_state["lignes_commande"].append(
        {"designation": "Nouvel article", "materiau": "marmer", "longueur": 1.00, "largeur": 0.30, "quantite": 1}
    )
    st.rerun()

if panier_final:
    st.subheader(f"TOTAL BRUT : {total_brut:.2f} DH")

    col_finance1, col_finance2 = st.columns(2)
    with col_finance1:
        remise = st.number_input("Remise globale (%)", min_value=0.0, max_value=100.0, value=0.0)
    with col_finance2:
        avance = st.number_input("Somme d'avance versée (DH)", min_value=0.0, value=0.0)

    montant_remise = total_brut * (remise / 100)
    total_net = total_brut - montant_remise
    reste_a_payer = total_net - avance

    st.markdown(f"**Montant Remise :** {montant_remise:.2f} DH")
    st.subheader(f"TOTAL NET À PAYER : {total_net:.2f} DH")

    if reste_a_payer > 0:
        st.warning(f"Reste à payer : {reste_a_payer:.2f} DH (Facture semi-payée)")
    else:
        st.success("Facture Entièrement Payée")

    if st.button("💾 Enregistrer la commande dans le tableau de l'application", type="primary"):
        sauvegarder_dans_application(panier_final, total_net, avance, reste_a_payer, nom_client, label_fichier, responsable_commande)
        st.success(f"Le dossier {label_fichier} a été enregistré avec succès !")

# --- Affichage et Gestion du tableau historique interne ---
st.header("🗂️ Tableau Historique des Commandes Enregistrées")

if st.session_state["historique_commandes"]:
    df_historique = pd.DataFrame(st.session_state["historique_commandes"])

    col_rech1, col_rech2, col_rech3 = st.columns(3)

    with col_rech1:
        recherche = st.text_input("🔍 Rechercher un dossier ou un client pour impression / suppression :", "")

    if recherche:
        df_historique = df_historique[
            df_historique["N° Dossier"].str.contains(recherche, case=False, na=False) |
            df_historique["Client"].str.contains(recherche, case=False, na=False)
        ]

    with col_rech2:
        dossier_a_supprimer = st.selectbox("🗑️ Sélectionner un dossier à supprimer", ["Aucun"] + list(df_historique["N° Dossier"].unique()))
        if dossier_a_supprimer != "Aucun":
            if st.button("Confirmer la suppression du dossier"):
                st.session_state["historique_commandes"] = [ligne for ligne in st.session_state["historique_commandes"] if ligne["N° Dossier"] != dossier_a_supprimer]
                st.success(f"Dossier {dossier_a_supprimer} supprimé avec succès.")
                st.rerun()

    with col_rech3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🖨️ Imprimer la facture filtrée"):
            components.html("<script>window.print();</script>", height=0)

    st.dataframe(df_historique, use_container_width=True)
else:
    st.write("Aucune commande enregistrée pour le moment dans cette session.")
