import inspect
import textwrap

import streamlit as st

from fullcollab_streamlit import FULLCOLLAB_DEMOS
from emma_diag import BOARD_FABRICANTS_DEMOS


st.set_page_config(page_title="Streamlit cours graphe")


def load_demos(src):
    """Retourne un dict {nom: fonction} depuis un module, un dict ou un objet."""
    demos = {}

    # Cas 1 : c’est un module ou un objet avec __dict__
    if hasattr(src, "__dict__"):
        items = vars(src).items()

    # Cas 2 : c’est déjà un dict
    elif isinstance(src, dict):
        items = src.items()

    else:
        # Cas 3 : objet sans __dict__
        items = ((name, getattr(src, name)) for name in dir(src))

    # On garde uniquement les fonctions appelables
    for name, obj in items:
        if callable(obj) and not name.startswith("__"):
            demos[name] = obj

    return demos


def main():
    st.title("Streamlit cours graphe")

    # Chargement sécurisé toutes les démos
    allDiag = {
        **load_demos(FULLCOLLAB_DEMOS),
        **load_demos(BOARD_FABRICANTS_DEMOS),
    }

    with st.sidebar:
        st.header("Configuration")
        selected_page = st.selectbox(
            label="Choose an example",
            options=list(allDiag.keys()),
        )

    demo = allDiag.get(selected_page)

    if demo:
        demo()
    else:
        st.error("La démo sélectionnée est introuvable.")


if __name__ == "__main__":
    main()

    with st.sidebar:
        st.markdown("---")
        st.markdown(
            '<h6>présentation par Emmanuella D’Almeida et Quentin Vermeersch</h6>',
            unsafe_allow_html=True,
        )
