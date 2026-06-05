import streamlit as st
import pandas as pd
import plotly.express as px
from database import load_data

st.set_page_config(
    page_title="Dashboard MOURAFAKA",
    layout="wide"
)

# =====================
# FONCTIONS
# =====================

def statut_formation(taux):
    if taux == 100:
        return "🟢 Terminée"
    elif taux >= 75:
        return "🟠 Moyenne"
    return "🔴 Faible"


def statut_coaching(taux):
    if taux == 100:
        return "🟢 Accompagnée"
    elif taux >= 70:
        return "🟠 Moyenne"
    return "🔴 Faible"


# =====================
# CHARGEMENT
# =====================

coop, formation, coaching = load_data()

coop.columns = coop.columns.str.strip()
formation.columns = formation.columns.str.strip()
coaching.columns = coaching.columns.str.strip()

st.title("📊 Dashboard MOURAFAKA")

# =====================
# FILTRES
# =====================

st.sidebar.header("Filtres")

regions = ["Toutes"] + sorted(coop["region"].dropna().unique().tolist())

region_selected = st.sidebar.selectbox("Région", regions)

if region_selected == "Toutes":
    coop_filtre = coop.copy()
else:
    coop_filtre = coop[coop["region"] == region_selected]

provinces = ["Toutes"] + sorted(coop_filtre["province"].dropna().unique().tolist())

province_selected = st.sidebar.selectbox("Province", provinces)

if province_selected != "Toutes":
    coop_filtre = coop_filtre[coop_filtre["province"] == province_selected]


# IDs filtrés
ids_filtre = coop_filtre["id_coop"].unique()


# =====================
# KPI
# =====================

st.subheader("📈 Indicateurs clés")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Coopératives", len(coop_filtre))

col2.metric(
    "Adhérents",
    int(coop_filtre["adherents_actuels"].fillna(0).sum())
)

col3.metric(
    "Femmes",
    int(coop_filtre["femmes_actuelles"].fillna(0).sum())
)

ca_total = coop_filtre["ca"].fillna(0).sum() if "ca" in coop_filtre.columns else 0

col4.metric("CA", f"{ca_total:,.0f} DH")


# =====================
# COOPERATIVES PAR REGION
# =====================

st.subheader("🗺️ Répartition des coopératives")

region_df = coop_filtre.groupby("region").size().reset_index(name="nb_coops")

fig = px.bar(region_df, x="region", y="nb_coops", title="Nombre de coopératives par région")

st.plotly_chart(fig, use_container_width=True)


# =====================
# FORMATION KPI (FILTRÉ)
# =====================

st.subheader("🎓 Formation")

formation_filtre = formation[formation["id_coop"].isin(ids_filtre)]

formation_cols = [
    "Elaboration_strategies",
    "Montage_projet",
    "Communication",
    "Governanace"
]

formation_cols = [c for c in formation_cols if c in formation_filtre.columns]

if len(formation_cols) > 0:

    formation_filtre["taux"] = (
        formation_filtre[formation_cols]
        .notna()
        .sum(axis=1)
        / len(formation_cols)
        * 100
    )

    st.metric(
        "Taux moyen de participation",
        f"{formation_filtre['taux'].mean():.1f}%"
    )


# =====================
# COACHING KPI (FILTRÉ)
# =====================

st.subheader("🧭 Coaching")

coaching_filtre = coaching[coaching["id_coop"].isin(ids_filtre)]

coaching_cols = [
    "s1","s2","s3","s4",
    "s5","s6","s7","s8",
    "s9","s10","s11","s12"
]

coaching_filtre["taux"] = (
    coaching_filtre[coaching_cols]
    .apply(lambda c: c.astype(str).str.strip().str.lower())
    .eq("oui")
    .sum(axis=1)
    / len(coaching_cols)
    * 100
)

st.metric(
    "Taux moyen de coaching",
    f"{coaching_filtre['taux'].mean():.1f}%"
)


# =====================
# FICHE COOPERATIVE
# =====================

st.subheader("🏢 Fiche détaillée")

liste_coops = sorted(coop_filtre["nom_cooperative"].dropna().unique())

if len(liste_coops) > 0:

    coop_selected = st.selectbox("Choisir une coopérative", liste_coops)

    fiche_df = coop_filtre[coop_filtre["nom_cooperative"] == coop_selected]

    if not fiche_df.empty:

        fiche = fiche_df.iloc[0]

        st.markdown("## Informations générales")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Nom :**", fiche["nom_cooperative"])
            st.write("**Région :**", fiche["region"])
            st.write("**Province :**", fiche["province"])
            st.write("**Secteur :**", fiche["secteur"])
            st.write("**Branche :**", fiche["branche"])

        with col2:
            st.write("**Adhérents :**", fiche["adherents_actuels"])
            st.write("**Femmes :**", fiche["femmes_actuelles"])
            st.write("**Jeunes diplômés :**", fiche["jeunes_diplomes_actuels"])
            st.write("**PSH :**", fiche["psh_actuels"])

        st.divider()

        # =====================
        # FORMATION COOP
        # =====================

        formation_coop = formation[formation["id_coop"] == fiche["id_coop"]]

        if not formation_coop.empty:

            st.subheader("🎓 Formation")

            formation_data = formation_coop.iloc[0]

            formation_labels = {
                "Elaboration_strategies": "Élaboration de stratégies",
                "Montage_projet": "Montage de projet",
                "Communication": "Communication",
                "Governanace": "Gouvernance"
            }

            nb_present = 0

            for col, label in formation_labels.items():

                if col in formation_data.index:

                    valeur = str(formation_data[col]).strip()

                    if valeur and valeur.lower() != "nan":
                        st.write(f"✅ {label}")
                        nb_present += 1
                    else:
                        st.write(f"❌ {label}")

            taux_formation_coop = (nb_present / len(formation_labels)) * 100

            st.progress(taux_formation_coop / 100)

            st.success(f"Taux Formation : {taux_formation_coop:.0f}%")

            st.info(statut_formation(taux_formation_coop))

        st.divider()

        # =====================
        # COACHING COOP
        # =====================

        coaching_coop = coaching[coaching["id_coop"] == fiche["id_coop"]]

        if not coaching_coop.empty:

            st.subheader("🧭 Coaching")

            coaching_data = coaching_coop.iloc[0]

            nb_present = 0

            cols = st.columns(4)

            for i, seance in enumerate(coaching_cols):

                valeur = str(coaching_data[seance]).strip().lower()

                if valeur == "oui":
                    cols[i % 4].success(seance.upper())
                    nb_present += 1
                else:
                    cols[i % 4].error(seance.upper())

            taux_coaching_coop = (nb_present / len(coaching_cols)) * 100

            st.progress(taux_coaching_coop / 100)

            st.success(f"Taux Coaching : {taux_coaching_coop:.0f}%")

            st.info(statut_coaching(taux_coaching_coop))