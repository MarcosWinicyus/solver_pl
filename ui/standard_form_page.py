import streamlit as st
import pandas as pd
from typing import List

from .helpers import number_emojis

def standard_form_ui():
    st.markdown("<h1 style='text-align: center;'>📝 Conversor para Forma Padrão</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center;'>
        Transforme problemas de Programação Linear para a <b>Forma Padrão</b>:
        <br>
        <i>(Maximização, Restrições de Igualdade e RHS não-negativo)</i>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- Configuração Inicial ---
    # Carregar estado ou usar defaults
    saved = st.session_state.get("problem", {})
    sv_c, sv_A, sv_b = saved.get("c", []), saved.get("A", []), saved.get("b", [])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        n_vars = st.number_input("🔢 **Variáveis**", 2, 10, max(len(sv_c), 2))
    with col2:
        n_cons = st.number_input("📏 **Restrições**", 1, 10, max(len(sv_A), 1))
    with col3:
        obj_type = st.selectbox("🎯 **Objetivo**", ["Maximização", "Minimização"])

    # --- Inputs ---
    st.markdown("#### 📝 **Função Objetivo**")
    cols_obj = st.columns(n_vars)
    c = []
    for i in range(n_vars):
        val = sv_c[i] if i < len(sv_c) else 0.0
        with cols_obj[i]:
            c.append(st.number_input(f"**x{i+1}**", value=val, key=f"std_c_{i}", help=f"Coeficiente da variável x{i+1}"))

    # Inputs de Restrições
    A = []
    b = []
    senses = []
    
    with st.expander("📋 **Restrições do Problema**", expanded=True):
        for r in range(n_cons):
            st.markdown(f"**Restrição {number_emojis[r+1]}**")
            cols = st.columns(n_vars + 2)
            row = []
            
            # Coeficientes
            for i in range(n_vars):
                def_val = sv_A[r][i] if r < len(sv_A) and i < len(sv_A[r]) else 0.0
                with cols[i]:
                    row.append(st.number_input(f"**x{i+1}**", value=def_val, key=f"std_a_{r}_{i}", label_visibility="collapsed", help=f"Coeficiente de x{i+1}"))
            
            # Tipo
            with cols[n_vars]:
                sense = st.selectbox("**Tipo**", ["≤", "=", "≥"], key=f"std_sense_{r}", label_visibility="collapsed", help="Tipo da restrição")
            
            # RHS
            with cols[n_vars+1]:
                def_rhs = sv_b[r] if r < len(sv_b) else 0.0
                rhs = st.number_input("**Valor**", value=def_rhs, key=f"std_b_{r}", label_visibility="collapsed", help="Valor do lado direito")
            
            A.append(row)
            b.append(rhs)
            senses.append(sense)

    st.markdown("---")

    if st.button("🔄 **Converter para Forma Padrão**", type="primary", use_container_width=True):
        st.divider()

        # --- Lógica de Conversão ---
        new_c = list(c)
        new_A = [row[:] for row in A]
        new_b = list(b)
        new_vars = [f"x_{{{i+1}}}" for i in range(n_vars)]
        steps = []
        
        # Passo 1: Objetivo
        is_min = (obj_type == "Minimização")
        if is_min:
            new_c = [-val for val in new_c]
            steps.append("⚠️ **Objetivo:** Minimização convertida para Maximização ($Max \ W = -Z$). Invertidos sinais da função objetivo.")
        
        # Passo 2: RHS Negativo
        for i in range(n_cons):
            if new_b[i] < 0:
                new_b[i] = -new_b[i]
                new_A[i] = [-val for val in new_A[i]]
                
                # Inverter desigualdade
                if senses[i] == "≤":
                    senses[i] = "≥"
                    steps.append(f"⚠️ **R{i+1}:** RHS negativo. Multiplicada por -1 e sinal invertido ($\le \\to \ge$).")
                elif senses[i] == "≥":
                    senses[i] = "≤"
                    steps.append(f"⚠️ **R{i+1}:** RHS negativo. Multiplicada por -1 e sinal invertido ($\ge \\to \le$).")
                else:
                    steps.append(f"⚠️ **R{i+1}:** RHS negativo. Multiplicada por -1.")

        # Passo 3: Variáveis de Folga e Excesso
        for i in range(n_cons):
            row = new_A[i]
            
            # Padding para vars já existentes
            while len(row) < len(new_vars):
                row.append(0.0)
                
            if senses[i] == "≤":
                # Adicionar Folga (+s)
                slack_name = f"s_{{{i+1}}}"
                new_vars.append(slack_name)
                
                # Adicionar 1.0 nesta restrição e 0.0 nas outras
                for r_idx in range(n_cons):
                    if r_idx == i:
                        new_A[r_idx].append(1.0)
                    else:
                        if r_idx < len(new_A): # Check safety
                            new_A[r_idx].append(0.0)
                
                # Custo 0 na objetivo
                new_c.append(0.0)
                # steps.append(f"ℹ️ **R{i+1}:** Restrição $\le$. Adicionada variável de folga ${slack_name}$.")
                
            elif senses[i] == "≥":
                # Adicionar Excesso (-e)
                surplus_name = f"e_{{{i+1}}}"
                new_vars.append(surplus_name)
                
                for r_idx in range(n_cons):
                    if r_idx == i:
                        new_A[r_idx].append(-1.0)
                    else:
                        new_A[r_idx].append(0.0)
                        
                new_c.append(0.0)
                # steps.append(f"ℹ️ **R{i+1}:** Restrição $\ge$. Adicionada variável de excesso ${surplus_name}$.")
        
        if steps:
            with st.expander("ℹ️ **Detalhes da Conversão**", expanded=False):
                for step in steps:
                    st.write(step)
        
        # --- Visualização Lado a Lado ---
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("1. Formulação Original")
            
            # Objetivo
            original_obj_str = " + ".join([f"{val}x_{{{i+1}}}" for i, val in enumerate(c)])
            original_obj_str = original_obj_str.replace("+ -", "- ")
            st.latex(f"\\text{{{obj_type[:3]}}} \\ Z = {original_obj_str}")
            
            # Restrições
            st.markdown("**Sujeito a:**")
            orig_latex_lines = []
            for i in range(n_cons):
                lhs = " + ".join([f"{val}x_{{{j+1}}}" for j, val in enumerate(A[i])]).replace("+ -", "- ")
                op = "=" if senses[i] == "=" else ("\\le" if senses[i] == "≤" else "\\ge")
                orig_latex_lines.append(f"{lhs} {op} {b[i]}")
            
            st.latex("\\begin{cases} " + " \\\\ ".join(orig_latex_lines) + " \\\\ x_j \\ge 0 \\end{cases}")

        with c2:
            st.subheader("2. Forma Padrão")
            
            # Objetivo Standard
            std_obj_str = " + ".join([f"{val} {var}" for val, var in zip(new_c, new_vars) if abs(val) > 1e-9])
            if not std_obj_str: std_obj_str = "0"
            std_obj_str = std_obj_str.replace("+ -", "- ")
            
            obj_label = "W" if is_min else "Z"
            st.latex(f"\\text{{Max}} \\ {obj_label} = {std_obj_str}")
            
            # Restrições Standard
            st.markdown("**Sujeito a:**")
            
            std_latex_lines = []
            for i in range(n_cons):
                # Re-pad rows if needed (though loop above should handle it)
                current_row = new_A[i]
                while len(current_row) < len(new_vars):
                    current_row.append(0.0)
                    
                lhs_parts = []
                for j, val in enumerate(current_row):
                    if abs(val) > 1e-9:
                        lhs_parts.append(f"{val} {new_vars[j]}")
                
                lhs_std = " + ".join(lhs_parts).replace("+ -", "- ")
                std_latex_lines.append(f"{lhs_std} = {new_b[i]}")
            
            st.latex("\\begin{cases} " + " \\\\ ".join(std_latex_lines) + " \\\\ x_j, s_i, e_i \\ge 0 \\end{cases}")
        
    # --- Rodapé ---
    st.markdown("---")
    st.caption("ℹ️ A Forma Padrão é pré-requisito para aplicação do algoritmo Simplex, convertendo todas as desigualdades em igualdades através de variáveis auxiliares.")
