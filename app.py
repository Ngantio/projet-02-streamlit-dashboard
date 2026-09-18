# ============================================================
# PROJET 2 — DASHBOARD INTERACTIF RETAIL
# Stack : Streamlit, Plotly, Pandas
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuration de la page ---
st.set_page_config(
    page_title="Dashboard Retail",
    page_icon="🛒",
    layout="wide"
)

# --- Chargement des données ---
@st.cache_data
def load_data():
    df = pd.read_excel('data/Online Retail.xlsx', engine='openpyxl')

    # Nettoyage
    df = df[df['Quantity'] > 0]
    df = df[df['UnitPrice'] > 0]
    df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
    df = df.dropna(subset=['Description'])

    # Features
    df['Revenue'] = df['Quantity'] * df['UnitPrice']
    df['Month'] = df['InvoiceDate'].dt.to_period('M').astype(str)
    df['Year'] = df['InvoiceDate'].dt.year

    return df

df = load_data()

# --- Titre principal ---
st.title("🛒 Dashboard Analyse des Ventes Retail")
st.markdown("**Dataset :** UCI Online Retail · 2010-2011 · E-commerce UK")
st.divider()

# --- Sidebar : Filtres ---
st.sidebar.header("🔧 Filtres")

# Filtre pays
pays_liste = ['Tous'] + sorted(df['Country'].unique().tolist())
pays_selectionne = st.sidebar.selectbox("🌍 Pays", pays_liste)

# Filtre période
mois_liste = sorted(df['Month'].unique().tolist())
mois_debut, mois_fin = st.sidebar.select_slider(
    "📅 Période",
    options=mois_liste,
    value=(mois_liste[0], mois_liste[-1])
)

# --- Application des filtres ---
df_filtre = df.copy()

if pays_selectionne != 'Tous':
    df_filtre = df_filtre[df_filtre['Country'] == pays_selectionne]

df_filtre = df_filtre[
    (df_filtre['Month'] >= mois_debut) &
    (df_filtre['Month'] <= mois_fin)
]

# --- KPIs ---
st.subheader("📊 Indicateurs clés")

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Revenu total",
            f"£{df_filtre['Revenue'].sum():,.0f}")

col2.metric("🧾 Commandes",
            f"{df_filtre['InvoiceNo'].nunique():,}")

col3.metric("👥 Clients",
            f"{df_filtre['CustomerID'].nunique():,}")

col4.metric("📦 Produits",
            f"{df_filtre['StockCode'].nunique():,}")

st.divider()

# --- Graphique 1 : Évolution CA mensuel ---
st.subheader("📈 Évolution du chiffre d'affaires mensuel")

ca_mensuel = (df_filtre.groupby('Month')['Revenue']
                       .sum()
                       .reset_index())

fig1 = px.line(
    ca_mensuel,
    x='Month',
    y='Revenue',
    markers=True,
    labels={'Month': 'Mois', 'Revenue': 'Revenu (£)'},
    color_discrete_sequence=['#E07B39']
)
fig1.update_layout(
    hovermode='x unified',
    yaxis_tickprefix='£',
    yaxis_tickformat=',.0f'
)
st.plotly_chart(fig1, use_container_width=True)

st.divider()

# --- Graphique 2 : Top 10 produits ---
st.subheader("📦 Top 10 produits par revenu")

mots_exclus = ['DOTCOM POSTAGE', 'POSTAGE', 'Manual',
               'AMAZONFEE', 'Bank Charges', 'CRUK']

top10 = (df_filtre[~df_filtre['Description'].isin(mots_exclus)]
                  .groupby('Description')['Revenue']
                  .sum()
                  .sort_values(ascending=False)
                  .head(10)
                  .reset_index())

fig2 = px.bar(
    top10,
    x='Revenue',
    y='Description',
    orientation='h',
    labels={'Revenue': 'Revenu (£)', 'Description': 'Produit'},
    color='Revenue',
    color_continuous_scale='Blues'
)
fig2.update_layout(
    yaxis={'categoryorder': 'total ascending'},
    xaxis_tickprefix='£',
    xaxis_tickformat=',.0f',
    coloraxis_showscale=False
)
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# --- Graphique 3 : Carte monde des ventes ---
st.subheader("🌍 Répartition géographique des ventes")

ca_pays = (df_filtre.groupby('Country')['Revenue']
                    .sum()
                    .reset_index())

fig3 = px.choropleth(
    ca_pays,
    locations='Country',
    locationmode='country names',
    color='Revenue',
    color_continuous_scale='Oranges',
    labels={'Revenue': 'Revenu (£)', 'Country': 'Pays'},
)
fig3.update_layout(
    geo=dict(showframe=False, showcoastlines=True),
    coloraxis_colorbar=dict(
        tickprefix='£',
        tickformat=',.0f'
    )
)
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# --- Graphique 4 : Patterns d'achat ---
st.subheader("⏰ Patterns d'achat")

col1, col2 = st.columns(2)

# Par jour de la semaine
jours_labels = {0: 'Lundi', 1: 'Mardi', 2: 'Mercredi',
                3: 'Jeudi', 4: 'Vendredi', 5: 'Samedi', 6: 'Dimanche'}

df_filtre['JourSemaine'] = df_filtre['InvoiceDate'].dt.dayofweek
ca_jour = (df_filtre.groupby('JourSemaine')['Revenue']
                    .sum()
                    .reset_index())
ca_jour['Jour'] = ca_jour['JourSemaine'].map(jours_labels)

fig4 = px.bar(
    ca_jour,
    x='Jour',
    y='Revenue',
    labels={'Revenue': 'Revenu (£)', 'Jour': 'Jour'},
    color='Revenue',
    color_continuous_scale='Purples'
)
fig4.update_layout(
    xaxis_tickangle=30,
    yaxis_tickprefix='£',
    yaxis_tickformat=',.0f',
    coloraxis_showscale=False
)
col1.plotly_chart(fig4, use_container_width=True)

# Par heure
df_filtre['Heure'] = df_filtre['InvoiceDate'].dt.hour
ca_heure = (df_filtre.groupby('Heure')['Revenue']
                     .sum()
                     .reset_index())

fig5 = px.line(
    ca_heure,
    x='Heure',
    y='Revenue',
    markers=True,
    labels={'Revenue': 'Revenu (£)', 'Heure': 'Heure'},
    color_discrete_sequence=['#8E44AD']
)
fig5.update_layout(
    yaxis_tickprefix='£',
    yaxis_tickformat=',.0f'
)
col2.plotly_chart(fig5, use_container_width=True)

st.divider()

# --- Footer ---
st.markdown("**Shanice Marvin Tiogang** · Data Science Portfolio · 2026")
