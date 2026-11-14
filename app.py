
import streamlit as st
import duckdb
import pandas as pd
import numpy as np
import plotly.express as px
import joblib

from pathlib import Path
from datetime import date

# =====================================================
# 1. CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="IMDb Analytics | BI Cinéma",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = (
    BASE_DIR / "warehouse"
    / "imdb_analytics" / "dev.duckdb"
)

MODEL_PATH = BASE_DIR / "models_ml" / "modele_imdb.pkl"

# =====================================================
# 2. DESIGN
# =====================================================

st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: #f1f5f9;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    color: #f8fafc;
}

div[data-testid="stMetric"] {
    background: #171e2b;
    border: 1px solid #293548;
    border-radius: 14px;
    padding: 18px;
}

div[data-testid="stMetricLabel"] {
    color: #94a3b8;
}

div[data-testid="stMetricValue"] {
    color: #f8fafc;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}

.stButton > button[kind="primary"] {
    border-radius: 10px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. CONNEXION DUCKDB
# =====================================================

if not DB_PATH.exists():
    st.error(f"Base DuckDB introuvable : {DB_PATH}")
    st.stop()


@st.cache_data(ttl=600, show_spinner=False)
def executer_requete(sql, params=()):
    con = duckdb.connect(
        str(DB_PATH),
        read_only=True
    )

    try:
        return con.execute(
            sql,
            list(params)
        ).df()
    finally:
        con.close()


# =====================================================
# 4. FONCTIONS UTILITAIRES
# =====================================================

def format_nombre(valeur):
    if pd.isna(valeur):
        return "N/A"

    return f"{int(valeur):,}".replace(",", " ")


def afficher_graphique(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        margin=dict(l=20, r=20, t=55, b=30),
        hovermode="closest"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


def telecharger_csv(df, nom):
    st.download_button(
        "Télécharger les résultats CSV",
        data=df.to_csv(
            index=False
        ).encode("utf-8-sig"),
        file_name=nom,
        mime="text/csv"
    )


@st.cache_resource
def charger_modele(chemin, modification):
    # Charger uniquement un modèle créé localement
    # et provenant d'une source de confiance.
    return joblib.load(chemin)


# =====================================================
# 5. NAVIGATION
# =====================================================

st.sidebar.title("🎬 IMDb Analytics")
st.sidebar.caption("Business Intelligence Cinéma")

page = st.sidebar.radio(
    "Navigation",
    [
        "Vue globale",
        "Analyse des genres",
        "Analyse temporelle",
        "Classement des films",
        "Qualité des données",
        "Prédiction ML"
    ]
)

# =====================================================
# 6. FILTRES GLOBAUX
# =====================================================

st.sidebar.divider()

pages_analyse = [
    "Vue globale",
    "Analyse des genres",
    "Analyse temporelle",
    "Classement des films"
]

if page in pages_analyse:

    st.sidebar.subheader("Filtres d'analyse")

    annee_debut, annee_fin = st.sidebar.slider(
        "Période de sortie",
        min_value=1880,
        max_value=date.today().year,
        value=(1990, date.today().year)
    )

    df_genres = executer_requete("""
        SELECT nom_genre
        FROM main.dim_genre
        WHERE nom_genre IS NOT NULL
        ORDER BY nom_genre
    """)

    liste_genres = df_genres["nom_genre"].tolist()

    genres_selectionnes = st.sidebar.multiselect(
        "Genres cinématographiques",
        options=liste_genres,
        default=[]
    )

    votes_min = st.sidebar.selectbox(
        "Votes minimum pour le classement",
        [100, 1000, 5000, 10000, 50000, 100000],
        index=3
    )

    st.sidebar.caption(
        f"Période sélectionnée : "
        f"{annee_debut} - {annee_fin}"
    )

    # Conditions communes pour toutes les analyses
    condition = "F.annee BETWEEN ? AND ?"

    parametres = [annee_debut, annee_fin]

    if genres_selectionnes:

        placeholders = ",".join(
            ["?"] * len(genres_selectionnes)
        )

        condition += f"""
            AND EXISTS (
                SELECT 1
                FROM main.pont_film_genre P
                INNER JOIN main.dim_genre G
                    ON P.genre_key = G.genre_key
                WHERE P.tconst = F.tconst
                  AND G.nom_genre IN ({placeholders})
            )
        """

        parametres.extend(genres_selectionnes)

    def requete_filtree(sql, autres_params=()):
        return executer_requete(
            sql,
            tuple(parametres) + tuple(autres_params)
        )


# =====================================================
# 7. KPI
# =====================================================

def afficher_kpi():

    df = requete_filtree(f"""
        SELECT
            COUNT(*) AS total_films,
            COUNT(F.note_moyenne) AS films_notes,
            ROUND(AVG(F.note_moyenne), 2) AS note,
            COALESCE(SUM(F.nb_votes), 0) AS votes,
            ROUND(AVG(F.duree_minutes), 1) AS duree
        FROM main.fait_film F
        WHERE {condition}
    """)

    total = int(df["total_films"].iloc[0])
    notes = int(df["films_notes"].iloc[0])
    votes = int(df["votes"].iloc[0])

    note = df["note"].iloc[0]
    duree = df["duree"].iloc[0]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total films", format_nombre(total))
    c2.metric("Films notés", format_nombre(notes))

    c3.metric(
        "Note moyenne",
        f"{float(note):.2f}/10"
        if pd.notna(note) else "N/A"
    )

    c4.metric("Total votes", format_nombre(votes))

    st.caption(
        "Durée moyenne : "
        + (
            f"{float(duree):.1f} minutes"
            if pd.notna(duree)
            else "Non disponible"
        )
    )


# =====================================================
# PAGE 1 — VUE GLOBALE
# =====================================================

if page == "Vue globale":

    st.title("IMDb Analytics")
    st.subheader("Tableau de bord décisionnel du cinéma")

    afficher_kpi()

    st.divider()

    st.header("Évolution de la production")

    df_annee = requete_filtree(f"""
        SELECT
            F.annee,
            COUNT(*) AS nombre_films
        FROM main.fait_film F
        WHERE {condition}
        GROUP BY F.annee
        ORDER BY F.annee
    """)

    if not df_annee.empty:

        fig = px.line(
            df_annee,
            x="annee",
            y="nombre_films",
            markers=True,
            title="Nombre de films par année",
            labels={
                "annee": "Année",
                "nombre_films": "Nombre de films"
            }
        )

        fig.update_layout(height=440)

        afficher_graphique(fig)

    else:
        st.info("Aucune donnée disponible.")

    st.divider()

    st.header("Répartition par genre")

    genres = requete_filtree(f"""
        SELECT
            G.nom_genre,
            COUNT(*) AS nombre_films
        FROM main.fait_film F
        INNER JOIN main.pont_film_genre P
            ON F.tconst = P.tconst
        INNER JOIN main.dim_genre G
            ON P.genre_key = G.genre_key
        WHERE {condition}
        GROUP BY G.nom_genre
        ORDER BY nombre_films DESC
        LIMIT 10
    """)

    if not genres.empty:

        fig = px.bar(
            genres.sort_values("nombre_films"),
            x="nombre_films",
            y="nom_genre",
            orientation="h",
            title="Top 10 des genres"
        )

        fig.update_layout(height=480)

        afficher_graphique(fig)

    st.caption(
        "Un film peut appartenir à plusieurs genres."
    )


# =====================================================
# PAGE 2 — ANALYSE DES GENRES
# =====================================================

elif page == "Analyse des genres":

    st.title("Analyse des genres cinématographiques")

    afficher_kpi()

    st.divider()

    df = requete_filtree(f"""
        SELECT
            G.nom_genre,
            COUNT(*) AS nombre_films,
            COUNT(F.note_moyenne) AS films_notes,
            ROUND(AVG(F.note_moyenne), 2)
                AS note_moyenne,
            COALESCE(SUM(F.nb_votes), 0)
                AS total_votes
        FROM main.fait_film F
        INNER JOIN main.pont_film_genre P
            ON F.tconst = P.tconst
        INNER JOIN main.dim_genre G
            ON P.genre_key = G.genre_key
        WHERE {condition}
        GROUP BY G.nom_genre
        ORDER BY nombre_films DESC
    """)

    if df.empty:

        st.warning("Aucun résultat disponible.")

    else:

        col1, col2 = st.columns(2)

        with col1:

            fig = px.bar(
                df.head(12).sort_values(
                    "nombre_films"
                ),
                x="nombre_films",
                y="nom_genre",
                orientation="h",
                title="Films par genre"
            )

            afficher_graphique(fig)

        with col2:

            df_notes = df[
                df["films_notes"] >= 100
            ].nlargest(12, "note_moyenne")

            if not df_notes.empty:

                fig = px.bar(
                    df_notes.sort_values(
                        "note_moyenne"
                    ),
                    x="note_moyenne",
                    y="nom_genre",
                    orientation="h",
                    title="Genres les mieux notés"
                )

                fig.update_xaxes(range=[0, 10])

                afficher_graphique(fig)

            else:
                st.info(
                    "Pas assez de films notés."
                )

        st.subheader("Tableau comparatif")

        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )

        telecharger_csv(
            df,
            "analyse_genres_imdb.csv"
        )


# =====================================================
# PAGE 3 — ANALYSE TEMPORELLE
# =====================================================

elif page == "Analyse temporelle":

    st.title("Évolution temporelle du cinéma")

    afficher_kpi()

    st.divider()

    df = requete_filtree(f"""
        SELECT
            CAST(
                FLOOR(F.annee / 10.0) * 10
                AS INTEGER
            ) AS decennie,

            COUNT(*) AS nombre_films,

            ROUND(
                AVG(F.note_moyenne), 2
            ) AS note_moyenne

        FROM main.fait_film F
        WHERE {condition}
        GROUP BY decennie
        ORDER BY decennie
    """)

    if not df.empty:

        fig1 = px.bar(
            df,
            x="decennie",
            y="nombre_films",
            title="Production par décennie"
        )

        afficher_graphique(fig1)

        notes_decennie = df.dropna(
            subset=["note_moyenne"]
        )

        fig2 = px.line(
            notes_decennie,
            x="decennie",
            y="note_moyenne",
            markers=True,
            title="Évolution de la note moyenne"
        )

        fig2.update_yaxes(range=[0, 10])

        afficher_graphique(fig2)

        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )

        telecharger_csv(
            df,
            "evolution_imdb.csv"
        )

    else:
        st.info("Aucune donnée pour cette période.")


# =====================================================
# PAGE 4 — CLASSEMENT DES FILMS
# =====================================================

elif page == "Classement des films":

    st.title("Classement des films IMDb")

    afficher_kpi()

    st.divider()

    st.subheader("Top 10 des films les mieux notés")

    top = requete_filtree(f"""
        SELECT
            D.titre AS Titre,
            F.annee AS Annee,
            F.note_moyenne AS Note,
            F.nb_votes AS Votes
        FROM main.fait_film F
        INNER JOIN main.dim_film D
            ON F.tconst = D.tconst
        WHERE {condition}
          AND F.nb_votes >= ?
          AND F.note_moyenne IS NOT NULL
        ORDER BY
            F.note_moyenne DESC,
            F.nb_votes DESC,
            D.titre
        LIMIT 10
    """, (votes_min,))

    st.dataframe(
        top,
        width="stretch",
        hide_index=True
    )

    if not top.empty:
        telecharger_csv(
            top,
            "top_10_films_imdb.csv"
        )

    st.divider()

    st.subheader("Recherche d'un film")

    recherche = st.text_input(
        "Rechercher par titre",
        placeholder="Batman, Titanic, Avatar..."
    )

    if recherche.strip():

        resultat = requete_filtree(f"""
            SELECT
                D.titre AS Titre,
                F.annee AS Annee,
                F.note_moyenne AS Note,
                F.nb_votes AS Votes
            FROM main.fait_film F
            INNER JOIN main.dim_film D
                ON F.tconst = D.tconst
            WHERE {condition}
              AND D.titre ILIKE ?
            ORDER BY
                F.nb_votes DESC NULLS LAST,
                D.titre
            LIMIT 100
        """, (f"%{recherche.strip()}%",))

        if resultat.empty:
            st.info("Aucun film trouvé.")

        else:
            st.dataframe(
                resultat,
                width="stretch",
                hide_index=True
            )

            telecharger_csv(
                resultat,
                "recherche_imdb.csv"
            )

    st.divider()

    st.subheader("Distribution des notes")

    notes_distribution = requete_filtree(f"""
        SELECT
            FLOOR(F.note_moyenne)
                AS tranche_note,
            COUNT(*) AS nombre_films
        FROM main.fait_film F
        WHERE {condition}
          AND F.note_moyenne IS NOT NULL
        GROUP BY tranche_note
        ORDER BY tranche_note
    """)

    if not notes_distribution.empty:

        fig = px.bar(
            notes_distribution,
            x="tranche_note",
            y="nombre_films",
            title="Distribution des notes IMDb"
        )

        afficher_graphique(fig)


# =====================================================
# PAGE 5 — QUALITÉ DES DONNÉES
# =====================================================

elif page == "Qualité des données":

    st.title("Qualité des données IMDb")

    st.markdown(
        "Analyse des valeurs manquantes "
        "dans le Data Warehouse."
    )

    qualite = executer_requete("""
        SELECT
            COUNT(*) AS total_films,

            COUNT(*) FILTER (
                WHERE annee IS NULL
            ) AS annee_manquante,

            COUNT(*) FILTER (
                WHERE duree_minutes IS NULL
            ) AS duree_manquante,

            COUNT(*) FILTER (
                WHERE note_moyenne IS NULL
            ) AS note_manquante

        FROM main.fait_film
    """)

    total = int(qualite["total_films"].iloc[0])

    st.metric(
        "Total des films",
        format_nombre(total)
    )

    st.dataframe(
        qualite,
        width="stretch",
        hide_index=True
    )

    manquants = pd.DataFrame({
        "Champ": ["Année", "Durée", "Note"],
        "Valeurs manquantes": [
            int(qualite["annee_manquante"].iloc[0]),
            int(qualite["duree_manquante"].iloc[0]),
            int(qualite["note_manquante"].iloc[0])
        ]
    })

    manquants["Pourcentage"] = (
        manquants["Valeurs manquantes"]
        / total * 100
    ).round(2)

    fig = px.bar(
        manquants,
        x="Champ",
        y="Pourcentage",
        text="Pourcentage",
        title="Taux de valeurs manquantes"
    )

    afficher_graphique(fig)

    st.success(
        "Dernière exécution communiquée : "
        "16 tests dbt réussis sur 16."
    )

    st.caption(
        "Les indicateurs de qualité sont globaux. "
        "Ils ne dépendent pas des filtres d'analyse."
    )


# =====================================================
# PAGE 6 — PRÉDICTION MACHINE LEARNING
# =====================================================

elif page == "Prédiction ML":

    st.title("Prédiction de la note IMDb")

    st.markdown(
        "Estimer la note moyenne d'un film "
        "en fonction de ses caractéristiques."
    )

    st.info(
        "Le modèle utilise Random Forest. "
        "Il prend en compte l'année, "
        "la durée et les genres du film."
    )

    if not MODEL_PATH.exists():

        st.error(
            "Modèle ML introuvable. "
            "Exécute la cellule de sauvegarde "
            "dans notebooks/prediction.ipynb."
        )

        st.stop()

    try:
        artefact = charger_modele(
            str(MODEL_PATH),
            MODEL_PATH.stat().st_mtime_ns
        )
    except Exception as e:
        st.error(
            f"Impossible de charger le modèle : {e}"
        )
        st.stop()

    modele = artefact["model"]
    features = artefact["features"]
    genres_ml = artefact["genres"]

    st.divider()

    st.subheader("Caractéristiques du film")

    c1, c2 = st.columns(2)

    with c1:

        annee = st.number_input(
            "Année de sortie",
            min_value=1880,
            max_value=2035,
            value=date.today().year,
            step=1
        )

    with c2:

        duree = st.number_input(
            "Durée du film (minutes)",
            min_value=1,
            max_value=500,
            value=100,
            step=1
        )

    genres_choisis = st.multiselect(
        "Sélectionner les genres",
        options=[
            g for g in genres_ml
            if g != "Unknown"
        ],
        default=[]
    )

    st.caption(
        "Tu peux sélectionner plusieurs genres."
    )

    st.divider()

    if st.button(
        "Prédire la note",
        type="primary",
        use_container_width=True
    ):

        # Créer une ligne avec exactement
        # les colonnes utilisées à l'entraînement

        entree = pd.DataFrame(
            0.0,
            index=[0],
            columns=features
        )

        entree.loc[0, "annee"] = annee

        entree.loc[
            0, "duree_log"
        ] = np.log1p(duree)

        # Encoder les genres
        if genres_choisis:

            for genre in genres_choisis:

                colonne = "genre_" + genre

                if colonne in entree.columns:
                    entree.loc[0, colonne] = 1

        elif "genre_Unknown" in entree.columns:

            entree.loc[
                0, "genre_Unknown"
            ] = 1

        # Faire la prédiction
        prediction = float(
            modele.predict(entree)[0]
        )

        prediction = float(
            np.clip(prediction, 1, 10)
        )

        st.success("Prédiction effectuée")

        st.metric(
            "Note IMDb estimée",
            f"{prediction:.2f} / 10"
        )

        # Affichage graphique de la note
        fig = px.bar(
            pd.DataFrame({
                "Indicateur": ["Note estimée"],
                "Note": [prediction]
            }),
            x="Note",
            y="Indicateur",
            orientation="h",
            range_x=[0, 10],
            title="Estimation de la note IMDb"
        )

        fig.update_layout(height=260)
        afficher_graphique(fig)

        st.subheader("Performance du modèle")

        col1, col2 = st.columns(2)

        mae = artefact.get("mae_test")
        r2 = artefact.get("r2_test")

        col1.metric(
            "MAE sur le test",
            f"{mae:.4f}" if mae is not None
            else "N/A"
        )

        col2.metric(
            "R² sur le test",
            f"{r2:.4f}" if r2 is not None
            else "N/A"
        )

        st.warning(
            "Cette note est une estimation "
            "expérimentale, et non une prévision "
            "garantie. Le modèle a été évalué "
            "sur des films IMDb déjà notés."
        )

    st.divider()

    st.markdown("### À propos du modèle")

    st.write(
        "Algorithme : Random Forest Regressor"
    )

    st.write(
        "Variables : année, durée transformée "
        "avec log1p et genres encodés."
    )

    st.write(
        "Validation : séparation temporelle "
        "entre films d'entraînement et de test."
    )

    st.caption(
        "Les prédictions en dehors de la période "
        "d'entraînement doivent être interprétées "
        "avec prudence."
    )


# =====================================================
# PIED DE PAGE
# =====================================================

st.divider()

st.caption(
    "IMDb Analytics | Projet BI Cinéma | "
    "Python • DuckDB • dbt • Streamlit • "
    "Plotly • Machine Learning"
)
