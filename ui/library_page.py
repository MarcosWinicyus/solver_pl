import streamlit as st
from typing import Dict, List, Any

def library_page():
    st.header("📚 Biblioteca de Problemas Clássicos")
    st.markdown("""
    Explore problemas clássicos da Pesquisa Operacional. 
    Selecione um problema para carregar seus dados automaticamente no solver apropriado.
    """)
    st.divider()

    # Definição dos Problemas
    problems = [
        {
            "title": "🏭 Mix de Produção (Manufatura)",
            "category": "Programação Linear (Simplex)",
            "description": """
            Uma fábrica produz dois produtos: **P1** e **P2**.
            
            **Dados:**
            - **Lucro P1:** $100/unidade
            - **Lucro P2:** $150/unidade
            
            **Restrições de Recursos:**
            1. **Tempo de Máquina:** P1 gasta 2h, P2 gasta 3h. Disponível: 120h.
            2. **Matéria-prima:** P1 gasta 1kg, P2 gasta 0.5kg. Disponível: 50kg.
            
            **Objetivo:** Maximizar o lucro total.
            """,
            "target_page": "📐 Método Simplex",
            "data": {
                "c": [100.0, 150.0],
                "A": [[2.0, 3.0], [1.0, 0.5]],
                "b": [120.0, 50.0],
                "maximize": True,
                "int_vars": []
            }
        },
        {
            "title": "🥗 Problema da Dieta (Nutrição)",
            "category": "Programação Linear (Simplex)",
            "description": """
            Planejar uma dieta com dois alimentos (**A** e **B**) para atingir requisitos nutricionais com o **menor custo**.
            
            **Dados:**
            - **Custo A:** $2.00
            - **Custo B:** $3.00
            
            **Requisitos:**
            1. **Proteína:** A tem 4g, B tem 2g. Mínimo necessário: 20g.
            2. **Vitamina:** A tem 2mg, B tem 5mg. Mínimo necessário: 30mg.
            
            **Objetivo:** Minimizar o custo total.
            """,
            "target_page": "📐 Método Simplex",
            "data": {
                "c": [2.0, 3.0],
                "A": [[-4.0, -2.0], [-2.0, -5.0]], # Convertido para <= (multiplicado por -1)
                "b": [-20.0, -30.0],
                "maximize": False, # Minimizar
                "int_vars": []
            }
        },
        {
            "title": "🎒 Problema da Mochila (Knapsack)",
            "category": "Programação Inteira (Branch & Bound)",
            "description": """
            Você tem uma mochila com capacidade de **15kg** e deve escolher quais itens levar para maximizar o valor, sem exceder o peso.
            
            **Itens Disponíveis:**
            1. **Item 1:** Valor $10, Peso 2kg
            2. **Item 2:** Valor $15, Peso 4kg
            3. **Item 3:** Valor $20, Peso 6kg
            4. **Item 4:** Valor $25, Peso 9kg
            
            **Objetivo:** Maximizar valor total (variáveis binárias/inteiras).
            """,
            "target_page": "🌳 Branch & Bound",
            "data": {
                "c": [10.0, 15.0, 20.0, 25.0],
                "A": [[2.0, 4.0, 6.0, 9.0]],
                "b": [15.0],
                "maximize": True,
                "int_vars": [0, 1, 2, 3] # Todos inteiros (0 ou 1 neste caso, mas B&B genérico trata como inteiros)
            }
        },
        {
            "title": "🪵 Corte de Estoque (Simplificado)",
            "category": "Programação Inteira (Branch & Bound)",
            "description": """
            Uma marcenaria vende rolos de tecido de 10m. Um cliente pede:
            - 3 pedaços de 3m
            - 2 pedaços de 4m
            
            (Exemplo simplificado focado em maximizar o uso de um único rolo ou lucro associado a padrões de corte).
            
            **Neste exemplo didático:**
            Maximizar o lucro escolhendo quantos produtos de cada tipo produzir com recursos limitados e indivisíveis.
            
            **Objetivo:** Maximizar Z = 5x1 + 8x2
            Sujeito a:
            x1 + x2 <= 6
            5x1 + 9x2 <= 45
            x1, x2 inteiros >= 0
            """,
            "target_page": "🌳 Branch & Bound",
            "data": {
                "c": [5.0, 8.0],
                "A": [[1.0, 1.0], [5.0, 9.0]],
                "b": [6.0, 45.0],
                "maximize": True,
                "int_vars": [0, 1]
            }
        }
    ]

    # Renderização dos Cards
    for i, prob in enumerate(problems):
        with st.container():
            st.markdown(f"### {prob['title']}")
            st.caption(f"📌 {prob['category']}")
            
            col_desc, col_action = st.columns([3, 1])
            
            with col_desc:
                st.markdown(prob['description'])
            
            with col_action:
                st.markdown("<br>", unsafe_allow_html=True) # Espaçamento
                if st.button(f"Carregar Problema", key=f"btn_prob_{i}", type="primary"):
                    load_problem_and_redirect(prob)
            
            st.divider()

def load_problem_and_redirect(problem: Dict[str, Any]):
    """Carrega os dados na sessão e redireciona."""
    
    # Salvar dados no formato esperado pelas páginas
    st.session_state["problem"] = problem["data"]
    
    # Agendar redirecionamento para a próxima execução (evita erro de widget instanciado)
    st.session_state["pending_redirect"] = problem["target_page"]
    
    st.toast(f"Problema '{problem['title']}' carregado! Redirecionando...", icon="✅")
    st.rerun()
