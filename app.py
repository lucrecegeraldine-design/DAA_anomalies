import streamlit as st
import pandas as pd
import numpy as np


# =====================================================
# CONFIGURATION PAGE
# =====================================================

st.set_page_config(
    page_title="DAA - Détection Automatique des Anomalies",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# STYLE APPLICATION
# =====================================================

st.markdown("""
<style>

/* Fond principal */
.stApp {
    background-color: white;
}

/* Titres */
h1, h2, h3, p, div {
    color: #111111 !important;
}

/* Boutons */
.stDownloadButton button {
    background-color: #00A651;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-size: 16px;
    font-weight: bold;
}

/* Upload */
[data-testid="stFileUploader"] {
    border: 2px dashed #00A651;
    padding: 20px;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.markdown("# 🟢 DAA")
st.markdown("### Détection Automatique des Anomalies de Trajets")

st.divider()

# =====================================================
# CHARGEMENT FICHIER
# =====================================================

uploaded_file = st.file_uploader(
    "📂 Charger le fichier CSV des trajets",
    type=["csv"]
)

# =====================================================
# SI FICHIER CHARGE
# =====================================================

if uploaded_file is not None:

    # =====================================================
    # LECTURE CSV
    # =====================================================

    df = pd.read_csv(uploaded_file, low_memory=False)

    st.success("✅ Fichier chargé avec succès")

    # =====================================================
    # APERCU DONNEES
    # =====================================================

    st.subheader("📄 Aperçu des données")

    st.dataframe(df.head())

    # =====================================================
    # NETTOYAGE
    # =====================================================

    df = df.replace(['None', 'nan', 'NaN', '', ' '], np.nan)

    colonnes_textes = [
        'vehicle_no',
        'conducteur',
        'rfid',
        'telephone'
    ]

    for col in colonnes_textes:

        if col in df.columns:

            df[col] = df[col].astype(str).str.strip()

            df[col] = df[col].replace('nan', np.nan)

            df[col] = df[col].fillna('NON IDENTIFIÉ')

    # =====================================================
    # CALCUL DUREE
    # =====================================================

    df['duree_secondes'] = pd.to_timedelta(
        df['duree_run'],
        errors='coerce'
    ).dt.total_seconds()

    # =====================================================
    # INITIALISATION ANOMALIES
    # =====================================================

    df['anomalies'] = ""

    # =====================================================
    # SEUILS
    # =====================================================

    seuil_vitesse = 200

    seuil_distance = df['dist_parcourue'].quantile(0.99)

    # =====================================================
    # DETECTION ANOMALIES
    # =====================================================

    # vitesse excessive
    df.loc[
        df['max_speed'] > seuil_vitesse,
        'anomalies'
    ] += "VITESSE_EXCESSIVE | "

    # distance aberrante
    df.loc[
        df['dist_parcourue'] > seuil_distance,
        'anomalies'
    ] += "DISTANCE_ABERRANTE | "

    # durée négative
    df.loc[
        df['duree_secondes'] < 0,
        'anomalies'
    ] += "DUREE_NEGATIVE | "

    # trajet trop long
    df.loc[
        df['duree_secondes'] > 86400,
        'anomalies'
    ] += "TRAJET_TROP_LONG | "

    # véhicule absent
    df.loc[
        df['vehicle_no'] == 'NON IDENTIFIÉ',
        'anomalies'
    ] += "VEHICULE_MANQUANT | "

    # conducteur absent
    df.loc[
        df['conducteur'] == 'NON IDENTIFIÉ',
        'anomalies'
    ] += "CONDUCTEUR_MANQUANT | "

    # RFID absent
    df.loc[
        df['rfid'] == 'NON IDENTIFIÉ',
        'anomalies'
    ] += "RFID_MANQUANT | "

    # téléphone absent
    df.loc[
        df['telephone'] == 'NON IDENTIFIÉ',
        'anomalies'
    ] += "TELEPHONE_MANQUANT | "

    # =====================================================
    # NOMBRE D'ANOMALIES
    # =====================================================

    df['nb_anomalies'] = df['anomalies'].apply(
        lambda x: len(
            [i for i in str(x).split('|')
             if i.strip() != ""]
        )
    )

    # =====================================================
    # DATASET ANOMALIES
    # =====================================================

    df_anomalies = df[
        df['anomalies'] != ""
    ].copy()

    # =====================================================
    # INDICATEURS
    # =====================================================

    st.subheader("📊 Résumé des anomalies")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Trajets analysés",
            len(df)
        )

    with col2:
        st.metric(
            "Trajets anormaux",
            len(df_anomalies)
        )

    with col3:

        taux = round(
            len(df_anomalies) / len(df) * 100,
            2
        )

        st.metric(
            "Taux anomalie",
            f"{taux}%"
        )

    # =====================================================
    # REPARTITION
    # =====================================================

    st.subheader("📈 Répartition des anomalies")

    repartition = (
        df_anomalies['anomalies']
        .str.split('|')
        .explode()
        .str.strip()
        .value_counts()
    )

    st.dataframe(repartition)

    # =====================================================
    # APERCU FINAL
    # =====================================================

    st.subheader("🚨 Aperçu du rapport final")

    st.dataframe(df_anomalies.head(20))

    # =====================================================
    # EXPORT FINAL CSV
    # =====================================================

    st.subheader("📥 Télécharger le rapport")

    csv = df_anomalies.to_csv(
        index=False,
        encoding='utf-8-sig'
    ).encode('utf-8-sig')

    st.download_button(
        label="⬇ Télécharger rapport DAA",
        data=csv,
        file_name="DAA_rapport_complet.csv",
        mime="text/csv"
    )

    st.success("✅ Rapport généré avec succès")