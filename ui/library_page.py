import streamlit as st
from typing import Dict, List, Any

def library_page():
    st.markdown("<h1 style='text-align: center;'>📚 Biblioteca de Problemas Clássicos</h1>", unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align: center; color: #666;'>
    Explore problemas clássicos da Pesquisa Operacional. <br>
    Selecione um problema para carregar seus dados automaticamente no solver apropriado.
    </p>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

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
        },
        {
            "title": "💎 Poliedro Distorcido (3D Visual)",
            "category": "Programação Linear (Simplex)",
            "description": """
            Problema projetado para gerar uma **região factível tridimensional complexa**.
            Ideal para testar a visualização 3D, rotação e identificação de vértices.
            
            **Restrições Geométricas:**
            Múltiplos cortes em diferentes ângulos para formar um poliedro irregular (similar a um cristal lapidado).
            
            **Objetivo:** Maximizar soma das variáveis.
            """,
            "target_page": "📐 Método Simplex",
            "data": {
                "c": [1.0, 1.0, 1.0],
                "A": [
                    [1.0, 1.0, 1.0],  # Teto inclinado
                    [1.0, 0.0, 0.0],  # Parede X
                    [0.0, 1.0, 0.0],  # Parede Y
                    [0.0, 0.0, 1.0],  # Parede Z
                    [1.0, 2.0, 0.0],  # Corte diagonal XY
                    [0.0, 2.0, 1.0]   # Corte diagonal YZ
                ],
                "b": [10.0, 6.0, 6.0, 6.0, 12.0, 12.0],
                "maximize": True,
                "int_vars": []
            }
        }
    ]


    # CSS para alinhar verticalmente o botão com o expander
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] {
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

    # Renderização dos Cards
    for i, prob in enumerate(problems):
        col_main, col_btn = st.columns([0.85, 0.15])
        
        with col_main:
            with st.expander(f"{prob['title']} — {prob['category']}"):
                
                c_text, c_math = st.columns(2)
                
                with c_text:
                    st.markdown("**Descrição:**")
                    st.markdown(prob['description'])
                
                with c_math:
                    st.markdown("**Modelagem Matemática:**")
                    
                    # Dados do problema
                    d = prob['data']
                    c = d['c']
                    A = d['A']
                    b = d['b']
                    is_max = d['maximize']
                    
                    # Construção do LaTeX
                    # Função Objetivo
                    obj_str = " + ".join([f"{val}x_{j+1}" for j, val in enumerate(c)])
                    st.latex(f"{'Max' if is_max else 'Min'} \ Z = {obj_str}")
                    
                    # Restrições
                    st.markdown("Sujeito a:")
                    for r_idx, row in enumerate(A):
                        lhs = " + ".join([f"{val}x_{j+1}" for j, val in enumerate(row)])
                        rhs = b[r_idx]
                        st.latex(f"{lhs} \le {rhs}")
                    
                    st.latex("x_j \ge 0")

        with col_btn:
            if st.button("🚀 Carregar", key=f"btn_prob_{i}", help=f"Resolver: {prob['title']}"):
                load_problem_and_redirect(prob)


def load_problem_and_redirect(problem: Dict[str, Any]):
    """Carrega os dados na sessão e redireciona."""
    
    # Salvar dados no formato esperado pelas páginas
    st.session_state["problem"] = problem["data"]
    
    # Agendar redirecionamento para a próxima execução (evita erro de widget instanciado)
    st.session_state["pending_redirect"] = problem["target_page"]
    
    st.toast(f"Problema '{problem['title']}' carregado! Redirecionando...", icon="✅")
    st.rerun()
