import inspect
import textwrap

import streamlit as st

from fullcollab_streamlit import FULLCOLLAB_DEMOS
from emma_diag import BOARD_FABRICANTS_DEMOS

def main():
    st.title("Streamlit cours graphe")
    allDiag = {**vars(FULLCOLLAB_DEMOS), **vars(BOARD_FABRICANTS_DEMOS)}
    with st.sidebar:
        st.header("Configuration")
        selected_page = st.selectbox(
            label="Choose an example",
            options= list(allDiag.keys()),
        )
        demo = (
            allDiag[selected_page]
        )

    demo()

if __name__ == "__main__":
    st.set_page_config(
        page_title="Streamlit cours graphe"
    )
    main()
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            '<h6>présentation par Emmanuella D’Almeida et Quentin Vermeersch</h6>',
            unsafe_allow_html=True,
        )
