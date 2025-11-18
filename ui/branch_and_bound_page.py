import streamlit as st
import pandas as pd
import numpy as np # Adicionado para tratar tipos do numpy na formatação

from .helpers import _store_problem, _load_problem, number_emojis
from core.branch_bound_solver import BranchBoundSolver


def bab_ui():
    st.header("🌳 Branch & Bound", help="Resolução de Problemas de Programação Linear Inteira")

    # Carregar estado anterior se existir
    saved = st.session_state.get("problem", {})
    saved_c, saved_A, saved_b = saved.get("c", []), saved.get("A", []), saved.get("b", [])
    saved_int = saved.get("int_vars", [])

    # Layout de entrada similar ao Simplex
    col_counts = st.columns(2)
    with col_counts[0]:
        n_vars = st.number_input("🔢 **Número de Variáveis**", 2, 4, max(len(saved_c), 2), help="Quantidade de variáveis de decisão")
    with col_counts[1]:
        n_cons = st.number_input("📏 **Número de Restrições**", 1, 4, max(len(saved_A), 1), help="Quantidade de restrições do problema")

    # Função objetivo
    st.markdown("#### 📝 **Função Objetivo (Maximização)**", help="Defina os coeficientes da função que será maximizada")
    
    obj_cols = st.columns(n_vars)
    c = []
    for i in range(n_vars):
        default = saved_c[i] if i < len(saved_c) else 1.0
        with obj_cols[i]:
            c.append(st.number_input(f"**x{i+1}**", value=default, key=f"bb_c_{i}", help=f"Coeficiente da variável x{i+1}"))

    # Restrições
    st.markdown("#### 📋 **Restrições (≤)**", help="Configure as restrições que limitam o problema")
    
    A, b = [], []
    for r in range(n_cons):
        st.markdown(f"**Restrição  - {number_emojis[r+1]}:**")
        cols = st.columns(n_vars + 1)
        row = []
        
        for i in range(n_vars):
            default = saved_A[r][i] if r < len(saved_A) and i < len(saved_A[r]) else 1.0
            with cols[i]:
                row.append(st.number_input(f"**x{i+1}**", key=f"bb_a_{r}_{i}", value=default, help=f"Coeficiente de x{i+1}"))
        
        with cols[-1]:
            default_rhs = saved_b[r] if r < len(saved_b) else 1.0
            rhs = st.number_input("**≤ Valor**", key=f"bb_b_{r}", value=default_rhs, help=f"Valor do lado direito")
        
        A.append(row)
        b.append(rhs)

    # Seleção de variáveis inteiras
    st.markdown("### 🔢 **Variáveis Inteiras**", help="Marque quais variáveis devem ter valores inteiros")
    
    int_cols = st.columns(n_vars)
    int_vars = []
    for i in range(n_vars):
        with int_cols[i]:
            is_int = st.checkbox(f"**x{i+1}** é inteira", value=(i in saved_int), key=f"int_{i}")
            if is_int:
                int_vars.append(i)

    # Botão resolver
    st.markdown("---")
    if st.button("🚀 **Resolver Branch & Bound**", type="primary"):
        try:
            with st.spinner("🔄 Resolvendo problema inteiro..."):
                solver = BranchBoundSolver()
                solver.solve(c, A, b, integer_vars=int_vars)
                
                if solver.best_solution is None:
                    st.error("❌ **Nenhuma solução inteira encontrada**")
                    st.info("Isso pode indicar que o problema é infactível ou que não existem soluções inteiras.")
                else:
                    _store_problem(c, A, b, int_vars)
                    st.session_state.setdefault("history", []).append({
                        "method": "Branch & Bound",
                        "c": c, "A": A, "b": b,
                        "z": solver.best_value,
                        "solution": solver.best_solution,
                        "integer_vars": int_vars
                    })
                    
                    st.success("🎉 **Solução Inteira Ótima Encontrada!**")
                    
                    col_result1, col_result2 = st.columns(2)
                    with col_result1:
                        st.metric("**Valor Ótimo Z***", f"{solver.best_value:.3f}")
                    
                    with col_result2:
                        st.markdown("**Valores das Variáveis:**")
                        for i, v in enumerate(solver.best_solution[:n_vars]):
                            st.write(f"• x{i+1} = {int(v) if abs(v - round(v)) < 1e-6 else v:.3f}")
                    
                    st.markdown("---")
                    st.markdown("### 📊 **Resumo do Algoritmo**")
                    
                    col_stats1, col_stats2, col_stats3 = st.columns(3)
                    with col_stats1:
                        st.metric("**Nós Explorados**", len(solver.nodes))
                    with col_stats2:
                        feasible_nodes = sum(1 for n in solver.nodes if n["feasible"])
                        st.metric("**Nós Factíveis**", feasible_nodes)
                    with col_stats3:
                        integer_nodes = sum(1 for n in solver.nodes if n.get("integer_feasible", False))
                        st.metric("**Soluções Inteiras**", integer_nodes)
                    
                    if solver.steps:
                        with st.expander("📝 **Passos do Algoritmo**", expanded=False):
                            for i, step in enumerate(solver.steps):
                                st.write(f"**{i+1}.** {step}")
                    
                    _render_branch_bound_tree(solver)
                    
        except Exception as e:
            st.error(f"❌ **Erro durante a resolução:** {str(e)}")
            st.exception(e)


def _format_solution(solution, max_vars_to_show=5):
    import json
    """Formata o array de solução para uma string de dicionário."""
    if solution is None or not isinstance(solution, (list, np.ndarray)):
        return "N/A"
    
    solution_dict = {}
    for i, val in enumerate(solution):
        if i >= max_vars_to_show:
            break
        key = f"X{i+1}"
        solution_dict[key] = f"{float(val):.2f}"

    # Converte o dicionário para uma string formatada
    items = [f"'{k}': {v}" for k, v in solution_dict.items()]
    
    if len(solution) > max_vars_to_show:
        items.append("'...': '...'")
        
    return "{" + ", ".join(items) + "}"


def _render_branch_bound_tree(solver):
    """
    Renderiza a árvore de Branch & Bound usando a biblioteca st-link-analysis.
    """
    st.markdown("---")
    st.markdown("### 🌳 **Árvore de Branch & Bound**")

    try:
        from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle

        nodes_data = []
        edges_data = []

        status_map = {
            "OPTIMAL": {"label": "Solução Ótima", "color": "#2e7d32", "icon": "verified"},
            "INTEGER": {"label": "Solução Inteira", "color": "#8e24aa", "icon": "check_circle"},
            "INFEASIBLE": {"label": "Infactível", "color": "#f44336", "icon": "lock"},
            "PRUNED": {"label": "Podado por Limite", "color": "#9e9e9e", "icon": "cancel"},
            "FRACTIONAL": {"label": "Relaxação", "color": "#2196f3", "icon": "functions"},
            "ROOT": {"label": "Raiz", "color": "#ffc107", "icon": "adjust"}
        }

        for node_info in solver.nodes:
            node_id = str(node_info["id"])
            
            status_key = "ROOT"
            if node_info['id'] == 0:
                 status_key = "ROOT"
                 # Se a raiz já for inteira e ótima
                 if node_info.get("integer_feasible") and abs(node_info["value"] - solver.best_value) < 1e-6:
                     status_key = "OPTIMAL"
            elif not node_info["feasible"]:
                status_key = "INFEASIBLE"
            elif node_info.get("integer_feasible"):
                if abs(node_info["value"] - solver.best_value) < 1e-6:
                    status_key = "OPTIMAL"
                else:
                    status_key = "INTEGER"
            elif node_info.get("pruned"):
                status_key = "PRUNED"
            else:
                status_key = "FRACTIONAL"
            
            status_details = status_map[status_key]
            
            bounds_str = ", ".join([f"x{var+1} {op} {val}" for var, (op, val) in node_info.get("bounds", {}).items()])
            
            solution_str = _format_solution(node_info.get("solution"))

            nodes_data.append({
                "data": {
                    "id": node_id,
                    "label": status_details["label"],
                    "caption": f"Z={node_info.get('value', 0):.2f}",
                    "Valor Z": f"{node_info.get('value', 0):.3f}",
                    "Status": status_details["label"],
                    "Bounds": bounds_str if bounds_str else "Nenhum",
                    "Solução": solution_str
                }
            })

            if node_info.get("parent") is not None:
                edges_data.append({
                    "data": {
                        "id": f'edge_{node_info["parent"]}_{node_id}',
                        "label": "BRANCH",
                        "source": str(node_info["parent"]),
                        "target": node_id
                    }
                })
        
        node_styles = [
            NodeStyle(status["label"], status["color"], "caption", status["icon"])
            for status in status_map.values()
        ]

        edge_styles = [
            EdgeStyle("BRANCH", color="#888888", directed=True)
        ]

        # **MELHORIA APLICADA AQUI**
        # O valor de 'rankSep' foi reduzido para diminuir o comprimento das arestas (espaçamento vertical).
        layout_config = {
            "name": "dagre",
            "rankDir": "TB",      # Direção: Top-to-Bottom
            "rankSep": 50,        # Distância vertical entre os níveis (tamanho da aresta)
            "nodeSep": 30,        # Distância horizontal entre nós
            "spacingFactor": 1.1,
        }

        st_link_analysis(
            elements={"nodes": nodes_data, "edges": edges_data},
            layout=layout_config,
            node_styles=node_styles,
            edge_styles=edge_styles,
            key="bb_tree_visualization"
        )
        
        st.markdown("""
        **Legenda:**
        - 🟢 **Verde (Ótima)**: A melhor solução inteira encontrada.
        - 🟣 **Roxo (Inteira)**: Solução inteira viável, mas não é a ótima (sub-ótima).
        - 🔴 **Vermelho (Infactível)**: O problema neste nó não tem solução.
        - ⚪ **Cinza (Podado por Limite)**: O limite superior deste nó é pior que a melhor solução inteira.
        - 🔵 **Azul (Relaxação)**: Nó com solução fracionária que foi ramificado.
        - 🟡 **Amarelo (Raiz)**: O nó inicial do problema.
        """)
        st.info("ℹ️ Clique em um nó para ver seus detalhes, como o valor de Z, os bounds aplicados e a solução da relaxação.")


    except Exception as e:
        st.error(f"❌ Ocorreu um erro inesperado ao tentar renderizar a árvore: {str(e)}")
        st.exception(e)