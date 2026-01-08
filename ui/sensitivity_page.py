from typing import List

import streamlit as st
import pandas as pd

from core.simplex_solver import SimplexSolver
from .helpers import number_emojis

def sensitivity_ui():
    st.markdown("<h1 style='text-align: center;'>📊 Análise de Sensibilidade</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center;'>
        Explore como mudanças nos parâmetros (<b>Coeficientes da Função Objetivo</b> e <b>Valores do Lado Direito</b>) 
        afetam a solução ótima e a viabilidade do problema.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Carregar estado anterior (se existir) para preencher defaults
    saved = st.session_state.get("problem", {})
    sv_c, sv_A, sv_b = saved.get("c", []), saved.get("A", []), saved.get("b", [])

    # --- Configuração do Layout (Similar ao Simplex) ---
    col_counts = st.columns(3)
    with col_counts[0]:
        n_vars = st.number_input("🔢 **Variáveis**", 2, 10, max(len(sv_c), 2), help="Quantidade de variáveis de decisão")
    with col_counts[1]:
        n_cons = st.number_input("📏 **Restrições**", 1, 10, max(len(sv_A), 1), help="Quantidade de restrições")
    
    with col_counts[2]:
        maximize = st.selectbox("🎯 **Objetivo**", ("Maximização", "Minimização"), index=0 if saved.get("maximize", True) else 1)

    is_max = (maximize == "Maximização")
    
    # --- Inputs ---
    
    st.markdown("#### 📝 **Função Objetivo**")
    obj_cols = st.columns(n_vars)
    c: List[float] = []
    for i in range(n_vars):
        default = sv_c[i] if i < len(sv_c) else 10.0
        with obj_cols[i]:
            c.append(st.number_input(f"**x{i+1}**", value=default, key=f"sen_c_{i}", help=f"Coeficiente da variável x{i+1}"))

    # Restrições em Expander
    with st.expander("📋 **Restrições do Problema**", expanded=True):
        A: List[List[float]] = []
        b: List[float] = []
        senses: List[str] = []
        
        for r in range(n_cons):
            st.markdown(f"**Restrição - {number_emojis[r+1]}:**")
            cols = st.columns(n_vars + 2)
            row = []
            
            for i in range(n_vars):
                default = sv_A[r][i] if r < len(sv_A) and i < len(sv_A[r]) else 1.0
                with cols[i]:
                    row.append(st.number_input(f"**x{i+1}**", value=default, key=f"sen_a_{r}_{i}", help=f"Coeficiente de x{i+1}"))
            
            with cols[n_vars]:
                sense = st.selectbox("**Tipo**", ["≤", "=", "≥"], key=f"sen_sense_{r}", help="Selecione o tipo")
            
            with cols[n_vars+1]:
                rhs_default = sv_b[r] if r < len(sv_b) else 10.0
                rhs = st.number_input("**Valor**", value=rhs_default, key=f"sen_b_{r}", help="Valor do lado direito")
            
            A.append(row)
            b.append(rhs)
            senses.append(sense)

    # Botão de Análise
    if st.button("🔎 **Gerar Relatório de Sensibilidade**", type="primary", use_container_width=True):
        # Conversão Simples para Standard (<=)
        A_conv, b_conv = [], []
        for row, rhs, sn in zip(A, b, senses):
            if sn == "≤":
                A_conv.append(row)
                b_conv.append(rhs)
            elif sn == "≥":
                A_conv.append([-x for x in row])
                b_conv.append(-rhs)
            else: # =
                A_conv.append(row)
                b_conv.append(rhs)
                A_conv.append([-x for x in row])
                b_conv.append(-rhs)

        try:
            solver = SimplexSolver()
            solver.solve(c, A_conv, b_conv, maximize=is_max)
            
            if not solver.optimal:
                st.error("❌ O problema não possui solução ótima finita. Não é possível realizar análise de sensibilidade.")
                return

            analysis = solver.get_sensitivity_analysis()
            
            st.divider()
            st.success("✅ **Análise Gerada com Sucesso!**")
            
            # --- Exibição dos Resultados ---
            
            # 1. Tabela de Coeficientes da Função Objetivo
            st.subheader("1. Sensibilidade dos Coeficientes da Função Objetivo ($c_j$)")
            st.markdown("""
            Analisa o quanto o lucro (ou custo) unitário de cada variável pode mudar sem que a **base ótima** se altere.
            - **Status**: Se a variável está na Base (produzida) ou Não-Básica (não vale a pena produzir).
            - **Custo Reduzido**: Quanto o lucro deve aumentar para a variável entrar na base (para não-básicas).
            """)
            
            obj_data = []
            for item in analysis["objective"]:
                obj_data.append({
                    "Variável": item["var"],
                    "Valor Atual": f"{item['current_cost']:.2f}",
                    "Min Permitido": f"{item['min']:.2f}" if isinstance(item['min'], (int, float)) else item['min'],
                    "Max Permitido": f"{item['max']:.2f}" if isinstance(item['max'], (int, float)) else item['max'],
                    "Status": item["status"]
                })
            st.dataframe(pd.DataFrame(obj_data), use_container_width=True, hide_index=True)

            st.write("")
            
            # 2. Tabela de RHS (Shadow Prices)
            st.subheader("2. Sensibilidade das Restrições (RHS $b_i$)")
            st.markdown("""
            Analisa o valor marginal (Preço Sombra) de cada recurso e os limites de disponibilidade.
            - **Preço Sombra**: Quanto a função objetivo melhora se aumentarmos 1 unidade deste recurso.
            - **Intervalo**: Faixa onde o preço sombra permanece válido (base viável).
            """)
            
            rhs_data = []
            for item in analysis["rhs"]:
                rhs_data.append({
                    "Restrição": f"R{item['id']} ({item['type']})",
                    "Valor Atual": f"{item['current_value']:.2f}",
                    "Preço Sombra": f"{item['shadow_price']:.4f}",
                    "Min Permitido": f"{item['min']:.2f}" if isinstance(item['min'], (int, float)) else item['min'],
                    "Max Permitido": f"{item['max']:.2f}" if isinstance(item['max'], (int, float)) else item['max']
                })
            
            st.dataframe(pd.DataFrame(rhs_data), use_container_width=True, hide_index=True)
            
            # Dica visual
            st.info("💡 **Dica:** O Preço Sombra de uma restrição indica o 'gargalo' do sistema. Restrições com Preço Sombra > 0 são ativas (esgotadas).")

        except Exception as e:
            st.error(f"Erro ao calcular sensibilidade: {e}")
            st.exception(e)
