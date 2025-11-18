import streamlit as st

def home_page():
    """
    Página inicial do Sistema de Otimização Visual.
    Apresenta o projeto, seus objetivos e os módulos disponíveis.
    """
    
    # Título e Subtítulo com estilo
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">📊 Sistema de Otimização Visual</h1>
        <p style="font-size: 1.2rem; color: #666;">
            Uma plataforma interativa para explorar, resolver e aprender sobre<br>
            <b>Programação Linear</b> e <b>Otimização Inteira</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Seção de Introdução / Proposta
    st.markdown("### 🎯 O que é este projeto?")
    st.markdown("""
    Este sistema foi desenvolvido com um propósito educacional claro: **desmistificar a Pesquisa Operacional**.
    
    Ao invés de apenas entregar a resposta final, nossa ferramenta foca em mostrar o **"como"** e o **"porquê"**. 
    Através de visualizações interativas e passos detalhados, você pode acompanhar o funcionamento interno 
    de algoritmos clássicos de otimização.
    """)

    st.markdown("---")

    # Seção dos Módulos (Algoritmos)
    st.markdown("### 🚀 Módulos Disponíveis")
    st.markdown("Explore nossos solvers especializados:")

    col1, col2 = st.columns(2)

    with col1:
        st.info("### 📐 Método Simplex")
        st.markdown("""
        O clássico algoritmo para resolução de Problemas de Programação Linear (PPL).
        
        **Destaques:**
        - ✨ **Passo a Passo:** Visualize cada iteração do Tableau.
        - 🔍 **Análise Detalhada:** Identifique variáveis básicas e não-básicas.
        - 📈 **Casos Especiais:** Detecção de múltiplas soluções, soluções ilimitadas e inviabilidade.
        - 📝 **Entrada Flexível:** Digite sua função objetivo e restrições facilmente.
        """)
        # Botão simulado (apenas visual, a navegação é pela sidebar)
        # st.button("Ir para Simplex", key="btn_simplex", disabled=True) 

    with col2:
        st.success("### 🌳 Branch & Bound")
        st.markdown("""
        A técnica definitiva para Programação Linear Inteira (PLI).
        
        **Destaques:**
        - 🌲 **Visualização de Árvore:** Veja a árvore de decisão crescer em tempo real.
        - ✂️ **Poda Inteligente:** Entenda quando e por que um ramo é podado.
        - 🔢 **Soluções Inteiras:** Garanta que suas variáveis de decisão sejam números inteiros.
        - 📊 **Integração:** Utiliza o Simplex para resolver os relaxamentos lineares.
        """)
        # st.button("Ir para Branch & Bound", key="btn_bab", disabled=True)

    st.markdown("---")

    # Seção de Features / Recursos Adicionais
    st.markdown("### ✨ Recursos Adicionais")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        st.markdown("#### 👁️ Visualização Gráfica")
        st.caption("Gráficos interativos que ajudam a entender a região viável e a função objetivo (para problemas de 2 variáveis).")
        
    with col_f2:
        st.markdown("#### 📝 Histórico de Sessão")
        st.caption("Mantenha o controle do seu aprendizado. Revise todos os problemas que você resolveu durante sua sessão atual.")
        
    with col_f3:
        st.markdown("#### 🎓 Foco Didático")
        st.caption("Explicações claras e feedback visual para auxiliar no entendimento dos conceitos teóricos.")

    st.divider()
    
    # Call to Action simples
    st.markdown("""
    <div style="text-align: center; color: #888;">
        <small>👈 Utilize o menu lateral para navegar entre os módulos e começar a resolver seus problemas!</small>
    </div>
    """, unsafe_allow_html=True)
