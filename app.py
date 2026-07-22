import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. Configuration de la page et sécurité d'accès de base
st.set_page_config(page_title="Marbrerie - Commandes Privées", page_icon="Ⓜ️", layout="wide")

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

# Fonction pour sauvegarder la commande finale dans un fichier Excel historique
def sauvegarder_dans_excel(panier_items, total_net, avance, reste, client_nom, nom_fichier, responsable):
    fichier_excel = "commandes_marbrerie.xlsx"
    date_actuelle = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    nouvelles_lignes = []
    for item in panier_items:
        nouvelles_lignes.append({
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
        })

    df_nouveau = pd.DataFrame(nouvelles_lignes)

    if os.path.exists(fichier_excel):
        df_existant = pd.read_excel(fichier_excel)
        df_final = pd.concat([df_existant, df_nouveau], ignore_index=True)
    else:
        df_final = df_nouveau

    df_final.to_excel(fichier_excel, index=False)

st.title("Ⓜ️ Système de Gestion des Commandes - Marbre & Granit")

if st.sidebar.button("🔒 Se déconnecter"):
    st.session_state["authentifie"] = False
    st.rerun()

# 3. Initialisation du tableau dynamique (Structure Excel)
if "lignes_commande" not in st.session_state:
    st.session_state["lignes_commande"] = [
        {"designation": "Escalier", "materiau": "marmer", "longueur": 1.00, "largeur": 0.30, "quantite": 1}
    ]

# --- Informations Dossier et Client ---
st.header("📂 Informations et Classification du Dossier")
col_info1, col_info2, col_info3 = st.columns(3)

with col_info1:
    label_fichier = st.text_input("N° Dossier / Référence :", "DOS-2026-001")
with col_info2:
    nom_client = st.text_input("Nom du client :", "Client_Anonyme")
with col_info3:
    responsable_commande = st.text_input("Responsable du suivi (Vendeur) :", "Nadim Jadoui")

# --- Tableau des articles type Excel ---
st.header("📊 Tableau des Articles de la Commande")

panier_final = []
total_brut = 0.0

# Affichage dynamique des lignes
for i, ligne in enumerate(st.session_state["lignes_commande"]):
    st.markdown(f"**Ligne N° {i+1} :**")
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        designation = st.text_input("Désignation / Usage", value=ligne["designation"], key=f"des_{i}")
    with c2:
        materiau = st.selectbox("Matériau", list(prix_materiaux.keys()), index=list(prix_materiaux.keys()).index(ligne["materiau"]), key=f"mat_{i}")
    with c3:
        longueur = st.number_input("Longueur (m)", min_value=0.01, value=ligne["longueur"], step=0.01, key=f"long_{i}")
    with c4:
        largeur = st.number_input("Largeur (m)", min_value=0.01, value=ligne["largeur"], step=0.01, key=f"larg_{i}")
    with c5:
        quantite = st.number_input("Quantité", min_value=1, value=ligne["quantite"], step=1, key=f"qte_{i}")

    # Mise à jour immédiate dans la session
    st.session_state["lignes_commande"][i] = {
        "designation": designation,
        "materiau": materiau,
        "longueur": longueur,
        "largeur": largeur,
        "quantite": quantite
    }

    # Calculs de la ligne
    prix_m2 = prix_materiaux[materiau]
    surface_totale = longueur * largeur * quantite
    total_ligne = surface_totale * prix_m2
    total_brut += total_ligne

    panier_final.append({
        "designation": designation,
        "materiau": materiau.upper(),
        "dimensions": f"{longueur}x{largeur}",
        "quantite": quantite,
        "surface": surface_totale,
        "total": total_ligne
    })

    st.caption(f"📐 Surface: {surface_totale:.2f} m² | 💰 Total Ligne: {total_ligne:.2f} DH")
    st.markdown("---")

# --- Bouton Plus (+) pour insérer une nouvelle ligne ---
if st.button("➕ Ajouter une nouvelle ligne (Style Excel)"):
    st.session_state["lignes_commande"].append(
        {"designation": "Nouvel article", "materiau": "marmer", "longueur": 1.00, "largeur": 0.30, "quantite": 1}
    )
    st.rerun()

# 4. Calculs financiers et validation
if panier_final:
    st.subheader(f"TOTAL BRUT : {total_brut:.2f} DH")

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

    # --- Actions de validation ---
    col_actions1, col_actions2 = st.columns(2)

    with col_actions1:
        if st.button("💾 Enregistrer tout le dossier dans Excel"):
            sauvegarder_dans_excel(
                panier_final,
                total_net,
                avance,
                reste_a_payer,
                nom_client,
                label_fichier,
                responsable_commande
            )
            st.success(f"✅ Le dossier ({label_fichier}) a été enregistré avec succès dans 'commandes_marbrerie.xlsx' !")
            # Réinitialisation à une seule ligne vide après l'enregistrement
            st.session_state["lignes_commande"] = [
                {"designation": "Escalier", "materiau": "marmer", "longueur": 1.00, "largeur": 0.30, "quantite": 1}
            ]
            st.rerun()

    with col_actions2:
        if st.button("🗑️ Vider le tableau actuel"):
            st.session_state["lignes_commande"] = [
                {"designation": "Escalier", "materiau": "marmer", "longueur": 1.00, "largeur": 0.30, "quantite": 1}
            ]
            st.rerun()

