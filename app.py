import inspect
import textwrap

import streamlit as st

from back import FULLCOLLAB_DEMOS

def main():
    st.title("Streamlit cours graphe")

    with st.sidebar:
        st.header("Configuration")
        selected_page = st.selectbox(
            label="Choose an example",
            options= list(FULLCOLLAB_DEMOS.keys()),
        )
        demo = (
            FULLCOLLAB_DEMOS[selected_page]
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
