from typing import List

import streamlit as st
import numpy as np
import pandas as pd

from core.branch_bound_solver import BranchBoundSolver
from core.simplex_solver import SimplexSolver
from .plots import feasible_region_2d
from .tableau_display import (
    show_tableau, 
    show_tableau_with_basis_info, 
    create_iteration_summary,
    show_final_solution,
    show_optimization_summary,
    extract_basis_variables
)


# ------------------------------------------------------------------ helpers

def _store_problem(c, A, b, int_vars=None):
    st.session_state["problem"] = {"c": c, "A": A, "b": b, "int_vars": int_vars or []}


def _load_problem(default_nvars=2, default_ncons=2):
    p = st.session_state.get("problem")
    if not p:
        return [], [], [], default_nvars, default_ncons
    return p["c"], p["A"], p["b"], len(p["c"]), len(p["A"])


# ------------------------------------------------------------------ SIMPLEX PAGE

def simplex_page():
    st.header("📐 Método Simplex")

    # carregamento de estado anterior (se existir)
    saved = st.session_state.get("problem", {})
    sv_c, sv_A, sv_b = saved.get("c", []), saved.get("A", []), saved.get("b", [])

    # ---------- linha com #variáveis e #restrições (lado a lado) ----------
    col_counts = st.columns(2)
    with col_counts[0]:
        n_vars = st.number_input("🔢 **Número de Variáveis**", 2, 5, max(len(sv_c), 2), help="Quantidade de variáveis de decisão")
    with col_counts[1]:
        n_cons = st.number_input("📏 **Número de Restrições**", 1, 5, max(len(sv_A), 1), help="Quantidade de restrições do problema")

    # seletor tipo (selectbox mais compacto)
    st.markdown("### 🎯 **Tipo de Problema**")
    maximize = st.selectbox("", ["🔺 Maximizar", "🔻 Minimizar"], label_visibility="collapsed") == "🔺 Maximizar"

    # ---------- função objetivo (inputs lado a lado) ------------------
    st.markdown("### 📝 **Coeficientes da Função Objetivo**")
    st.markdown("*Defina os coeficientes da função Z que será otimizada*")
    
    obj_cols = st.columns(n_vars)
    c: List[float] = []
    for i in range(n_vars):
        default = sv_c[i] if i < len(sv_c) else 1.0
        with obj_cols[i]:
            c.append(st.number_input(f"**x{i+1}**", value=default, key=f"c_{i}", help=f"Coeficiente da variável x{i+1}"))

    # ---------- restrições -------------------------------------------
    st.markdown("### 📋 **Restrições do Problema**")
    st.markdown("*Configure as restrições que limitam o problema*")
    
    A: List[List[float]] = []
    b: List[float] = []
    senses: List[str] = []
    
    for r in range(n_cons):
        st.markdown(f"**Restrição {r+1}:**")
        cols = st.columns(n_vars + 2)  # variáveis + seletor + RHS
        row = []
        
        # Inputs dos coeficientes das variáveis
        for i in range(n_vars):
            default = sv_A[r][i] if r < len(sv_A) and i < len(sv_A[r]) else 1.0
            with cols[i]:
                row.append(st.number_input(
                    f"**x{i+1}**", 
                    value=default, 
                    key=f"a_{r}_{i}",
                    help=f"Coeficiente de x{i+1} na restrição {r+1}"
                ))
        
        # Seletor do tipo de restrição
        with cols[n_vars]:
            sense = st.selectbox(
                "**Tipo**", 
                ["≤", "=", "≥"], 
                index=0, 
                key=f"sense_{r}",
                help="Selecione o tipo da restrição"
            )
        
        # Valor do lado direito (RHS)
        with cols[n_vars + 1]:
            rhs_default = sv_b[r] if r < len(sv_b) else 1.0
            rhs = st.number_input(
                "**Valor**", 
                value=rhs_default, 
                key=f"rhs_{r}",
                help=f"Valor do lado direito da restrição {r+1}"
            )
        
        A.append(row)
        b.append(rhs)
        senses.append(sense)

    # -------- botão resolver ----------------------------------------
    st.markdown("---")
    if st.button("🚀 **Resolver Problema**", type="primary", use_container_width=True):
        # Pré-processar sentidos: converter tudo para ≤
        A_conv, b_conv = [], []
        for row, rhs, sn in zip(A, b, senses):
            if sn == "≤":
                A_conv.append(row)
                b_conv.append(rhs)
            elif sn == "≥":
                A_conv.append([-x for x in row])
                b_conv.append(-rhs)
            else:  # igualdade → duas
                A_conv.append(row)
                b_conv.append(rhs)
                A_conv.append([-x for x in row])
                b_conv.append(-rhs)
        
        try:
            with st.spinner("🔄 Resolvendo problema..."):
                solver = SimplexSolver()
                solver.solve(c, A_conv, b_conv, maximize=maximize)
                
                if solver.unbounded:
                    st.error("⚠️ **Problema Ilimitado** - A função objetivo pode crescer infinitamente")
                    return
                    
                if not solver.optimal:
                    st.error("❌ **Não foi possível encontrar solução ótima**")
                    return
                
                sol, z = solver.get_solution()
                _store_problem(c, A, b)  # salvamos versões originais para load
                
                # Adicionar ao histórico
                st.session_state.setdefault("history", []).append({
                    "method": "Simplex",
                    "c": c,
                    "A": A,
                    "b": b,
                    "z": z,
                    "solution": sol,
                })

                # ----- Mostrar resultado final primeiro -------------------------
                st.success(f"🎉 **Solução Ótima Encontrada!**")
                
                # Usar a nova função para mostrar a solução
                show_final_solution(
                    solution=sol[:n_vars], 
                    objective_value=z, 
                    basis_info=solver.get_basis_info(),
                    maximize=maximize
                )
                
                # Mostrar resumo da otimização
                show_optimization_summary(
                    method="Simplex Primal",
                    iterations=len(solver.steps) - 1,  # -1 porque inclui o tableau inicial
                    status="Optimal"
                )

                # ----- Mostrar iterações do algoritmo ------------------------
                st.markdown("---")
                st.markdown("### 📊 **Iterações do Algoritmo Simplex**")
                
                for idx, (tbl, step, desc, piv) in enumerate(
                    zip(solver.tableaux, solver.steps, solver.decisions, solver.pivots)
                ):
                    # Expandir o primeiro passo (tableau inicial) e solução final por padrão
                    is_initial = idx == 0
                    is_final = "Ótima" in step
                    
                    with st.expander(f"**{step}**", expanded=(is_initial or is_final)):
                        # Descrição detalhada com markdown formatado
                        st.markdown(desc)
                        
                        st.markdown("---")
                        
                        # Extrair informações da base para este tableau
                        if hasattr(solver, '_current_basis') and idx > 0:
                            # Para iterações após a inicial, obter base atualizada
                            basis_info = extract_basis_variables(tbl, solver._current_basis, len(c))
                        else:
                            # Para o tableau inicial, usar base de folgas
                            basis_info = [(f"s{i+1}", tbl[i+1, -1]) for i in range(tbl.shape[0]-1)]
                        
                        # Mostrar tableau com índices corretos das variáveis básicas
                        show_tableau_with_basis_info(tbl, basis_info, pivot=piv)
                        
                        # Para iterações de pivot, mostrar informações adicionais
                        if piv != (-1, -1) and "Iteração" in step and idx > 0:
                            pr, pc = piv
                            
                            st.markdown("---")
                            st.markdown("#### 🔄 **Resumo da Operação de Pivoteamento**")
                            
                            # Informações em colunas
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.success(f"**🟢 Entra na Base:**\n\nx{pc+1}")
                            
                            with col2:
                                st.warning(f"**⚡ Elemento Pivot:**\n\n{tbl[pr, pc]:.3f}")
                            
                            with col3:
                                st.error(f"**🔴 Sai da Base:**\n\nLinha {pr}")
                            
                            # Informações técnicas adicionais
                            st.markdown("#### 📋 **Detalhes Técnicos**")
                            
                            details_col1, details_col2 = st.columns(2)
                            
                            with details_col1:
                                st.markdown(f"""
                                **Posição do Pivot:**
                                - Linha: {pr}
                                - Coluna: {pc+1}
                                - Valor: {tbl[pr, pc]:.6f}
                                """)
                            
                            with details_col2:
                                st.markdown(f"""
                                **Operações Realizadas:**
                                - ✅ Linha {pr} ÷ {tbl[pr, pc]:.3f}
                                - ✅ Eliminar coluna {pc+1}
                                - ✅ Atualizar base
                                """)
                        
                        # Mostrar informações da base atual (apenas para tableaux após iterações)
                        if idx > 0:  # Não mostrar para o tableau inicial
                            st.markdown("---")
                            st.markdown("#### 📊 **Análise da Base Atual**")
                            
                            # Identificar e categorizar variáveis
                            basic_vars = [info for info in basis_info if abs(info[1]) > 1e-6]
                            zero_vars = [info for info in basis_info if abs(info[1]) <= 1e-6]
                            
                            if basic_vars:
                                st.markdown("**💡 Interpretação:**")
                                
                                # Categorizar por tipo de variável
                                decision_vars = [(name, val) for name, val in basic_vars if name.startswith('x')]
                                slack_vars = [(name, val) for name, val in basic_vars if name.startswith('s')]
                                
                                if decision_vars:
                                    decision_text = ", ".join([f"{name} = {val:.3f}" for name, val in decision_vars])
                                    st.markdown(f"• **Variáveis de decisão ativas:** {decision_text}")
                                
                                if slack_vars:
                                    slack_text = ", ".join([f"{name} = {val:.3f}" for name, val in slack_vars])
                                    st.markdown(f"• **Folgas disponíveis:** {slack_text}")
                                
                                # Mostrar variáveis não-básicas (sempre zero)
                                all_decision_vars = [f"x{i+1}" for i in range(len(c))]
                                basic_decision_names = [name for name, _ in decision_vars]
                                non_basic_decision = [var for var in all_decision_vars if var not in basic_decision_names]
                                
                                if non_basic_decision:
                                    st.markdown(f"• **Variáveis não-básicas (= 0):** {', '.join(non_basic_decision)}")

                # ----- Gráfico da região factível (apenas para 2 variáveis) ----
                if n_vars == 2:
                    st.markdown("---")
                    st.markdown("### 📈 **Visualização da Região Factível**")
                    fig = feasible_region_2d(c, A_conv, b_conv)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Gráfico disponível apenas para problemas com 2 variáveis")
                        
        except Exception as e:
            st.error(f"❌ **Erro durante a resolução:** {str(e)}")
            st.exception(e)


# ------------------------------------------------------------------ BRANCH & BOUND PAGE

def bab_page():
    st.header("🌳 Branch & Bound")
    st.markdown("*Resolução de Problemas de Programação Linear Inteira*")

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
    st.markdown("### 📝 **Função Objetivo (Maximização)**")
    st.markdown("*Defina os coeficientes da função que será maximizada*")
    
    obj_cols = st.columns(n_vars)
    c = []
    for i in range(n_vars):
        default = saved_c[i] if i < len(saved_c) else 1.0
        with obj_cols[i]:
            c.append(st.number_input(f"**x{i+1}**", value=default, key=f"bb_c_{i}", help=f"Coeficiente da variável x{i+1}"))

    # Restrições
    st.markdown("### 📋 **Restrições (≤)**")
    st.markdown("*Configure as restrições que limitam o problema*")
    
    A, b = [], []
    for r in range(n_cons):
        st.markdown(f"**Restrição {r+1}:**")
        cols = st.columns(n_vars + 1)
        row = []
        
        # Coeficientes das variáveis
        for i in range(n_vars):
            default = saved_A[r][i] if r < len(saved_A) and i < len(saved_A[r]) else 1.0
            with cols[i]:
                row.append(st.number_input(f"**x{i+1}**", key=f"bb_a_{r}_{i}", value=default, help=f"Coeficiente de x{i+1}"))
        
        # Valor do lado direito
        with cols[-1]:
            default_rhs = saved_b[r] if r < len(saved_b) else 1.0
            rhs = st.number_input("**≤ Valor**", key=f"bb_b_{r}", value=default_rhs, help=f"Valor do lado direito")
        
        A.append(row)
        b.append(rhs)

    # Seleção de variáveis inteiras
    st.markdown("### 🔢 **Variáveis Inteiras**")
    st.markdown("*Marque quais variáveis devem ter valores inteiros*")
    
    int_cols = st.columns(n_vars)
    int_vars = []
    for i in range(n_vars):
        with int_cols[i]:
            is_int = st.checkbox(f"**x{i+1}** é inteira", value=(i in saved_int), key=f"int_{i}")
            if is_int:
                int_vars.append(i)

    # Botão resolver
    st.markdown("---")
    if st.button("🚀 **Resolver Branch & Bound**", type="primary", use_container_width=True):
        try:
            with st.spinner("🔄 Resolvendo problema inteiro..."):
                solver = BranchBoundSolver()
                solver.solve(c, A, b, integer_vars=int_vars)
                
                if solver.best_solution is None:
                    st.error("❌ **Nenhuma solução inteira encontrada**")
                    st.info("Isso pode indicar que o problema é infactível ou que não existem soluções inteiras.")
                else:
                    # Salvar problema e adicionar ao histórico
                    _store_problem(c, A, b, int_vars)
                    st.session_state.setdefault("history", []).append({
                        "method": "Branch & Bound",
                        "c": c,
                        "A": A,
                        "b": b,
                        "z": solver.best_value,
                        "solution": solver.best_solution,
                        "integer_vars": int_vars
                    })
                    
                    # Mostrar resultado
                    st.success("🎉 **Solução Inteira Ótima Encontrada!**")
                    
                    # Valor ótimo e variáveis
                    col_result1, col_result2 = st.columns(2)
                    with col_result1:
                        st.metric("**Valor Ótimo Z***", f"{solver.best_value:.3f}")
                    
                    with col_result2:
                        st.markdown("**Valores das Variáveis:**")
                        for i, v in enumerate(solver.best_solution[:n_vars]):
                            st.write(f"• x{i+1} = {int(v) if abs(v - round(v)) < 1e-6 else v:.3f}")
                    
                    # Resumo do algoritmo
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
                    
                    # Passos do algoritmo
                    if solver.steps:
                        with st.expander("📝 **Passos do Algoritmo**", expanded=False):
                            for i, step in enumerate(solver.steps):
                                st.write(f"**{i+1}.** {step}")
                    
                    # Visualização da árvore
                    _render_branch_bound_tree(solver)
                    
        except Exception as e:
            st.error(f"❌ **Erro durante a resolução:** {str(e)}")
            st.exception(e)


def _render_branch_bound_tree(solver):
    """
    Renderiza a árvore de Branch & Bound usando diferentes métodos disponíveis.
    """
    st.markdown("---")
    st.markdown("### 🌳 **Árvore de Branch & Bound**")
    
    # Tentar usar streamlit-link-analysis
    try:
        import streamlit_link_analysis
        
        # Preparar dados para o gráfico
        nodes = []
        edges = []
        
        # Cores para diferentes status
        colors = {
            "integer": "#4caf50",    # verde - solução inteira
            "infeasible": "#f44336", # vermelho - infactível  
            "fractional": "#2196f3", # azul - relaxação fracionária
            "processed": "#9e9e9e"   # cinza - processado
        }
        
        # Criar nós
        for n in solver.nodes:
            node_id = str(n["id"])
            
            # Determinar cor e status
            if not n["feasible"]:
                color = colors["infeasible"]
                status = "Infactível"
            elif n.get("integer_feasible"):
                color = colors["integer"]
                status = "Solução Inteira"
            elif n.get("processed"):
                color = colors["processed"]
                status = "Podado"
            else:
                color = colors["fractional"]
                status = "Relaxação"
            
            # Criar label do nó
            if n["feasible"]:
                label = f"Nó {n['id']}\nZ = {n['value']:.2f}\n{status}"
            else:
                label = f"Nó {n['id']}\nInfactível"
            
            nodes.append({
                "id": node_id,
                "label": label,
                "color": color,
                "size": 25,
                "font": {"size": 12}
            })
        
        # Criar arestas
        for n in solver.nodes:
            if n.get("parent") is not None:
                edges.append({
                    "from": str(n["parent"]),
                    "to": str(n["id"]),
                    "arrows": "to"
                })
        
        # Configuração do gráfico
        config = {
            "height": 600,
            "physics": {
                "enabled": True,
                "solver": "hierarchicalRepulsion",
                "hierarchicalRepulsion": {
                    "centralGravity": 0.0,
                    "springLength": 100,
                    "springConstant": 0.01,
                    "nodeDistance": 120,
                    "damping": 0.09
                }
            },
            "layout": {
                "hierarchical": {
                    "enabled": True,
                    "direction": "UD",
                    "sortMethod": "directed"
                }
            }
        }
        
        # Renderizar
        streamlit_link_analysis.st_link_analysis(
            elements={"nodes": nodes, "edges": edges},
            config=config,
            key="bb_tree"
        )
        
        # Legenda
        st.markdown("""
        **Legenda:**
        - 🟢 **Verde**: Solução inteira encontrada
        - 🔴 **Vermelho**: Nó infactível (podado por inviabilidade)
        - 🔵 **Azul**: Relaxação linear (solução fracionária)
        - ⚫ **Cinza**: Nó processado/podado por bound
        """)
        
    except ImportError:
        # Fallback: Usar plotly se disponível
        try:
            import plotly.graph_objects as go
            
            st.info("📦 Para melhor visualização, instale: `pip install streamlit-link-analysis`")
            
            # Criar gráfico com plotly
            fig = go.Figure()
            
            # Preparar dados dos nós
            node_data = {
                "id": [],
                "x": [],
                "y": [],
                "text": [],
                "color": [],
                "size": []
            }
            
            # Layout simples em árvore (posicionamento manual)
            levels = {}
            for n in solver.nodes:
                parent = n.get("parent")
                if parent is None:
                    levels[n["id"]] = 0
                else:
                    levels[n["id"]] = levels.get(parent, 0) + 1
            
            max_level = max(levels.values()) if levels else 0
            level_counts = {i: 0 for i in range(max_level + 1)}
            
            for n in solver.nodes:
                level = levels[n["id"]]
                x = level_counts[level] - (sum(1 for nid, l in levels.items() if l == level) - 1) / 2
                y = -level
                level_counts[level] += 1
                
                # Cor baseada no status
                if not n["feasible"]:
                    color = "red"
                    status = "Inf"
                elif n.get("integer_feasible"):
                    color = "green"
                    status = "Int"
                else:
                    color = "blue"
                    status = "Frac"
                
                node_data["id"].append(n["id"])
                node_data["x"].append(x)
                node_data["y"].append(y)
                node_data["text"].append(f"Nó {n['id']}<br>Z={n['value']:.2f}<br>{status}")
                node_data["color"].append(color)
                node_data["size"].append(20)
            
            # Adicionar nós
            fig.add_trace(go.Scatter(
                x=node_data["x"],
                y=node_data["y"],
                mode='markers+text',
                marker=dict(
                    size=node_data["size"],
                    color=node_data["color"],
                    line=dict(width=2, color='black')
                ),
                text=[f"N{nid}" for nid in node_data["id"]],
                textposition="middle center",
                hovertext=node_data["text"],
                hoverinfo="text",
                name="Nós"
            ))
            
            # Adicionar arestas
            for n in solver.nodes:
                if n.get("parent") is not None:
                    parent_idx = node_data["id"].index(n["parent"])
                    node_idx = node_data["id"].index(n["id"])
                    
                    fig.add_trace(go.Scatter(
                        x=[node_data["x"][parent_idx], node_data["x"][node_idx]],
                        y=[node_data["y"][parent_idx], node_data["y"][node_idx]],
                        mode='lines',
                        line=dict(color='gray', width=2),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
            
            fig.update_layout(
                title="Árvore de Branch & Bound",
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                showlegend=False,
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except ImportError:
            # Fallback: Visualização em texto estruturado
            st.warning("📦 Para visualização gráfica, instale: `pip install streamlit-link-analysis plotly`")
            
            st.markdown("**Estrutura da Árvore (Formato Texto):**")
            
            def print_tree_text(node_id, nodes_dict, level=0):
                """Imprime árvore em formato texto hierárquico."""
                indent = "│   " * level
                node = nodes_dict[node_id]
                
                # Escolher ícone e cor baseado no status
                if not node["feasible"]:
                    icon = "❌"
                    status = "Infactível"
                elif node.get("integer_feasible"):
                    icon = "✅"
                    status = f"Solução Inteira (Z = {node['value']:.3f})"
                else:
                    icon = "🔄"
                    status = f"Relaxação (Z = {node['value']:.3f})"
                
                # Mostrar nó
                node_text = f"{indent}├─ {icon} **Nó {node_id}**: {status}"
                st.markdown(node_text)
                
                # Mostrar bounds se existirem
                if node.get("bounds"):
                    bounds_text = ", ".join([f"x{var+1} {op} {val}" for var, (op, val) in node["bounds"].items()])
                    st.markdown(f"{indent}│   *Bounds: {bounds_text}*")
                
                # Recursão para filhos
                children = [n for n in nodes_dict.values() if n.get("parent") == node_id]
                children.sort(key=lambda x: x["id"])
                for child in children:
                    print_tree_text(child["id"], nodes_dict, level + 1)
            
            # Converter para dicionário e mostrar
            nodes_dict = {n["id"]: n for n in solver.nodes}
            if nodes_dict:
                st.markdown("**🌱 Raiz:**")
                print_tree_text(0, nodes_dict)
    
    except Exception as e:
        st.error(f"Erro na visualização da árvore: {str(e)}")
        
        # Último recurso: tabela simples
        st.markdown("**📊 Tabela de Nós:**")
        
        table_data = []
        for n in solver.nodes:
            status = "Infactível" if not n["feasible"] else ("Inteira" if n.get("integer_feasible") else "Fracionária")
            value_str = f"{n['value']:.3f}" if n["feasible"] else "N/A"
            parent_str = str(n["parent"]) if n.get("parent") is not None else "—"
            
            table_data.append({
                "Nó": n["id"],
                "Pai": parent_str,
                "Valor Z": value_str,
                "Status": status,
                "Processado": "Sim" if n.get("processed") else "Não"
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)


# ================================ LEARNING PAGE ================================

def learning_page():
    st.header("📚 Módulo de Aprendizado")
    st.markdown("*Conteúdos teóricos e educacionais sobre otimização*")
    
    # Placeholder para conteúdo futuro
    st.info("🚧 Em desenvolvimento - Conteúdos teóricos serão adicionados em breve!")
    
    # Seções planejadas
    with st.expander("📋 **Conteúdos Planejados**"):
        st.markdown("""
        ### 🎯 Tópicos que serão abordados:
        
        #### 📐 **Método Simplex**
        - Fundamentação teórica
        - Interpretação geométrica
        - Casos especiais (degeneração, ciclagem)
        - Análise de sensibilidade
        
        #### 🌳 **Branch & Bound**
        - Algoritmos de enumeração
        - Estratégias de ramificação
        - Técnicas de poda
        - Complexidade computacional
        
        #### 📊 **Programação Linear**
        - Modelagem de problemas
        - Dualidade
        - Análise pós-ótima
        - Aplicações práticas
        
        #### 🎮 **Exercícios Interativos**
        - Problemas guiados passo a passo
        - Quiz de conceitos
        - Simulações interativas
        - Estudos de caso
        """)
    
    # Links úteis temporários
    with st.expander("🔗 **Recursos Externos**"):
        st.markdown("""
        ### 📚 **Referências Recomendadas:**
        
        - **Livros Clássicos:**
          - Hillier & Lieberman - Introduction to Operations Research
          - Bazaraa, Jarvis & Sherali - Linear Programming and Network Flows
          
        - **Recursos Online:**
          - MIT OpenCourseWare - Linear Programming
          - Khan Academy - Linear Programming
          
        - **Softwares Complementares:**
          - CPLEX, Gurobi (comerciais)
          - GLPK, CBC (open source)
        """)