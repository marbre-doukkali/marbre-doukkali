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

liste_responsables = ["Anouar", "Mourade", "Abd allah", "Mohamed", "Autre (كتابة اسم آخر)"]

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

catalogueCalculPierre = [
    # ==========================================
    # 1. أنواع الغرانيت والكوارتز الشاملة (Tout Granette & Quartz)
    # ==========================================
    { "id": "noir_galaxy", "name": "Noir Galaxy", "type": "Granit", "origin": "Importé (Inde)", "price": 1450 },
    { "id": "noir_zimbabwe", "name": "Noir Zimbabwe", "type": "Granit", "origin": "Importé", "price": 1550 },
    { "id": "noir_absolu", "name": "Noir Absolu", "type": "Granit", "origin": "Importé", "price": 1600 },
    { "id": "blue_pearl", "name": "Blue Pearl", "type": "Granit", "origin": "Importé (Norvège)", "price": 1750 },
    { "id": "gris_espagnol", "name": "Gris Espagnol", "type": "Granit", "origin": "Importé (Espagne)", "price": 600 },
    { "id": "bianco_sardo", "name": "Bianco Sardo", "type": "Granit", "origin": "Importé (Italie)", "price": 650 },
    { "id": "tan_brown", "name": "Tan Brown", "type": "Granit", "origin": "Importé", "price": 750 },
    { "id": "kashmir_white", "name": "Kashmir White", "type": "Granit", "origin": "Importé", "price": 1200 },
    { "id": "titanium_gold", "name": "Titanium Gold", "type": "Granit", "origin": "Exotique", "price": 1900 },
    { "id": "steel_grey", "name": "Steel Grey", "type": "Granit", "origin": "Importé", "price": 800 },
    { "id": "black_pearl", "name": "Black Pearl", "type": "Granit", "origin": "Importé", "price": 850 },
    { "id": "verde_butterfly", "name": "Verde Butterfly", "type": "Granit", "origin": "Importé", "price": 900 },
    { "id": "rosa_porrino", "name": "Rosa Porrino", "type": "Granit", "origin": "Importé", "price": 580 },
    { "id": "quartz_blanc_pur", "name": "Quartz Blanc Pur", "type": "Quartz", "origin": "Importé", "price": 1300 },
    { "id": "quartz_calacatta", "name": "Quartz Calacatta", "type": "Quartz", "origin": "Importé", "price": 1850 },
    { "id": "gris_maroc", "name": "Gris Maroc", "type": "Granit", "origin": "Local (Maroc)", "price": 400 },

    # ==========================================
    # 2. أنواع الرخام الشاملة (Tout Marbre)
    # ==========================================
    # الرخام المستورد (Marbre Importé)
    { "id": "calacatta", "name": "Calacatta Blanc", "type": "Marbre", "origin": "Importé (Italie)", "price": 2150 },
    { "id": "statuaire", "name": "Statuario", "type": "Marbre", "origin": "Importé (Italie)", "price": 2300 },
    { "id": "carrara_blanc", "name": "Carrara Blanc", "type": "Marbre", "origin": "Importé (Italie)", "price": 1100 },
    { "id": "crema_marfil", "name": "Crema Marfil", "type": "Marbre", "origin": "Importé (Espagne)", "price": 550 },
    { "id": "marquina_noir", "name": "Marquina Noir", "type": "Marbre", "origin": "Importé (Espagne)", "price": 700 },
    { "id": "emparador_dark", "name": "Emperador Dark", "type": "Marbre", "origin": "Importé", "price": 850 },
    { "id": "emparador_light", "name": "Emperador Light", "type": "Marbre", "origin": "Importé", "price": 750 },
    { "id": "travertin_import", "name": "Travertin Romano", "type": "Marbre", "origin": "Importé (Turquie)", "price": 450 },
    { "id": "rosso_alicante", "name": "Rosso Alicante", "type": "Marbre", "origin": "Importé", "price": 650 },
    { "id": "onyx_marbre", "name": "Onyx Translucide", "type": "Marbre", "origin": "Exotique", "price": 3200 },

    # الرخام المحلي المغربي (Marbre Local Maroc)
    { "id": "tiflet_gris", "name": "Gris Tiflet", "type": "Marbre", "origin": "Local (Maroc)", "price": 420 },
    { "id": "noir_khenifra", "name": "Noir Khénifra", "type": "Marbre", "origin": "Local (Maroc)", "price": 850 },
    { "id": "volubilis", "name": "Volubilis", "type": "Marbre", "origin": "Local (Maroc)", "price": 380 },
    { "id": "beige_taza", "name": "Pierre de Taza", "type": "Marbre", "origin": "Local (Maroc)", "price": 350 },
    { "id": "rouge_agadir", "name": "Rouge Agadir", "type": "Marbre", "origin": "Local (Maroc)", "price": 300 },
    { "id": "jaune_marly", "name": "Jaune Marly", "type": "Marbre", "origin": "Local (Maroc)", "price": 320 },
    { "id": "sky_maroc", "name": "Sky Maroc (Gris)", "type": "Marbre", "origin": "Local (Maroc)", "price": 390 }
]

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
            .btn-imprimer {{
                display: block; width: 180px; margin: 15px auto; padding: 10px;
                background-color: #0f172a; color: white; text-align: center;
                font-weight: bold; border-radius: 6px; cursor: pointer; text-decoration: none;
            }}
            @media print {{
                .btn-imprimer {{ display: none; }}
            }}
        </style>
    </head>
    <body>
        <div class="btn-imprimer" onclick="window.print();">🖨️ طباعة الفاتورة</div>
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
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    color: #0f172a;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ============================= INITIALISATION DES DONNÉES =============================
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

if "df_dossiers" not in st.session_state:
    st.session_state.df_dossiers = pd.DataFrame(columns=[
        "N° Dossier", "Client", "Téléphone", "Responsable", "Statut",
        "Date_H", "Total HT (DH)", "Remise (%)", "Total TTC (DH)",
        "Total Net (DH)", "Avance (DH)", "Reste à payer (DH)"
    ])

if "df_details" not in st.session_state:
    st.session_state.df_details = pd.DataFrame(columns=[
        "N° Dossier", "Désignation", "Matériau", "Dimensions", "Quantité", "Surface (m2)", "Total HT (DH)"
    ])

if "articles_temporaires" not in st.session_state:
    st.session_state.articles_temporaires = []

# ============================= AUTHENTIFICATION =============================
if not st.session_state.authentifie:
    st.markdown('<div class="industrial-marble-m"><span class="luxury-marble-text">Ⓜ️</span></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align:center; color:white;">Marbrerie ERP - Marbre Doukkali</h2>', unsafe_allow_html=True)
