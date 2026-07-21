import streamlit as st

# 1. Configuration de la page et sécurité d'accès de base
st.set_page_config(page_title="Marbrerie - Commandes Privées", page_icon="🏗️", layout="wide")

# Système de mot de passe simple pour votre équipe
PASSWORD_SECRET = "2017@2026" # <--- Changez ce mot de passe secret ici

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

st.title("🏗️ Système de Gestion des Commandes - Marbrerie")

# Déconnexion
if st.sidebar.button("🔒 Se déconnecter"):
    st.session_state["authentifie"] = False
    st.rerun()

# 3. Gestion du panier en mémoire web
if "panier" not in st.session_state:
    st.session_state["panier"] = []

# Formulaire d'ajout d'article
st.header("🛒 Ajouter un article")
col1, col2, col3 = st.columns(3)

with col1:
    designation = st.text_input("Désignation / Usage (ex: escalier, plan de travail)", "Escalier")
    materiau = st.selectbox("Nom du marbre ou granit", list(prix_materiaux.keys()))

with col2:
    longueur = st.number_input("Longueur (m)", min_value=0.01, value=1.00, step=0.01)
    largeur = st.number_input("Largeur (m)", min_value=0.01, value=0.30, step=0.01)

with col3:
    quantite = st.number_input("Nombre (Quantité)", min_value=1, value=1, step=1)

if st.button("➕ Ajouter à la commande"):
    prix_m2 = prix_materiaux[materiau]
    surface_totale = longueur * largeur * quantite
    total_ligne = surface_totale * prix_m2

    st.session_state["panier"].append({
        "designation": designation,
        "materiau": materiau.upper(),
        "dimensions": f"{longueur}x{largeur}",
        "quantite": quantite,
        "surface": surface_totale,
        "total": total_ligne
    })
    st.success(f"Ajouté : {designation} en {materiau.upper()} ({total_ligne:.2f} DH)")

# 4. Affichage du bon de commande final
if st.session_state["panier"]:
    st.header("📄 Bon de Commande Actuel")

    total_brut = 0.0
    for idx, item in enumerate(st.session_state["panier"]):
        st.write(f"**{idx+1}. {item['designation']}** [{item['materiau']}] ({item['dimensions']}) x{item['quantite']} | Surface: {item['surface']:.2f} m² = **{item['total']:.2f} DH**")
        total_brut += item['total']

    st.markdown("---")
    st.subheader(f"TOTAL BRUT : {total_brut:.2f} DH")

    # Remise et Avance
    col_finance1, col_finance2 = st.columns(2)
    with col_finance1:
        remise = st.number_input("Remise globale (%)", min_value=0.0, max_value=100.0, value=0.0)
    with col_finance2:
        avance = st.number_input("Somme d'avance versée (DH)", min_value=0.0, value=0.0)

    montant_remise = (total_brut * remise) / 100
    total_net = total_brut - montant_remise
    reste_a_payer = total_net - avance

    st.write(f"Montant Remise : {montant_remise:.2f} DH")
    st.markdown(f"### **TOTAL NET À PAYER : {total_net:.2f} DH**")

    st.subheader("📊 Statut du Paiement")
    if reste_a_payer > 0:
        st.warning(f"Reste à payer : {reste_a_payer:.2f} DH (Facture semi-payée)")
    elif reste_a_payer == 0:
        st.success("Facture entièrement payée.")
    else:
        st.info(f"Montant à rendre au client : {-reste_a_payer:.2f} DH")

    if st.button("🗑️ Vider la commande"):
        st.session_state["panier"] = []
        st.rerun()
