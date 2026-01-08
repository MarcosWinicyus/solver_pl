from typing import List

import streamlit as st

from .helpers import _store_problem, _load_problem, number_emojis
from core.simplex_solver import SimplexSolver
from .plots import feasible_region_2d, feasible_region_3d
from .tableau_display import (
    show_tableau_with_basis_info, 
    show_final_solution,
    show_optimization_summary,
    extract_basis_variables
)

def simplex_ui():
    st.markdown("<h1 style='text-align: center;'>📐 Método Simplex - Tableau</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # carregamento de estado anterior (se existir)
    saved = st.session_state.get("problem", {})
    sv_c, sv_A, sv_b = saved.get("c", []), saved.get("A", []), saved.get("b", [])

    col_counts = st.columns(3)
    with col_counts[0]:
        n_vars = st.number_input("🔢 **Número de Variáveis**", 2, 10, max(len(sv_c), 2), help="Quantidade de variáveis de decisão")
    with col_counts[1]:
        n_cons = st.number_input("📏 **Número de Restrições**", 1, 10, max(len(sv_A), 1), help="Quantidade de restrições do problema")

    # Ler preferência de maximização salva
    saved_maximize = saved.get("maximize", True)
    maximize_idx = 0 if saved_maximize else 1

    with col_counts[2]:

        maximize = st.selectbox(
            "🎯 Tipo de otimização:",
            ("🔺 Maximizar", "🔻 Minimizar"),
            index=maximize_idx,
            help="Tipo de otimização em relação ao valor de Z, Maximizar ou Mínimizar"
        )
        
    is_max = (maximize == "🔺 Maximizar")

    st.markdown("#### 📝 **Coeficientes da Função Objetivo**", help="Defina os coeficientes da função Z que será otimizada")
    
    obj_cols = st.columns(n_vars)
    c: List[float] = []
    for i in range(n_vars):
        default = sv_c[i] if i < len(sv_c) else 1.0
        with obj_cols[i]:
            c.append(st.number_input(f"**x{i+1}**", value=default, key=f"c_{i}", help=f"Coeficiente da variável x{i+1}"))

    # ---------- restrições -------------------------------------------
    # ---------- restrições -------------------------------------------
    with st.expander("📋 **Restrições do Problema**", expanded=True):
        
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
    col_opt1, col_opt2, col_btn = st.columns([0.35, 0.25, 0.4])
    with col_opt1:
        didactic_mode = st.checkbox("🎓 **Modo Didático**", value=True, help="Mostrar explicações detalhadas passo a passo", key="didactic_mode_cb")
    with col_opt2:
        step_by_step = st.checkbox("👣 **Passo a Passo**", value=False, disabled=not didactic_mode)
        if not didactic_mode: step_by_step = False
    with col_btn:
        solve_clicked = st.button("🚀 **Resolver Problema**", type="primary", use_container_width=True)

    if solve_clicked:
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
             solver = SimplexSolver()
             # is_max já está definido na linha 41
             
             if step_by_step and didactic_mode:
                 solver.initialize(c, A_conv, b_conv, maximize=is_max)
                 st.session_state["simplex_solver"] = solver
                 st.session_state["simplex_params"] = {
                     "c": c, "A": A_conv, "b": b_conv, "max": is_max
                 }
                 st.rerun()
             else:
                 solver.solve(c, A_conv, b_conv, maximize=is_max)
                 st.session_state["simplex_solver"] = solver
                 st.session_state["simplex_params"] = {
                     "c": c, "A": A_conv, "b": b_conv, "max": is_max
                 }
                 
                 # Salvar histórico no modo normal
                 if solver.optimal:
                     sol, z = solver.get_solution()
                     st.session_state.setdefault("history", []).append({
                        "method": "Simplex", "c": c, "A": A, "b": b, "z": z, "solution": sol, "maximize": is_max
                     })
                     
        except Exception as e:
             st.error(f"Erro ao iniciar solver: {e}")
             st.exception(e)



    # --------------------------------------------------------------------------
    # Renderização de Resultados
    # --------------------------------------------------------------------------
    if "simplex_solver" in st.session_state:
        solver = st.session_state["simplex_solver"]
        params = st.session_state.get("simplex_params", {})
        is_max = params.get("max", True)
        
        if solver.unbounded:
            st.error("⚠️ **Problema Ilimitado** - A função objetivo pode crescer infinitamente")
        elif solver.infeasible:
             st.error("❌ **Não foi possível encontrar solução ótima** (Inviável)")
        
        # Validar se tem tableaux para mostrar
        if solver.tableaux:
             # Tenta extrair solução se ótima
             if solver.optimal:
                 try:
                     final_sol, final_z = solver.get_solution()
                     st.success(f"🎉 **Solução Ótima Encontrada!**")
                     basis_info = solver.get_basis_info()
                     show_final_solution(
                        solution=final_sol, 
                        objective_value=final_z, 
                        basis_info=basis_info,
                        maximize=is_max,
                        method="Simplex Primal",
                        iterations=len(solver.steps) - 1
                     )
                 except Exception as e:
                     st.warning(f"Detalhes da solução não disponíveis: {e}")

             # ----- Mostrar iterações do algoritmo ------------------------
             st.markdown("---")
             col_hdr, col_nx = st.columns([0.75, 0.25])
             with col_hdr:
                 st.markdown("### 📊 **Iterações do Algoritmo Simplex**")
             with col_nx:
                 if step_by_step and didactic_mode and not solver.finished:
                     if st.button("⏭️ **Próximo Passo**", type="primary", key="btn_next_step_simplex_inline"):
                         solver.step()
                         st.rerun()
                
        for idx, (tbl, step, desc, piv) in enumerate(
            zip(solver.tableaux, solver.steps, solver.decisions, solver.pivots)
        ):
            # Expandir lógica
            is_initial = idx == 0
            is_final = "Ótima" in step
            is_last = idx == len(solver.tableaux) - 1
            
            # Se passo a passo, expande apenas o último. Se não, expande inicial e final.
            should_expand = is_last if step_by_step else (is_initial or is_final)
            
            if didactic_mode:
                with st.expander(f"**{step}**", expanded=should_expand):
                    st.markdown(desc)
                    st.markdown("---")
                    
                    # Extrair informações da base para este tableau
                    if hasattr(solver, '_current_basis') and idx > 0:
                        basis_info = extract_basis_variables(tbl, solver._current_basis, len(c))
                    else:
                        basis_info = [(f"s{i+1}", tbl[i+1, -1]) for i in range(tbl.shape[0]-1)]
                    # Mostrar tableau com índices corretos das variáveis básicas
                    show_tableau_with_basis_info(tbl, basis_info, pivot=piv, show_legend=didactic_mode)
                    
                    if piv != (-1, -1) and "Iteração" in step and idx > 0:
                        pr, pc = piv
                        st.markdown("---")
                        st.markdown("#### 🔄 **Resumo da Operação de Pivoteamento**")
                        col1, col2, col3 = st.columns(3)
                        with col1: st.success(f"**🟢 Entra na Base:**\n\nx{pc+1}")
                        with col2: st.warning(f"**⚡ Elemento Pivot:**\n\n{tbl[pr, pc]:.3f}")
                        with col3: st.error(f"**🔴 Sai da Base:**\n\nLinha {pr}")
                        
                        st.markdown("#### 📋 **Detalhes Técnicos**")
                        details_col1, details_col2 = st.columns(2)
                        with details_col1:
                            st.markdown(f"**Posição do Pivot:**\n- Linha: {pr}\n- Coluna: {pc+1}\n- Valor: {tbl[pr, pc]:.6f}")
                        with details_col2:
                            st.markdown(f"**Operações Realizadas:**\n- ✅ Linha {pr} ÷ {tbl[pr, pc]:.3f}\n- ✅ Eliminar coluna {pc+1}\n- ✅ Atualizar base")

                    if idx > 0:
                        st.markdown("---")
                        st.markdown("#### 📊 **Análise da Base Atual**")
                        basic_vars = [info for info in basis_info if abs(info[1]) > 1e-6]
                        if basic_vars:
                            st.markdown("**💡 Interpretação:**")
                            decision_vars = [(name, val) for name, val in basic_vars if name.startswith('x')]
                            slack_vars = [(name, val) for name, val in basic_vars if name.startswith('s')]
                            if decision_vars: st.markdown(f"• **Variáveis de decisão ativas:** {', '.join([f'{n} = {v:.3f}' for n, v in decision_vars])}")
                            if slack_vars: st.markdown(f"• **Folgas disponíveis:** {', '.join([f'{n} = {v:.3f}' for n, v in slack_vars])}")
                            all_decision_vars = [f"x{i+1}" for i in range(len(c))]
                            basic_decision_names = [name for name, _ in decision_vars]
                            non_basic_decision = [var for var in all_decision_vars if var not in basic_decision_names]
                            if non_basic_decision: st.markdown(f"• **Variáveis não-básicas (= 0):** {', '.join(non_basic_decision)}")

            else:
                # Modo Não-Didático: Apenas Tableau Limpo
                
                # Mostrar razão e linha aplicada da iteração ANTERIOR (transição)
                if idx > 0:
                    prev_piv = solver.pivots[idx-1]
                    if prev_piv != (-1, -1):
                        pr, pc = prev_piv
                        prev_tbl = solver.tableaux[idx-1]
                        pivot_val = prev_tbl[pr, pc]
                        st.markdown(f"**Linha Aplicada:** {pr} | **Elemento Pivot:** {pivot_val:.3f}")
                
                st.markdown(f"##### **{step}**")
                # Passar basis_vars=None para esconder a seção "Status da Base Atual"
                show_tableau_with_basis_info(tbl, basis_vars=None, pivot=piv, show_legend=False)
                st.markdown("---")

        # ----- Visualização da Região Factível (2D/3D) -------------------
        if params.get("A") and params.get("b"):
             A_plot = params["A"]
             b_plot = params["b"]
             c_plot = params["c"]
             n_plot = len(c_plot)
             
             optimal_sol = None
             if solver.optimal:
                 try:
                     sol_values, _ = solver.get_solution()
                     # Garantir que temos valores para as variáveis originais
                     if len(sol_values) >= n_plot:
                        optimal_sol = sol_values[:n_plot]
                 except:
                     pass

             fig = None
             if n_plot == 2:
                 st.markdown("### 📈 **Visualização da Região Factível (2D)**")
                 fig = feasible_region_2d(c_plot, A_plot, b_plot, optimal_solution=optimal_sol)
             elif n_plot == 3:
                 st.markdown("### 🧊 **Visualização da Região Factível (3D)**")
                 fig = feasible_region_3d(c_plot, A_plot, b_plot, optimal_solution=optimal_sol)
             
             if fig:
                 st.plotly_chart(fig, use_container_width=True)
             elif n_plot in [2, 3]:
                 # Se não gerou figura mas é 2D/3D, avisa.
                 # Pode ocorrer se região ilimitada ou vazia com o método vertex.
                 # O método 'find_vertices' pode retornar vazio.
                 pass
                



