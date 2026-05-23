from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

DATA_DIR = Path(__file__).resolve().parent / "Data"

st.set_page_config(page_title="Ba7ath Dashboard", layout="wide")
st.title("🌾 Tableau de bord : Enquête sur le Cheptel Ovin")

@st.cache_data
def load_data():
    # Chargement du nouveau fichier propre
    return pd.read_csv(DATA_DIR / "Clean_Master_Ovin.csv")

df = load_data()

# --- FILTRES ---
st.sidebar.header("🔍 Filtres")

# Curseur des années (Entiers uniquement)
annee_vals = df["Annee"].dropna().to_numpy()
min_year, max_year = int(annee_vals.min()), int(annee_vals.max())
selected_years = st.sidebar.slider("Période", min_year, max_year, (min_year, max_year))

# Liste des gouvernorats
govs = sorted(df['Governorate'].unique().tolist())
default_govs = [g for g in ["Kairouan", "La Manouba", "Zaghouan", "Sfax"] if g in govs]
selected_govs = st.sidebar.multiselect("Gouvernorats", govs, default=default_govs)

# Application des filtres
mask = (df['Annee'] >= selected_years[0]) & (df['Annee'] <= selected_years[1]) & (df['Governorate'].isin(selected_govs))
df_filtered = df.loc[mask]

# Agrégations
df_nat = df_filtered.groupby('Annee')['Effectif_Ovin'].sum().reset_index()
df_reg = df_filtered.groupby(['Annee', 'Governorate'])['Effectif_Ovin'].sum().reset_index()

# --- KPI ---
c1, c2, c3 = st.columns(3)
if not df_nat.empty:
    c1.metric("Volume total sur la période", f"{int(df_nat['Effectif_Ovin'].sum()):,} têtes".replace(',', ' '))
    c2.metric("Moyenne annuelle globale", f"{int(df_nat['Effectif_Ovin'].mean()):,} têtes".replace(',', ' '))
c3.metric("Régions analysées", len(selected_govs))

st.markdown("---")

# --- GRAPHIQUES ---
tab1, tab2, tab3, tab4 = st.tabs(["🇹🇳 1. National", "📈 2. Régional", "🥧 3. Parts", "🐑 4. Femelles"])

with tab1:
    if not df_nat.empty:
        fig1 = px.line(df_nat, x="Annee", y="Effectif_Ovin", markers=True, title="Évolution Globale (Cumul)")
        fig1.update_layout(xaxis=dict(tickformat="d")) # Force l'affichage "2024" (pas 2024.0)
        st.plotly_chart(fig1, width='stretch')

with tab2:
    if not df_reg.empty:
        fig2 = px.line(df_reg, x="Annee", y="Effectif_Ovin", color="Governorate", markers=True, title="Comparatif par Gouvernorat")
        fig2.update_layout(xaxis=dict(tickformat="d"))
        st.plotly_chart(fig2, width='stretch')

with tab3:
    if not df_reg.empty:
        y_pie = st.selectbox("Année pour le camembert:", sorted(df_reg['Annee'].unique(), reverse=True))
        fig3 = px.pie(df_reg[df_reg['Annee'] == y_pie], values="Effectif_Ovin", names="Governorate", hole=0.4)
        st.plotly_chart(fig3, width='stretch')

with tab4:
    # Le nouveau CSV possède une colonne 'Est_Femelle' (True/False)
    df_femelles = df_filtered.loc[df_filtered["Est_Femelle"].fillna(False)]
    if len(df_femelles) > 0:
        df_fem_agg = df_femelles.groupby(['Annee', 'Governorate'])['Effectif_Ovin'].sum().reset_index()
        fig4 = px.bar(df_fem_agg, x="Annee", y="Effectif_Ovin", color="Governorate", barmode="group", title="Femelles Productives")
        fig4.update_layout(xaxis=dict(tickformat="d"))
        st.plotly_chart(fig4, width='stretch')
    else:
        st.warning("Aucune donnée 'Femelle Productive' disponible pour cette sélection.")