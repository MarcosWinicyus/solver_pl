
import streamlit as st
import numpy as np
import pandas as pd
from ui.library_page import load_problem_and_redirect

def duality_ui():
    st.markdown("<h1 style='text-align: center;'>🔄 Dualidade (Conversor Primal-Dual)</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center;'>
        Ferramenta para converter problemas Primais em seus equivalentes Duais.<br>
        <b>Teorema da Dualidade:</b> Primal <b>Max</b> Z = cx (Ax ≤ b) ↔ Dual <b>Min</b> W = by (Aᵀy ≥ c)
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- Configuração do Primal ---
    st.subheader("1. Definição do Problema Primal")
    
    col_counts = st.columns(3)
    with col_counts[0]:
        n_vars = st.number_input("🔢 **Número de Variáveis (Primal)**", 2, 10, 2, help="Quantidade de variáveis de decisão")
    with col_counts[1]:
        n_constr = st.number_input("📏 **Número de Restrições (Primal)**", 1, 10, 2, help="Quantidade de restrições")
    
    with col_counts[2]:
        maximize = st.selectbox(
            "🎯 Tipo de otimização:",
            ("🔺 Maximizar", "🔻 Minimizar"),
            index=0,
            help="Tipo de otimização do Primal"
        )
    is_max = (maximize == "🔺 Maximizar")

    st.markdown("#### Função Objetivo Primal ($Z$)")
    cols_c = st.columns(n_vars)
    c = []
    for i in range(n_vars):
        with cols_c[i]:
            val = st.number_input(f"**x{i+1}**", value=1.0, key=f"p_c_{i}")
            c.append(val)

    st.markdown("#### Restrições Primal")
    A = []
    b = []
    senses = []
    
    for r in range(n_constr):
        st.markdown(f"**Restrição {r+1}:**")
        cols = st.columns(n_vars + 2)
        row = []
        for j in range(n_vars):
            with cols[j]:
                val = st.number_input(f"**x{j+1}**", value=1.0, key=f"p_a_{r}_{j}", help=f"Coeficiente de x{j+1}")
                row.append(val)
        
        with cols[n_vars]:
            sense = st.selectbox("Tipo", ["≤", "=", "≥"], index=0, key=f"p_sense_{r}")
            senses.append(sense)
            
        with cols[n_vars+1]:
            val_b = st.number_input("**Valor**", value=10.0, key=f"p_b_{r}")
            b.append(val_b)
        A.append(row)

    # --- Conversão ---
    if st.button("🔄 Converter para DUAL", type="primary"):
        # Lógica de processamento
        n_vars_dual = n_constr
        n_constr_dual = n_vars
        
        A_np = np.array(A)
        b_np = np.array(b)
        c_np = np.array(c)
        
        A_dual = A_np.T.tolist()
        c_dual = b_np.tolist() 
        b_dual = c_np.tolist()
        
        dual_is_max = not is_max
        objective_name = "Minimizar" if not dual_is_max else "Maximizar"
        
        dual_sense_default = "≥" if is_max else "≤"
        
        dual_vars_domain = []
        for s in senses:
            if is_max:
                if s == "≤": domain = "≥ 0"
                elif s == "≥": domain = "≤ 0"
                else: domain = "Livre"
            else:
                if s == "≥": domain = "≥ 0"
                elif s == "≤": domain = "≤ 0"
                else: domain = "Livre"
            dual_vars_domain.append(domain)
            
        # Salvar no session state para persistencia
        st.session_state["dual_result"] = {
            "n_vars_dual": n_vars_dual,
            "n_constr_dual": n_constr_dual,
            "c_dual": c_dual,
            "A_dual": A_dual,
            "b_dual": b_dual,
            "is_max": is_max,
            "dual_is_max": dual_is_max,
            "objective_name": objective_name,
            "dual_sense_default": dual_sense_default,
            "dual_vars_domain": dual_vars_domain,
            "c_original": c,
            "A_original": A,
            "b_original": b,
            "senses_original": senses
        }

    # --- Exibição do Resultado (Persistente) ---
    if "dual_result" in st.session_state:
        res = st.session_state["dual_result"]
        
        st.divider()
        st.subheader("2. Problema Dual Resultante")
        
        col_primal, col_dual = st.columns(2)
        
        with col_primal:
            st.markdown("##### Primal")
            st.latex(f"{'Max' if res['is_max'] else 'Min'} \ Z = " + " + ".join([f"{val}x_{i+1}" for i, val in enumerate(res['c_original'])]))
            st.markdown("Sujeito a:")
            for i in range(len(res["A_original"])):
                lhs = " + ".join([f"{res['A_original'][i][j]}x_{j+1}" for j in range(len(res['c_original']))])
                st.latex(f"{lhs} \ {res['senses_original'][i]} \ {res['b_original'][i]}")
            st.markdown("$x_j \ge 0$")
                
        with col_dual:
            st.markdown("##### Dual")
            desig = res['dual_sense_default']
            
            st.latex(f"{res['objective_name']} \ W = " + " + ".join([f"{val}y_{i+1}" for i, val in enumerate(res['c_dual'])]))
            st.markdown("Sujeito a:")
            for i in range(res["n_constr_dual"]):
                lhs = " + ".join([f"{res['A_dual'][i][j]}y_{j+1}" for j in range(res["n_vars_dual"])])
                st.latex(f"{lhs} \ {desig} \ {res['b_dual'][i]}")
            
            st.markdown("**Domínio das Variáveis:**")
            for i, dom in enumerate(res['dual_vars_domain']):
                st.markdown(f"$y_{i+1}$: {dom}")
            
            st.divider()
            st.markdown("###### Resolver:")
            
            # Botões dentro da coluna do Dual
            b_col1, b_col2 = st.columns(2)
            
            # Preparar dados para solver
            dual_problem_data = {
                "c": res['c_dual'],
                "A": res['A_dual'], 
                "b": res['b_dual'],
                "maximize": res['dual_is_max'],
                "int_vars": [],
                "constraint_types": [res['dual_sense_default']] * res["n_constr_dual"]
            }
            
            with b_col1:
                if st.button("📐 Resolver no Simplex", type="primary", key="btn_solve_dual_simplex"):
                    load_problem_and_redirect({
                        "title": "Problema Dual",
                        "target_page": "📐 Método Simplex",
                        "data": dual_problem_data
                    })

            with b_col2:
                if st.button("🌳 Resolver no B&B", type="primary", key="btn_solve_dual_bb"):
                    load_problem_and_redirect({
                        "title": "Problema Dual",
                        "target_page": "🌳 Branch & Bound",
                        "data": dual_problem_data
                    })
