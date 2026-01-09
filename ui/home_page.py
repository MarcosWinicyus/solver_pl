
import streamlit as st

from ui.lang import t

import base64
import os

def home_page():
    # Helper para carregar imagem e converter para base64
    def get_img_as_base64(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    img_path = "images/logo.svg"
    img_base64 = get_img_as_base64(img_path)

    # Hero Section: Logo + Nome (Centralizados)
    st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 40px; margin-top: -20px;">
            <img src="data:image/svg+xml;base64,{img_base64}" width="100">
            <h1 style="font-size: 3.5rem; margin: 0;">
                <span style="color: var(--text-color);">Solver</span> <span style="color: #4CAF50;">LP</span>
            </h1>
        </div>
    """, unsafe_allow_html=True)

    # Subtitulo
    st.markdown(f"""
    <div style="text-align: center; margin-top: -20px; margin-bottom: 50px;">
        <p style="font-size: 1.25rem; color: var(--text-color); font-weight: 300; opacity: 0.8;">
            {t("home.subtitle")}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- Linha 1: Solvers (Principais) ---
    c_solv1, c_solv2 = st.columns(2)
    
    with c_solv1:
        st.markdown(f"""
        <div style="background-color: var(--secondary-background-color); padding: 20px; border-radius: 10px; border: 1px solid rgba(128, 128, 128, 0.2); height: 100%;">
            <h3 style="color: #00CCFF;">{t("home.simplex_title")}</h3>
            <p style="font-size: 0.9rem; opacity: 0.8;">
                {t("home.simplex_desc")}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with c_solv2:
        st.markdown(f"""
        <div style="background-color: var(--secondary-background-color); padding: 20px; border-radius: 10px; border: 1px solid rgba(128, 128, 128, 0.2); height: 100%;">
            <h3 style="color: #28a745;">{t("home.bab_title")}</h3>
            <p style="font-size: 0.9rem; opacity: 0.8;">
                {t("home.bab_desc")}
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    
    # --- Linha 2: Ferramentas (Novidades) ---
    c_tool1, c_tool2, c_tool3 = st.columns(3)
    
    with c_tool1:
        st.markdown(f"""
        <div style="background-color: var(--secondary-background-color); padding: 20px; border-radius: 10px; border: 1px solid rgba(128, 128, 128, 0.2); height: 100%;">
            <h3 style="color: #ffc107;">{t("home.duality_title")}</h3>
            <p style="font-size: 0.9rem; opacity: 0.8;">
                {t("home.duality_desc")}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c_tool2:
        st.markdown(f"""
        <div style="background-color: var(--secondary-background-color); padding: 20px; border-radius: 10px; border: 1px solid rgba(128, 128, 128, 0.2); height: 100%;">
            <h3 style="color: #e91e63;">{t("home.sensitivity_title")}</h3>
            <p style="font-size: 0.9rem; opacity: 0.8;">
                {t("home.sensitivity_desc")}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c_tool3:
        st.markdown(f"""
        <div style="background-color: var(--secondary-background-color); padding: 20px; border-radius: 10px; border: 1px solid rgba(128, 128, 128, 0.2); height: 100%;">
            <h3 style="color: #00bcd4;">{t("home.std_form_title")}</h3>
            <p style="font-size: 0.9rem; opacity: 0.8;">
                {t("home.std_form_desc")}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")

    # --- Linha 3: Recursos (Biblioteca, Histórico e Multi-Idioma) ---
    c_res1, c_res2, c_res3 = st.columns(3)
    
    with c_res1:
        st.markdown(f"""
        <div style="background-color: var(--secondary-background-color); padding: 20px; border-radius: 10px; border: 1px solid rgba(128, 128, 128, 0.2); height: 100%;">
            <h3 style="color: #9b59b6;">{t("home.library_title")}</h3>
            <p style="font-size: 0.9rem; opacity: 0.8;">
                 {t("home.library_desc")}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c_res2:
        st.markdown(f"""
        <div style="background-color: var(--secondary-background-color); padding: 20px; border-radius: 10px; border: 1px solid rgba(128, 128, 128, 0.2); height: 100%;">
            <h3 style="color: #e67e22;">{t("home.history_title")}</h3>
            <p style="font-size: 0.9rem; opacity: 0.8;">
                {t("home.history_desc")}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with c_res3:
        st.markdown(f"""
        <div style="background-color: var(--secondary-background-color); padding: 20px; border-radius: 10px; border: 1px solid rgba(128, 128, 128, 0.2); height: 100%;">
            <h3 style="color: #4CAF50;">{t("home.multilang_title")}</h3>
            <p style="font-size: 0.9rem; opacity: 0.8;">
                {t("home.multilang_desc")}
            </p>
        </div>
        """, unsafe_allow_html=True)

    # st.divider()
    
    # # Footer Minimalista
    # st.markdown("""
    # <div style="text-align: center; color: #555; font-size: 0.8rem; margin-top: 30px;">
    #     Use a barra lateral para navegar • v0.4
    # </div>
    # """, unsafe_allow_html=True)
