from typing import List

import streamlit as st

from .helpers import _store_problem, _load_problem, number_emojis
from core.simplex_solver import SimplexSolver
from .plots import feasible_region_2d
from .tableau_display import (
    show_tableau_with_basis_info, 
    show_final_solution,
    show_optimization_summary,
    extract_basis_variables
)

def simplex_ui():
    st.header("📐 Método Simplex - Tableau")

    # carregamento de estado anterior (se existir)
    saved = st.session_state.get("problem", {})
    sv_c, sv_A, sv_b = saved.get("c", []), saved.get("A", []), saved.get("b", [])

    col_counts = st.columns(3)
    with col_counts[0]:
        n_vars = st.number_input("🔢 **Número de Variáveis**", 2, 5, max(len(sv_c), 2), help="Quantidade de variáveis de decisão")
    with col_counts[1]:
        n_cons = st.number_input("📏 **Número de Restrições**", 1, 5, max(len(sv_A), 1), help="Quantidade de restrições do problema")

    with col_counts[2]:

        maximize = st.selectbox(
            "🎯 Tipo de otimização:",
            ("🔺 Maximizar", "🔻 Minimizar"),
            help="Tipo de otimização em relação ao valor de Z, Maximizar ou Mínimizar"
        )

    st.markdown("#### 📝 **Coeficientes da Função Objetivo**", help="Defina os coeficientes da função Z que será otimizada")
    
    obj_cols = st.columns(n_vars)
    c: List[float] = []
    for i in range(n_vars):
        default = sv_c[i] if i < len(sv_c) else 1.0
        with obj_cols[i]:
            c.append(st.number_input(f"**x{i+1}**", value=default, key=f"c_{i}", help=f"Coeficiente da variável x{i+1}"))

    # ---------- restrições -------------------------------------------
    st.markdown("#### 📋 **Restrições do Problema**", help="Configure as restrições que limitam o problema")
    
    A: List[List[float]] = []
    b: List[float] = []
    senses: List[str] = []

    
    for r in range(n_cons):
        st.markdown(f"**Restrição - {number_emojis[r+1]}:**")
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
    if st.button("🚀 **Resolver Problema**", type="primary", width='stretch'):
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
                        st.plotly_chart(fig, width='stretch')
                    else:
                        st.info("Gráfico disponível apenas para problemas com 2 variáveis")
                        
        except Exception as e:
            st.error(f"❌ **Erro durante a resolução:** {str(e)}")
            st.exception(e)

