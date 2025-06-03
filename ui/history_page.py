import streamlit as st


def history_page():
    st.header("🕑 Histórico de Problemas")
    history = st.session_state.get("history", [])
    if not history:
        st.info("Nenhum problema resolvido nesta sessão.")
        return
    for idx, item in enumerate(reversed(history)):
        with st.expander(f"Problema #{len(history)-idx} – {item['method']} – Z={item['z']:.3f}"):
            st.json(item, expanded=False)

    # download JSON
    import json

    if st.button("⬇️ Baixar histórico JSON"):
        st.download_button(
            "Download",
            json.dumps(history, indent=2),
            file_name="historico_otimizacao.json",
            mime="application/json",
        )