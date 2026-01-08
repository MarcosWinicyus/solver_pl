import streamlit as st
import pandas as pd
import numpy as np # Adicionado para tratar tipos do numpy na formatação

from .helpers import _store_problem, _load_problem, number_emojis
from core.branch_bound_solver import BranchBoundSolver


def bab_ui():
    st.markdown("<h1 style='text-align: center;'>🌳 Branch & Bound</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Resolução de Problemas de Programação Linear Inteira</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Carregar estado anterior se existir
    saved = st.session_state.get("problem", {})
    saved_c, saved_A, saved_b = saved.get("c", []), saved.get("A", []), saved.get("b", [])
    saved_int = saved.get("int_vars", [])

    # Layout de entrada similar ao Simplex
    col_counts = st.columns(3)
    with col_counts[0]:
        n_vars = st.number_input("🔢 **Número de Variáveis**", 2, 10, max(len(saved_c), 2), help="Quantidade de variáveis de decisão")
    with col_counts[1]:
        n_cons = st.number_input("📏 **Número de Restrições**", 1, 10, max(len(saved_A), 1), help="Quantidade de restrições do problema")
        
    with col_counts[2]:
        maximize = st.selectbox(
            "🎯 **Objetivo**", 
            ["Maximização", "Minimização"], 
            index=0 if saved.get("maximize", True) else 1
        )
        is_max = (maximize == "Maximização")

    # Função objetivo
    label_obj = "Função Objetivo (Maximização)" if is_max else "Função Objetivo (Minimização)"
    st.markdown(f"#### 📝 **{label_obj}**", help="Defina os coeficientes da função objetivo")
    
    obj_cols = st.columns(n_vars)
    c = []
    for i in range(n_vars):
        default = saved_c[i] if i < len(saved_c) else 1.0
        with obj_cols[i]:
            c.append(st.number_input(f"**x{i+1}**", value=default, key=f"bb_c_{i}", help=f"Coeficiente da variável x{i+1}"))

    # Seleção de variáveis inteiras
    st.markdown("### 🔢 **Variáveis Inteiras**", help="Marque quais variáveis devem ter valores inteiros")
    
    int_cols = st.columns(n_vars)
    int_vars = []
    # Se não houver estado salvo, todas as variáveis vêm marcadas como inteiras por padrão
    all_indices = list(range(n_vars))
    default_int_vars = saved_int if "int_vars" in saved else all_indices
    
    for i in range(n_vars):
        with int_cols[i]:
            is_int = st.checkbox(f"**x{i+1}** é inteira", value=(i in default_int_vars), key=f"int_{i}")
            if is_int:
                int_vars.append(i)

    # Restrições
    # Restrições
    with st.expander("📋 **Restrições**", expanded=True):
        
        A, b = [], []
        senses = []
        for r in range(n_cons):
            st.markdown(f"**Restrição  - {number_emojis[r+1]}:**")
            cols = st.columns(n_vars + 2)
            row = []
            
            for i in range(n_vars):
                default = saved_A[r][i] if r < len(saved_A) and i < len(saved_A[r]) else 1.0
                with cols[i]:
                    row.append(st.number_input(f"**x{i+1}**", key=f"bb_a_{r}_{i}", value=default, help=f"Coeficiente de x{i+1}"))
            
            with cols[n_vars]:
                sense = st.selectbox("**Tipo**", ["≤", "=", "≥"], index=0, key=f"bb_sense_{r}")
                
            with cols[n_vars+1]:
                default_rhs = saved_b[r] if r < len(saved_b) else 1.0
                rhs = st.number_input("**Valor**", key=f"bb_b_{r}", value=default_rhs, help=f"Valor do lado direito")
            
            A.append(row)
            b.append(rhs)
            senses.append(sense)

    # Seleção de variáveis inteiras


    # Botão resolver
    
    # Controles de Execução (Estratégia, Modo e Botão na mesma linha)
    
    col_strat, col_mode, col_btn = st.columns([3, 2, 2], gap="medium")
    
    with col_strat:
        strategy_options = {
            "Busca em Largura (BFS)": "BFS",
            "Busca em Profundidade (DFS)": "DFS",
            "Melhor Limitante (BestBound)": "BestBound"
        }
        
        selected_strategy_label = st.selectbox(
            "🔍 **Estratégia de Busca**",
            list(strategy_options.keys()),
            index=0,
            help="Escolha como o algoritmo explora a árvore.\n\nBFS: Nível a nível.\nDFS: Profundidade primeiro.\nBestBound: Maior Z primeiro."
        )
        selected_strategy = strategy_options[selected_strategy_label]

    with col_mode:
        # Espaçamento para alinhar com o input
        st.write("")
        st.write("")
        step_by_step = st.checkbox("👣 **Passo a Passo**", value=False, help="Executar nó a nó.")

    with col_btn:
        # Espaçamento para alinhar com o input
        st.write("")
        st.write("")
        solve_clicked = st.button("🚀 **Iniciar**", type="primary", use_container_width=True)

    # Botão de Próximo Passo - Será renderizado no cabeçalho da árvore
    run_next_step = False # Flag para executar lógica


    if solve_clicked:
        try:
            with st.spinner("🔄 Inicializando problema..." if step_by_step else "🔄 Resolvendo problema inteiro..."):
                # Converter restrições para formato Ax <= b
                A_conv, b_conv = [], []
                for row, rhs, sn in zip(A, b, senses):
                    if sn == "≤":
                        A_conv.append(row)
                        b_conv.append(rhs)
                    elif sn == "≥":
                        A_conv.append([-x for x in row])
                        b_conv.append(-rhs)
                    else:  # igualdade
                        A_conv.append(row)
                        b_conv.append(rhs)
                        A_conv.append([-x for x in row])
                        b_conv.append(-rhs)

                # Ajustar função objetivo para Minimização se necessário
                final_c = list(c)
                if not is_max:
                    final_c = [-x for x in final_c]

                solver = BranchBoundSolver()
                
                if step_by_step:
                    solver.initialize(final_c, A_conv, b_conv, integer_vars=int_vars, strategy=selected_strategy)
                    st.session_state["bb_solver"] = solver
                    st.rerun() # Força atualização para mostrar o botão de próximo passo imediatamente
                else:
                    # Modo normal (completo)
                    solver.solve(final_c, A_conv, b_conv, integer_vars=int_vars, strategy=selected_strategy)
                    st.session_state["bb_solver"] = solver # Salva para exibir resultados abaixo
                    
        except Exception as e:
            st.error(f"❌ **Erro durante a resolução:** {str(e)}")
            st.exception(e)

    # Lógica de execução do próximo passo (verificação via chave ou botão renderizado posteriormente)
    # Como o botão será renderizado depois, precisamos checar se foi clicado no rerun anterior ou capturar aqui?
    # Streamlit buttons return True on the script run immediately following the click.
    # We will check st.session_state for a specific key if we use a keyed button later,
    # OR we need to render the button HERE if we want to capture 'next_step_clicked' easily without flow issues.
    # BUT user wants button next to header.
    # Allow rendering button later, but we need to check its state.
    # Actually, standard Streamlit flow: Render -> Click -> Rerun -> Check.
    # So we can define the button later.
    
    pass

    # Exibição dos Resultados (sempre que houver um solver no estado)
    if "bb_solver" in st.session_state:
        solver = st.session_state["bb_solver"]
        
        # Resultados Parciais ou Finais
        if solver.nodes: # Só mostrar se já tiver algum nó
            if solver.finished and solver.best_solution is None:
                 st.error("❌ **Nenhuma solução inteira encontrada**")
                 st.info("Isso pode indicar que o problema é infactível ou que não existem soluções inteiras.")
            else:
                 # Exibir estatísticas (parciais ou finais)
                 best_val_display = f"{solver.best_value:.3f}" if solver.best_value != float("-inf") else "N/A"
                 
                 st.markdown("---") # Adicionado entre botões e números dos resultados
                 col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
                 with col_stats1: st.metric("**Melhor Z Atual/Final**", best_val_display)
                 with col_stats2: st.metric("**Nós Explorados**", len(solver.nodes))
                 with col_stats3: st.metric("**Nós na Fila**", len(solver.queue))
                 with col_stats4: 
                     integer_nodes = sum(1 for n in solver.nodes if n.get("integer_feasible", False))
                     st.metric("**Soluções Inteiras**", integer_nodes)

            # Cabeçalho da Árvore + Botão Próximo Passo
            # st.markdown("---") # Removido a pedido do usuário
            col_tree_header, col_tree_btn = st.columns([0.8, 0.2])
            
            with col_tree_header:
                 st.markdown("### 🌳 **Árvore de Branch & Bound**")
            
            with col_tree_btn:
                 # Se passo a passo ativo e não terminou
                 if step_by_step and not solver.finished:
                      # Alinhar à direita para ficar próximo ao header mas oposto
                      if st.button("⏭️ **Próximo Passo**", key="btn_next_step", type="secondary", use_container_width=True):
                          run_next_step = True
            
            # Executar lógica do próximo passo se clicado
            if run_next_step:
                 solver.step()
                 st.rerun() # Rerun para atualizar grafo e estatísticas

            # Renderizar Grafo
            _render_branch_bound_tree(solver)
            
            # Exibir logs, solução e legenda ABAIXO do grafo em duas colunas
            st.markdown("---")
            col_results, col_legend = st.columns([0.65, 0.35], gap="large")

            with col_results:
                # Logs Primeiro (Top-Left)
                if solver.steps:
                    with st.expander("📝 **Log de Passos**", expanded=True):
                        for i, step in enumerate(solver.steps):
                             st.write(f"**{i+1}.** {step}")

                # Melhor Solução Inteira (Bottom-Left)
                if solver.best_solution is not None:
                    st.markdown("### 📊 **Melhor Solução Inteira**")
                    cols_per_row = min(3, n_vars) # Reduzido para caber na coluna
                    rows_needed = (n_vars + cols_per_row - 1) // cols_per_row
                    solution = solver.best_solution[:n_vars]
                    for row in range(rows_needed):
                        var_cols = st.columns(cols_per_row)
                        for col_idx in range(cols_per_row):
                            var_idx = row * cols_per_row + col_idx
                            if var_idx < n_vars:
                                with var_cols[col_idx]:
                                    val = solution[var_idx]
                                    if abs(val - round(val)) < 1e-6: val_fmt = f"{int(round(val))}"
                                    else: val_fmt = f"{val:.3f}"
                                    st.success(f"**x{var_idx+1} = {val_fmt}**")
            
            with col_legend:
                st.markdown("### 🏷️ **Legenda**")
                st.info("ℹ️ Clique em um nó para ver detalhes.")
                st.markdown("""
                - 🟢 **Verde (Ótima)**: Melhor solução inteira.
                - 🟣 **Roxo (Inteira)**: Solução inteira viável (sub-ótima).
                - 🔴 **Vermelho (Infactível)**: Sem solução.
                - ⚪ **Cinza (Podado)**: Limite pior que o incumbente.
                - 🔵 **Azul (Relaxação)**: Solução fracionária.
                - 🟡 **Amarelo (Raiz)**: Nó inicial.
                """)

        elif solver.finished: # Sem nós mas finalizado (Erro na Raiz)
             st.error("❌ **Não foi possível iniciar o Branch & Bound**")
             st.warning("""
             O problema relaxado (na raiz) não pôde ser resolvido. Possíveis causas:
             - **Infactibilidade**: As restrições são conflitantes.
             - **Ilimitado**: A função objetivo tende ao infinito (verifique se escolheu Max/Min corretamente).
             """)
             if solver.steps:
                 st.info(f"Log do Solver: {solver.steps[-1]}")


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
                branch_label = node_info.get("branch_reason", "BRANCH")
                edges_data.append({
                    "data": {
                        "id": f'edge_{node_info["parent"]}_{node_id}',
                        "label": branch_label,
                        "source": str(node_info["parent"]),
                        "target": node_id,
                        "Solução": solution_str  # Adds solution info to the edge sidebar
                    }
                })
        
        node_styles = [
            NodeStyle(status["label"], status["color"], "caption", status["icon"])
            for status in status_map.values()
        ]

        # Gerar estilos de aresta dinamicamente para cada label única
        unique_edge_labels = set(e["data"]["label"] for e in edges_data)
        edge_styles = [
            EdgeStyle(label, color="#888888", directed=True, labeled=True)
            for label in unique_edge_labels
        ]

        # Ajuste de Layout para evitar sobreposição
        layout_config = {
            "name": "dagre",
            "rankDir": "TB",      # Direção: Top-to-Bottom
            "rankSep": 50,        # Ajustado para equilíbrio
            "nodeSep": 40,        # Ajustado para equilíbrio
            "spacingFactor": 1.2,
        }

        st_link_analysis(
            elements={"nodes": nodes_data, "edges": edges_data},
            layout=layout_config,
            node_styles=node_styles,
            edge_styles=edge_styles,
            key=f"bb_tree_viz_{len(solver.nodes)}" # Chave dinâmica para forçar re-renderização do layout a cada passo
        )
        



    except Exception as e:
        st.error(f"❌ Ocorreu um erro inesperado ao tentar renderizar a árvore: {str(e)}")
        st.exception(e)