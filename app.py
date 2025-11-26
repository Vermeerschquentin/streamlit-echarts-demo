import inspect
import textwrap

import streamlit as st

from fullcollab_streamlit import FULLCOLLAB_DEMOS
from emma_diag import BOARD_FABRICANTS_DEMOS


# --- Configuration de page doit être AVANT tout code Streamlit ---
st.set_page_config(page_title="Streamlit cours graphe")


def load_demos(module):
    """Retourne uniquement les attributs appelables (fonctions) du module."""
    return {
        name: obj
        for name, obj in vars(module).items()
        if callable(obj) and not name.startswith("__")
    }


def main():
    st.title("Streamlit cours graphe")

    # On charge proprement toutes les démos
    allDiag = {
        **load_demos(FULLCOLLAB_DEMOS),
        **load_demos(BOARD_FABRICANTS_DEMOS)
    }

    with st.sidebar:
        st.header("Configuration")
        selected_page = st.selectbox(
            label="Choose an example",
            options=list(allDiag.keys()),
        )

    # Récupération et exécution de la démo
    demo = allDiag.get(selected_page)
    if demo:
        demo()
    else:
        st.error("Erreur : la démo sélectionnée est introuvable.")


if __name__ == "__main__":
    main()

    # Footer dans la sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            '<h6>présentation par Emmanuella D’Almeida et Quentin Vermeersch</h6>',
            unsafe_allow_html=True,
        )
