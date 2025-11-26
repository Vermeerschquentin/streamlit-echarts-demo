import pandas as pd
from streamlit_echarts import st_echarts


def load_data(file_path='./data/pointsDeVente-tous.csv'):
    """Charge les données du fichier CSV"""
    try:
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['dateID'].astype(str), format='%Y%m%d')
        return df
    except Exception as e:
        print(f"Erreur lors du chargement: {e}")
        return None


def render_produits_par_categorie(df):
    """Graphique: Nombre de produits uniques par catégorie"""
    produits_uniques = df.groupby('catID')['produit ID'].nunique()
    
    options = {
        "title": {"text": "Nombre de produits uniques par catégorie"},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "xAxis": {
            "type": "category",
            "data": [str(x) for x in produits_uniques.index.tolist()],
            "axisLabel": {"rotate": 45}
        },
        "yAxis": {"type": "value", "name": "Nombre de produits"},
        "series": [{
            "data": produits_uniques.values.tolist(),
            "type": "bar",
            "itemStyle": {"color": "#5470c6"}
        }]
    }
    st_echarts(options=options, height="500px")


def render_produits_par_fabricant(df, top_n=20):
    """Graphique: Top fabricants par nombre de produits uniques"""
    produits_uniques = df.groupby('fabID')['produit ID'].nunique().nlargest(top_n)
    
    options = {
        "title": {"text": f"Top {top_n} Fabricants par nombre de produits uniques"},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "xAxis": {
            "type": "category",
            "data": [str(x) for x in produits_uniques.index.tolist()],
            "axisLabel": {"rotate": 45}
        },
        "yAxis": {"type": "value", "name": "Nombre de produits"},
        "series": [{
            "data": produits_uniques.values.tolist(),
            "type": "bar",
            "itemStyle": {"color": "#91cc75"}
        }]
    }
    st_echarts(options=options, height="500px")


def render_magasins_par_categorie(df):
    """Graphique: Nombre de magasins uniques par catégorie"""
    magasins_uniques = df.groupby('catID')['magID'].nunique()
    
    options = {
        "title": {"text": "Nombre de magasins distincts par catégorie"},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "xAxis": {
            "type": "category",
            "data": [str(x) for x in magasins_uniques.index.tolist()],
            "axisLabel": {"rotate": 45}
        },
        "yAxis": {"type": "value", "name": "Nombre de magasins"},
        "series": [{
            "data": magasins_uniques.values.tolist(),
            "type": "bar",
            "itemStyle": {"color": "#fac858"}
        }]
    }
    st_echarts(options=options, height="500px")


def render_magasins_par_fabricant(df, top_n=20):
    """Graphique: Top fabricants par nombre de magasins uniques"""
    magasins_uniques = df.groupby('fabID')['magID'].nunique().nlargest(top_n)
    
    options = {
        "title": {"text": f"Top {top_n} Fabricants par nombre de magasins distincts"},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "xAxis": {
            "type": "category",
            "data": [str(x) for x in magasins_uniques.index.tolist()],
            "axisLabel": {"rotate": 45}
        },
        "yAxis": {"type": "value", "name": "Nombre de magasins"},
        "series": [{
            "data": magasins_uniques.values.tolist(),
            "type": "bar",
            "itemStyle": {"color": "#ee6666"}
        }]
    }
    st_echarts(options=options, height="500px")


def render_tendance_produits_mensuelle(df):
    """Graphique: Tendance du nombre de produits uniques par mois"""
    produits_par_mois = df.groupby(df['date'].dt.to_period('M'))['produit ID'].nunique()
    
    options = {
        "title": {"text": "Tendance du nombre de produits uniques par mois"},
        "tooltip": {"trigger": "axis"},
        "xAxis": {
            "type": "category",
            "data": [str(x) for x in produits_par_mois.index.tolist()],
            "axisLabel": {"rotate": 45}
        },
        "yAxis": {"type": "value", "name": "Nombre de produits"},
        "series": [{
            "data": produits_par_mois.values.tolist(),
            "type": "line",
            "smooth": True,
            "itemStyle": {"color": "#73c0de"},
            "areaStyle": {"opacity": 0.3}
        }],
        "grid": {"containLabel": True}
    }
    st_echarts(options=options, height="500px")


def render_sankey_diagram(df):
    """Diagramme Sankey: Flux Magasin -> Catégories -> Fournisseurs"""
    # Sélectionner le magasin par défaut (le plus fréquent)
    default_magID = df['magID'].value_counts().index[0]
    df_mag = df[df['magID'] == default_magID]
    
    # Top 10 catégories pour ce magasin
    top_categories = df_mag.groupby('catID')['produit ID'].nunique().nlargest(10)
    
    # Top 5 fournisseurs par catégorie
    nodes = []
    links = []
    
    # Ajouter le nœud du magasin
    nodes.append({"name": f"Magasin {default_magID}"})
    
    # Ajouter les catégories et leurs liens
    for cat_id, num_products in top_categories.items():
        cat_name = f"Cat {cat_id}"
        nodes.append({"name": cat_name})
        links.append({
            "source": f"Magasin {default_magID}",
            "target": cat_name,
            "value": num_products
        })
        
        # Ajouter les fournisseurs pour cette catégorie
        df_cat = df_mag[df_mag['catID'] == cat_id]
        top_suppliers = df_cat.groupby('fabID')['produit ID'].nunique().nlargest(5)
        
        for fab_id, num_prod_fab in top_suppliers.items():
            fab_name = f"Fab {fab_id}"
            if {"name": fab_name} not in nodes:
                nodes.append({"name": fab_name})
            links.append({
                "source": cat_name,
                "target": fab_name,
                "value": num_prod_fab
            })
    
    options = {
        "title": {
            "text": "Flux: Magasin → Catégories → Fournisseurs",
            "subtext": "Basé sur le nombre de produits uniques"
        },
        "tooltip": {"trigger": "item", "triggerOn": "mousemove"},
        "series": [{
            "type": "sankey",
            "data": nodes,
            "links": links,
            "emphasis": {"focus": "adjacency"},
            "lineStyle": {"color": "gradient", "curveness": 0.5}
        }]
    }
    st_echarts(options=options, height="700px")


# Dictionnaire des visualisations disponibles
FULLCOLLAB_DEMOS = {
    "Produits par Catégorie": (
        render_produits_par_categorie,
        "Nombre de produits uniques par catégorie"
    ),
    "Produits par Fabricant": (
        render_produits_par_fabricant,
        "Top 20 fabricants par nombre de produits"
    ),
    "Magasins par Catégorie": (
        render_magasins_par_categorie,
        "Nombre de magasins distincts par catégorie"
    ),
    "Magasins par Fabricant": (
        render_magasins_par_fabricant,
        "Top 20 fabricants par nombre de magasins"
    ),
    "Tendance Mensuelle": (
        render_tendance_produits_mensuelle,
        "Évolution du nombre de produits par mois"
    ),
    "Diagramme Sankey": (
        render_sankey_diagram,
        "Flux Magasin → Catégories → Fournisseurs"
    )
}
