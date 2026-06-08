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

def normalize_region(x):
    if pd.isna(x):
        return x
    x = str(x).strip().lower()

    mapping = {
        "marrakech-safi": "Marrakech-Safi",
        "marrakech safi": "Marrakech-Safi",
        "marrakech - safi": "Marrakech-Safi",
        "marrakech_safi": "Marrakech-Safi",
    }

    return mapping.get(x, x.title())


coop["region"] = coop["region"].apply(normalize_region)

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

st.subheader("🏆 Ranking des provinces - Formation")

formation_rank = formation.copy()
formation_rank = formation_rank[formation_rank["id_coop"].isin(ids_filtre)]

formation_cols = [
    "Elaboration_strategies",
    "Montage_projet",
    "Communication",
    "Governanace"
]

formation_cols = [c for c in formation_cols if c in formation_rank.columns]

formation_rank["score_formation"] = (
    formation_rank[formation_cols]
    .apply(lambda c: c.astype(str).str.strip().str.lower())
    .eq("présent")
    .sum(axis=1)
    / len(formation_cols)
    * 100
)

province_formation = (
    formation_rank.merge(coop_filtre[["id_coop", "province"]], on="id_coop")
    .groupby("province")["score_formation"]
    .mean()
    .reset_index()
    .sort_values("score_formation", ascending=False)
)

fig = px.bar(
    province_formation,
    x="province",
    y="score_formation",
    title="Score moyen Formation par province"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("🏆 Ranking des provinces - Coaching")

coaching_rank = coaching.copy()
coaching_rank = coaching_rank[coaching_rank["id_coop"].isin(ids_filtre)]

coaching_cols = [
    "s1","s2","s3","s4",
    "s5","s6","s7","s8",
    "s9","s10","s11","s12"
]

coaching_rank["score_coaching"] = (
    coaching_rank[coaching_cols]
    .apply(lambda c: c.astype(str).str.strip().str.lower())
    .eq("oui")
    .sum(axis=1)
    / len(coaching_cols)
    * 100
)

province_coaching = (
    coaching_rank.merge(coop_filtre[["id_coop", "province"]], on="id_coop")
    .groupby("province")["score_coaching"]
    .mean()
    .reset_index()
    .sort_values("score_coaching", ascending=False)
)

fig = px.bar(
    province_coaching,
    x="province",
    y="score_coaching",
    title="Score moyen Coaching par province"
)

st.plotly_chart(fig, use_container_width=True)

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
    .apply(lambda c: c.astype(str).str.strip().str.lower())
    .eq("présent")
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
# ANALYSE PARTICIPATION
# =====================

st.subheader("📊 Analyse de la participation")

# ---------------------
# Ligne 1 : Sexe dirigeant / Adhérents
# ---------------------

col1, col2 = st.columns(2)

with col1:

    st.markdown("### 👩‍💼 Sexe du dirigeant")

    genre_df = (
        coop_filtre["feminine"]
        .fillna("Non renseigné")
        .astype(str)
        .str.lower()
        .replace({
            "oui": "Dirigée par une femme",
            "non": "Dirigée par un homme"
        })
        .value_counts()
        .reset_index()
    )

    genre_df.columns = ["Genre", "Nombre"]

    fig = px.pie(
        genre_df,
        names="Genre",
        values="Nombre",
        hole=0.3
    )

    fig.update_traces(
        textinfo="label+percent+value"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:

    st.markdown("### 👥 Adhérents par sexe")

    nb_femmes = (
        coop_filtre["femmes_actuelles"]
        .fillna(0)
        .sum()
    )

    nb_hommes = (
        coop_filtre["adherents_actuels"]
        .fillna(0)
        .sum()
        - nb_femmes
    )

    adherents_df = pd.DataFrame({
        "Sexe": ["Femmes", "Hommes"],
        "Nombre": [nb_femmes, nb_hommes]
    })

    fig = px.pie(
        adherents_df,
        names="Sexe",
        values="Nombre",
        hole=0.3
    )

    fig.update_traces(
        textinfo="label+percent+value"
    )

    st.plotly_chart(fig, use_container_width=True)


# ---------------------
# Ligne 2 : Formation
# ---------------------

st.markdown("### 🎓 Participation aux formations")

formation_analyse = formation[
    formation["id_coop"].isin(ids_filtre)
].copy()

formation_cols = [
    "Elaboration_strategies",
    "Montage_projet",
    "Communication",
    "Governanace"
]

formation_cols = [
    c for c in formation_cols
    if c in formation_analyse.columns
]

formation_analyse["nb_sessions"] = (
    formation_analyse[formation_cols]
    .apply(lambda c: c.astype(str).str.strip().str.lower())
    .eq("présent")
    .sum(axis=1)
)

formation_stats = pd.DataFrame({
    "Catégorie": [
        "4 sessions",
        "3 sessions",
        "2 sessions",
        "1 session",
        "0 session"
    ],
    "Nombre": [
        (formation_analyse["nb_sessions"] == 4).sum(),
        (formation_analyse["nb_sessions"] == 3).sum(),
        (formation_analyse["nb_sessions"] == 2).sum(),
        (formation_analyse["nb_sessions"] == 1).sum(),
        (formation_analyse["nb_sessions"] == 0).sum()
    ]
})

fig = px.pie(
    formation_stats,
    names="Catégorie",
    values="Nombre",
    hole=0.3
)

fig.update_traces(
    textinfo="label+percent+value"
)

st.plotly_chart(fig, use_container_width=True)


# ---------------------
# Ligne 3 : Coaching
# ---------------------

st.markdown("### 🧭 Participation au coaching")

coaching_analyse = coaching[
    coaching["id_coop"].isin(ids_filtre)
].copy()

coaching_cols = [
    "s1","s2","s3","s4",
    "s5","s6","s7","s8",
    "s9","s10","s11","s12"
]

coaching_analyse["nb_seances"] = (
    coaching_analyse[coaching_cols]
    .apply(lambda c: c.astype(str).str.strip().str.lower())
    .eq("oui")
    .sum(axis=1)
)

nb_total = (
    coaching_analyse["nb_seances"] == 12
).sum()

nb_aucune = (
    coaching_analyse["nb_seances"] == 0
).sum()

col1, col2 = st.columns(2)

col1.metric(
    "Coops ayant suivi les 12 séances",
    int(nb_total)
)

col2.metric(
    "Coops n'ayant suivi aucune séance",
    int(nb_aucune)
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
                "Governanace": "Gouvernance",
            }

            nb_present = 0

            for col, label in formation_labels.items():
                if col in formation_data.index:
                    valeur = str(formation_data[col]).strip().lower()

                    if valeur == "présent":
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