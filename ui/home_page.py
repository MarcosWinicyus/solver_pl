
import streamlit as st

def home_page():
    # Hero Section Minimalista
    st.markdown("""
    <div style="text-align: center; margin-top: 0px; margin-bottom: 50px;">
        <h1 style="font-size: 3.5rem; background: -webkit-linear-gradient(45deg, #00CCFF, #3366ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Solver PL
        </h1>
        <p style="font-size: 1.25rem; color: #888; font-weight: 300;">
            Plataforma Didática de Otimização Linear e Inteira
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- Linha 1: Solvers (Principais) ---
    c_solv1, c_solv2 = st.columns(2)
    
    with c_solv1:
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 20px; border-radius: 10px; border: 1px solid #333; height: 100%;">
            <h3 style="color: #00CCFF;">📐 Simplex 2.0</h3>
            <p style="color: #AAA; font-size: 0.9rem;">
                Resolução passo a passo com <b>visualização 3D/2D</b> interativa, análise de tableau e múltiplas iterações.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with c_solv2:
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 20px; border-radius: 10px; border: 1px solid #333; height: 100%;">
            <h3 style="color: #28a745;">🌳 Branch & Bound</h3>
            <p style="color: #AAA; font-size: 0.9rem;">
                Algoritmo para problemas inteiros (PLI) com árvore de decisão interativa e estratégias de busca em profundidade/largura.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    
    # --- Linha 2: Ferramentas (Novidades) ---
    c_tool1, c_tool2, c_tool3 = st.columns(3)
    
    with c_tool1:
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 20px; border-radius: 10px; border: 1px solid #333; height: 100%;">
            <h3 style="color: #ffc107;">🔄 Dualidade</h3>
            <p style="color: #AAA; font-size: 0.9rem;">
                Converta Problemas Primais em Duais instantaneamente e alterne entre os modos de resolução.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c_tool2:
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 20px; border-radius: 10px; border: 1px solid #333; height: 100%;">
            <h3 style="color: #e91e63;">📊 Sensibilidade</h3>
            <p style="color: #AAA; font-size: 0.9rem;">
                Analise preços sombra, custos reduzidos e intervalos de estabilidade para os parâmetros da função objetivo e restrições.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c_tool3:
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 20px; border-radius: 10px; border: 1px solid #333; height: 100%;">
            <h3 style="color: #00bcd4;">📝 Forma Padrão</h3>
            <p style="color: #AAA; font-size: 0.9rem;">
                Converta qualquer PL para o formato canônico com variáveis de folga/excesso e comparação lado a lado.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")

    # --- Linha 3: Recursos (Biblioteca e Histórico) ---
    c_res1, c_res2 = st.columns(2)
    
    with c_res1:
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 20px; border-radius: 10px; border: 1px solid #333; height: 100%;">
            <h3 style="color: #9b59b6;">📚 Biblioteca</h3>
            <p style="color: #AAA; font-size: 0.9rem;">
                 Acervo de problemas clássicos (Dieta, Mochila, Mix de Produção) prontos para carregar e testar.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c_res2:
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 20px; border-radius: 10px; border: 1px solid #333; height: 100%;">
            <h3 style="color: #e67e22;">🕑 Histórico</h3>
            <p style="color: #AAA; font-size: 0.9rem;">
                Suas sessões são salvas automaticamente. Recupere, exporte ou revise problemas anteriores.
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
