import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuration de la page
st.set_page_config(page_title="Marbrerie - Commandes Privées", page_icon="Ⓜ️", layout="wide")

# Injection CSS avancée : Force un style TABLEAU EXCEL à l'impression et masque les outils Streamlit
st.markdown("""
    <style>
    /* Style visuel à l'écran pour le tableau type Excel */
    .excel-table {
        width: 100%;
        border-collapse: collapse;
        font-family: Arial, sans-serif;
        font-size: 14px;
        margin-top: 15px;
    }
    .excel-table th {
        background-color: #F2F2F2 !important;
        color: #000000 !important;
        border: 1px solid #AAAAAA !important;
        padding: 8px;
        text-align: left;
        font-weight: bold;
    }
    .excel-table td {
        border: 1px solid #CCCCCC !important;
        padding: 8px;
        color: #333333;
    }
    .excel-table tr:nth-child(even) {
        background-color: #F9F9F9;
    }

    /* Bouton d'impression moderne style Excel */
    .btn-print {
        background-color: #107C41; /* Vert Excel */
        color: white;
        border: none;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: bold;
        border-radius: 4px;
        cursor: pointer;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    }
    .btn-print:hover {
        background-color: #0B5931;
    }

    /* REGLES STRICTES POUR L'IMPRESSION (Ctrl+P ou Bouton) */
    @media print {
        /* Cache absolument tout sauf la zone de facturation */
        [data-testid="stSidebar"],
        .stButton,
        div.row-widget.stRadio,
        [data-testid="stHeader"],
        iframe,
        header,
        footer,
        div[data-testid="stForm"],
        .btn-print,
        .no-print {
            display: none !important;
        }

        /* Supprime les espacements Streamlit pour l'impression */
        .main .block-container {
            padding: 0px !important;
            margin: 0px !important;
            max-width: 100% !important;
        }

        /* Force le quadrillage Excel noir et blanc sur papier */
        .excel-table th {
            background-color: #EFEFEF !important;
            color: #000 !important;
            border: 1px solid #000000 !important;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
        .excel-table td {
            border: 1px solid #000000 !important;
            color: #000 !important;
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
            "Date Commande": date_actuelle, "N° Dossier": nom_fichier, "Responsable": responsable, "Client": client_nom,
            "Désignation / Usage": item["designation"], "Matériau": item["materiau"], "Dimensions": item["dimensions"],
            "Quantité": item["quantite"], "Surface Totale (m2)": item["surface"], "Total Ligne (DH)": item["total"],
            "Total Net Commande (DH)": total_net, "Avance (DH)": avance, "Reste à Payer (DH)": reste
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

# Zone de Saisie Saisie (S'effacera à l'impression)
st.markdown('<div class="no-print">', unsafe_allow_html=True)
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
st.markdown('</div>', unsafe_allow_html=True)

panier_final = []
total_HT = 0.0
indices_a_supprimer = []

# Saisie des articles
for i, ligne in enumerate(st.session_state["lignes_commande"]):
    # On encapsule la saisie dans une div qui disparait à l'impression
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
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
        if st.button("🗑️", key=f"suppr_{i}"):
            indices_a_supprimer.append(i)

    st.session_state["lignes_commande"][i] = {
        "designation": designation, "materiau": materiau, "longueur": longueur, "largeur": largeur, "quantite": quantite
    }
    st.markdown('</div>', unsafe_allow_html=True)

    # Calculs hors interface graphique
    prix_m2 = prix_materiaux[materiau]
    surface_totale = longueur * largeur * quantite
    total_ligne = surface_totale * prix_m2
    total_HT += total_ligne * 1.2

    panier_final.append({
        "designation": designation, "materiau": materiau.upper(), "dimensions": f"{longueur:.2f} x {largeur:.2f}",
        "quantite": quantite, "surface": f"{surface_totale:.2f} m²", "prix_unit": f"{prix_m2} DH", "total": f"{total_ligne:.2f} DH"
    })

if indices_a_supprimer:
    for index in sorted(indices_a_supprimer, reverse=True):
        st.session_state["lignes_commande"].pop(index)
    st.rerun()

st.markdown('<div class="no-print">', unsafe_allow_html=True)
if st.button("➕ Ajouter une nouvelle ligne (Style Excel)"):
    st.session_state["lignes_commande"].append(
        {"designation": "Nouvel article", "materiau": "marmer", "longueur": 1.00, "largeur": 0.30, "quantite": 1}
    )
    st.rerun()

col_finance1, col_finance2 = st.columns(2)
with col_finance1:
    remise = st.number_input("Remise globale (%)", min_value=0.0, max_value=100.0, value=0.0)
with col_finance2:
    avance = st.number_input("Somme d'avance versée (DH)", min_value=0.0, value=0.0)

montant_remise = total_HT * (remise / 100)
total_TTC = total_HT - montant_remise
reste_a_payer = total_TTC - avance
st.markdown('</div>', unsafe_allow_html=True)


# ==================== ZONE DOCUMENT PROPRE (STYLE TABLEAU EXCEL) ====================
if panier_final:
    st.markdown("---")

    # BOUTON IMPRESSION EXCEL NATIF (Ne recharge JAMAIS la page Streamlit)
    import streamlit as st

st.markdown("""
<style>
.btn-print {
    background-color: #28a745;
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: 8px;
    font-size: 16px;
    cursor: pointer;
}
.btn-print:hover {
    background-color: #218838;
}
</style>

<button class="btn-print" onclick="window.print()">
    🖨️ Imprimer la Commande (Format Excel)
</button>
""", unsafe_allow_html=True)

    # Construction du tableau HTML pur style Excel pour l'impression brute
    lignes_tableau_html = ""
    for idx, item in enumerate(panier_final):
        lignes_tableau_html += f"""
        <tr>
            <td>{idx + 1}</td>
