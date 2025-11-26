import datetime
import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts, JsCode

str
# Variables globales pour stocker les données
_cached_produits = None
_cached_pdv = None


def load_data():
    """Charge les données des fichiers CSV"""
    global _cached_produits, _cached_pdv

    if _cached_produits is not None and _cached_pdv is not None:
        return _cached_produits, _cached_pdv

    try:
        file_produits = "./data/produits-tous.csv"
        file_pdv = "./data/pointsDeVente-tous.csv"

        col_produits = ['dateID', 'prodID', 'catID', 'fabID']
        produits = pd.read_csv(file_produits, sep=";", header=None, names=col_produits)

        col_pdv = ['dateID', 'prodID', 'catID', 'fabID', 'magID']
        pdv = pd.read_csv(file_pdv, sep=",", header=5, names=col_pdv)

        # Conversion des dates
        produits['date'] = pd.to_datetime(produits['dateID'].astype(str), format='%Y%m%d', errors='coerce')
        pdv['date'] = pd.to_datetime(pdv['dateID'].astype(str), format='%Y%m%d', errors='coerce')

        _cached_produits = produits
        _cached_pdv = pdv

        return produits, pdv
    except Exception as e:
        st.error(f"Erreur lors du chargement: {e}")
        return None, None


def render_top_magasins_categorie():
    """Top 10 magasins par catégorie"""
    produits, pdv = load_data()
    if pdv is None:
        return

    listeCats = sorted(pdv['catID'].unique())
    catID = st.selectbox("Sélectionner une catégorie", listeCats, key="cat_top_mag")

    subset = pdv[pdv['catID'] == catID]
    top10_mag = subset.groupby('magID')['prodID'].count().nlargest(10).sort_values()

    options = {
        "title": {"text": f"Top 10 magasins pour la catégorie {catID}"},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "xAxis": {"type": "value", "name": "Nombre de produits"},
        "yAxis": {
            "type": "category",
            "data": [str(x) for x in top10_mag.index.tolist()],
            "name": "ID du magasin"
        },
        "series": [{
            "data": top10_mag.values.tolist(),
            "type": "bar",
            "itemStyle": {"color": "#5470c6"}
        }]
    }
    st_echarts(options=options, height="500px")

    # Afficher le nombre d'acteurs
    fabricants = subset['fabID'].nunique()
    st.metric("Nombre de fabricants dans cette catégorie", fabricants)


def render_score_sante_fabricant():
    """Score santé d'un fabricant dans une catégorie"""
    produits, pdv = load_data()
    if pdv is None:
        return

    col1, col2 = st.columns(2)

    with col1:
        listeCats = sorted(pdv['catID'].unique())
        catID = st.selectbox("Catégorie", listeCats, key="cat_score")

    with col2:
        listeFabs = sorted(pdv['fabID'].unique())
        fabID = st.selectbox("Fabricant", listeFabs, key="fab_score")

    subset = pdv[pdv['catID'] == catID]
    total_cat = subset['prodID'].nunique()
    total_fab = subset[subset['fabID'] == fabID]['prodID'].nunique()
    score_sante = (total_fab / total_cat * 100) if total_cat > 0 else 0

    # Gauge avec ECharts
    options = {
        "title": {"text": f"Score Santé Fab {fabID} - Cat {catID}", "left": "center"},
        "series": [{
            "type": "gauge",
            "startAngle": 180,
            "endAngle": 0,
            "min": 0,
            "max": 100,
            "splitNumber": 10,
            "axisLine": {
                "lineStyle": {
                    "width": 30,
                    "color": [
                        [0.3, "#fd666d"],
                        [0.7, "#37a2da"],
                        [1, "#67e0e3"]
                    ]
                }
            },
            "pointer": {
                "itemStyle": {"color": "auto"}
            },
            "axisTick": {"distance": -30, "length": 8},
            "splitLine": {"distance": -30, "length": 30},
            "axisLabel": {"distance": -20, "fontSize": 12},
            "detail": {
                "valueAnimation": True,
                "formatter": "{value}%",
                "fontSize": 30,
                "offsetCenter": [0, "70%"]
            },
            "data": [{"value": score_sante, "name": "Score"}]
        }]
    }
    st_echarts(options=options, height="400px")

    # Moyenne de produits par fabricant
    moyenne = subset.groupby('fabID')['prodID'].nunique().mean()
    st.metric(f"Moyenne de produits de catégorie {catID} par fabricant", f"{moyenne:.1f}")


def render_presence_marche():
    """Fabricants les plus présents sur le marché"""
    produits, pdv = load_data()
    if pdv is None:
        return

    topN = st.slider("Nombre de fabricants à afficher", 5, 20, 10, step=5, key="top_market")

    presence_fab = pdv.groupby('fabID')['magID'].nunique().nlargest(topN)

    options = {
        "title": {"text": f"Top {topN} fabricants présents dans le plus de magasins"},
        "tooltip": {"trigger": "item"},
        "legend": {"orient": "vertical", "left": "left"},
        "series": [{
            "type": "pie",
            "radius": "50%",
            "data": [{"value": v, "name": str(k)} for k, v in presence_fab.items()],
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)"
                }
            }
        }]
    }
    st_echarts(options=options, height="500px")


def render_disponibilite_magasins():
    """Taux de disponibilité par magasin (Dumbbell chart)"""
    produits, pdv = load_data()
    if pdv is None:
        return

    listeMags = sorted(pdv['magID'].unique())
    listeFabs = sorted(pdv['fabID'].unique())

    col1, col2, col3 = st.columns(3)

    with col1:
        magA = st.selectbox("Magasin A", listeMags, key="magA")
    with col2:
        magB = st.selectbox("Magasin B", listeMags, index=min(1, len(listeMags) - 1), key="magB")
    with col3:
        fabID = st.selectbox("Fabricant", listeFabs, key="fab_dumbbell")

    subset_fab = pdv[pdv['fabID'] == fabID]
    prod_magA = subset_fab[subset_fab['magID'] == magA].groupby('catID')['prodID'].nunique()
    prod_magB = subset_fab[subset_fab['magID'] == magB].groupby('catID')['prodID'].nunique()

    df_dumbbell = pd.DataFrame({
        'Magasin A': prod_magA,
        'Magasin B': prod_magB
    }).fillna(0)

    categories = [str(cat) for cat in df_dumbbell.index]

    series = []

    # Lignes de connexion
    for cat in df_dumbbell.index:
        valA = int(df_dumbbell.loc[cat, 'Magasin A'])
        valB = int(df_dumbbell.loc[cat, 'Magasin B'])
        series.append({
            "type": "line",
            "lineStyle": {"color": "gray", "width": 2},
            "symbol": "none",
            "data": [[valA, str(cat)], [valB, str(cat)]]
        })

    # Points pour Magasin A
    series.append({
        "name": f"Magasin {magA}",
        "type": "scatter",
        "symbolSize": 12,
        "itemStyle": {"color": "#5470c6"},
        "data": [[int(df_dumbbell.loc[cat, 'Magasin A']), str(cat)] for cat in df_dumbbell.index]
    })

    # Points pour Magasin B
    series.append({
        "name": f"Magasin {magB}",
        "type": "scatter",
        "symbolSize": 12,
        "itemStyle": {"color": "#91cc75"},
        "data": [[int(df_dumbbell.loc[cat, 'Magasin B']), str(cat)] for cat in df_dumbbell.index]
    })

    options = {
        "title": {"text": f"Disponibilité du fabricant {fabID} : {magA} vs {magB}"},
        "tooltip": {"trigger": "item"},
        "legend": {"data": [f"Magasin {magA}", f"Magasin {magB}"]},
        "xAxis": {"type": "value", "name": "Nombre de produits disponibles"},
        "yAxis": {"type": "category", "data": categories, "name": "Catégorie"},
        "series": series
    }

    st_echarts(options=options, height="600px")


def render_ratio_accords_produits():
    """Ratio accords / produits par fabricant"""
    produits, pdv = load_data()
    if pdv is None:
        return

    listeCats = sorted(pdv['catID'].unique())
    catID = st.selectbox("Catégorie", listeCats, key="cat_ratio")

    # Sélection de période
    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input("Date début", datetime.date(2022, 1, 1), key="debut_ratio")
    with col2:
        date_fin = st.date_input("Date fin", datetime.datetime.now().date(), key="fin_ratio")

    subset_cat = pdv[pdv['catID'] == catID].copy()

    # Filtrer par dates
    start_date = pd.to_datetime(date_debut)
    end_date = pd.to_datetime(date_fin) + pd.Timedelta(days=1)
    subset_cat = subset_cat[(subset_cat['date'] >= start_date) & (subset_cat['date'] <= end_date)]

    acc_per_fab = subset_cat.groupby('fabID')['prodID'].count().rename('nb_accords')
    prods_per_fab = subset_cat.groupby('fabID')['prodID'].nunique().rename('nb_produits')

    ratio_df = pd.concat([acc_per_fab, prods_per_fab], axis=1).fillna(0)
    ratio_df['ratio'] = ratio_df.apply(
        lambda r: r['nb_accords'] / r['nb_produits'] if r['nb_produits'] > 0 else 0,
        axis=1
    )
    ratio_df = ratio_df.sort_values('ratio', ascending=False).head(30).reset_index()

    if ratio_df.empty:
        st.warning("Pas de données pour cette catégorie / période.")
        return

    # Scatter plot avec bulles
    options = {
        "title": {"text": f"Ratio accords/produits (cat {catID})"},
        "tooltip": {
            "trigger": "item",
            "formatter": JsCode("""
                function(params) {
                    return 'Fabricant: ' + params.data[3] + '<br/>' +
                           'Ratio: ' + params.data[0].toFixed(2) + '<br/>' +
                           'Accords: ' + params.data[4] + '<br/>' +
                           'Produits: ' + params.data[5];
                }
            """).js_code
        },
        "xAxis": {"type": "value", "name": "Ratio accords / produit"},
        "yAxis": {
            "type": "category",
            "data": ratio_df['fabID'].astype(str).tolist(),
            "name": "Fabricant"
        },
        "visualMap": {
            "min": ratio_df['ratio'].min(),
            "max": ratio_df['ratio'].max(),
            "dimension": 0,
            "orient": "vertical",
            "right": 10,
            "top": "center",
            "text": ["HIGH", "LOW"],
            "calculable": True,
            "inRange": {"color": ["#50a3ba", "#eac736", "#d94e5d"]}
        },
        "series": [{
            "type": "scatter",
            "symbolSize": JsCode("""
                function(data) {
                    return Math.sqrt(data[4]) * 2;
                }
            """).js_code,
            "data": [
                [
                    row['ratio'],
                    idx,
                    row['nb_accords'],
                    str(row['fabID']),
                    row['nb_accords'],
                    row['nb_produits']
                ]
                for idx, row in ratio_df.iterrows()
            ],
            "emphasis": {"focus": "self"}
        }]
    }
    st_echarts(options=options, height="650px")
def render_intensite_concurrentielle():
    """Intensité concurrentielle par catégorie (HHI)"""

    produits, pdv = load_data()
    if pdv is None:
        return

    listeCats = sorted(pdv['catID'].unique())
    catID = st.selectbox("Catégorie", listeCats, key="cat_hhi")

    subset_cat = pdv[pdv['catID'] == catID]
    prod_counts_by_fab = subset_cat.groupby('fabID')['prodID'].nunique()
    total_products_cat = prod_counts_by_fab.sum()

    if total_products_cat == 0:
        st.warning("Aucun produit enregistré pour cette catégorie.")
        return

    market_share = prod_counts_by_fab / total_products_cat
    hhi = (market_share ** 2).sum()

    if hhi < 0.01:
        interp = "Concurrence faible"
    elif hhi < 0.03:
        interp = "Concurrence modérée"
    else:
        interp = "Concurrence élevée"

    ms_df = pd.DataFrame({
        "share_frac": market_share.values,
        "nb_products": prod_counts_by_fab.values
    }, index=market_share.index.astype(str)).sort_values("share_frac", ascending=False).head(20)
    st.write(ms_df)

    # Graphique ECharts
    x_data = [str(x) for x in ms_df.index.tolist()]
    y_data = [float(x) for x in ms_df['share_frac'].tolist()]

    options = {
        "title": {"text": f"Parts de marché - Catégorie {catID}"},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "xAxis": {"type": "category", "data": x_data, "axisLabel": {"rotate": 45}},
        "yAxis": {"type": "value", "name": "Part de marché"},
        "series": [{"type": "bar", "data": y_data, "itemStyle": {"color": "#ee6666"}}]
    }
    st_echarts(options=options, height="500px")

    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"HHI pour la catégorie {catID}", f"{hhi:.4f}")
    with col2:
        st.metric("Interprétation", interp)


def render_croissance_catalogue():
    """Croissance du catalogue (nouveaux produits mensuels)"""
    produits, pdv = load_data()
    if produits is None:
        return

    col1, col2 = st.columns(2)

    with col1:
        listeCats = sorted(produits['catID'].unique())
        catID = st.selectbox("Catégorie", listeCats, key="cat_growth")

    with col2:
        growth_scope = st.radio("Vue", ("Toute la catégorie", "Par fabricant"), key="scope_growth")

    prods_scope = produits[produits['catID'] == catID].copy()

    if growth_scope == "Par fabricant":
        listeFabs = sorted(prods_scope['fabID'].unique())
        fabID = st.selectbox("Fabricant", listeFabs, key="fab_growth")
        prods_scope = prods_scope[prods_scope['fabID'] == fabID]

    if 'date' in prods_scope.columns:
        first_seen = prods_scope.groupby('prodID')['date'].min().dropna()
        first_seen_month = first_seen.dt.to_period('M').value_counts().sort_index()

        idx = pd.to_datetime(first_seen_month.index.to_timestamp())
        df_growth = pd.DataFrame({
            'month': idx,
            'nouv_prod': first_seen_month.values
        }).sort_values('month')

        if df_growth.empty:
            st.warning("Pas assez de données temporelles.")
            return

        # Convertir en format pour ECharts
        months_str = df_growth['month'].dt.strftime('%Y-%m').tolist()

        options = {
            "title": {"text": f"Nouveaux produits par mois - {growth_scope} (cat {catID})"},
            "tooltip": {"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "data": months_str,
                "axisLabel": {"rotate": 45}
            },
            "yAxis": {"type": "value", "name": "Nouveaux produits"},
            "series": [{
                "data": df_growth['nouv_prod'].values.tolist(),
                "type": "line",
                "smooth": True,
                "itemStyle": {"color": "#73c0de"},
                "areaStyle": {"opacity": 0.3}
            }]
        }
        st_echarts(options=options, height="500px")


# Dictionnaire des visualisations disponibles
BOARD_FABRICANTS_DEMOS = {
    "Top Magasins par Catégorie": render_top_magasins_categorie,
    "Score Santé Fabricant": render_score_sante_fabricant,
    "Présence sur le Marché": render_presence_marche,
    "Disponibilité Magasins": render_disponibilite_magasins,
    "Ratio Accords/Produits": render_ratio_accords_produits,
    "Intensité Concurrentielle": render_intensite_concurrentielle,
    "Croissance Catalogue": render_croissance_catalogue
}