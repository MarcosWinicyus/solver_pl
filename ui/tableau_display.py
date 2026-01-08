import pandas as pd
import streamlit as st
import numpy as np


def show_tableau(T, caption="", pivot: tuple[int, int] | None = None, basis_vars=None, show_legend=True):
    """
    Mostra o tableau com formatação aprimorada e índices corretos das variáveis básicas.
    
    Args:
        T: Tableau do simplex (numpy array)
        caption: Título/descrição do tableau
        pivot: Tupla (linha, coluna) para destacar elemento pivot
        basis_vars: Lista de nomes das variáveis básicas para os índices das linhas
        show_legend: Se deve mostrar a legenda de cores (default True)
    """
    rows, cols = T.shape
    n_slack = rows - 1
    n_vars = cols - n_slack - 1

    # Criar nomes das colunas (sem asteriscos)
    col_names = [f"x{i+1}" for i in range(n_vars)] + [f"s{i+1}" for i in range(n_slack)] + ["RHS"]

    # Criar nomes das linhas baseados nas variáveis básicas reais
    if basis_vars and len(basis_vars) >= n_slack:
        # Usar as variáveis básicas fornecidas
        row_names = ["Z"] + [var_name for var_name, _ in basis_vars[:n_slack]]
    else:
        # Fallback para o padrão antigo se não tiver informação da base
        row_names = ["Z"] + [f"R{i+1}" for i in range(n_slack)]

    # Criar DataFrame
    df = pd.DataFrame(T, index=row_names, columns=col_names)

    # Aplicar formatação
    styler = df.style.format("{:.3f}")
    
    # Destacar elemento pivot se fornecido
    if pivot and pivot != (-1, -1):
        pr, pc = pivot
        
        def highlight_pivot(data):
            """Aplica destaque ao elemento pivot, linha e coluna."""
            style_df = pd.DataFrame('', index=data.index, columns=data.columns)
            
            # Destacar elemento pivot em amarelo forte (texto preto para contraste)
            style_df.iloc[pr, pc] = 'background-color: #ffeb3b; color: black; font-weight: bold; border: 2px solid #f57f17;'
            
            # Destacar linha pivot em amarelo claro
            for col in range(cols):
                if col != pc:
                    style_df.iloc[pr, col] = 'background-color: #fff9c4; color: black;'
            
            # Destacar coluna pivot em amarelo claro
            for row in range(rows):
                if row != pr:
                    style_df.iloc[row, pc] = 'background-color: #fff9c4; color: black;'
            
            return style_df
        
        styler = styler.apply(highlight_pivot, axis=None)
    
    # Destacar linha Z (função objetivo)
    def highlight_objective(data):
        style_df = pd.DataFrame('', index=data.index, columns=data.columns)
        for col in range(cols):
            if pivot is None or pivot == (-1, -1) or (0, col) != pivot:
                style_df.iloc[0, col] = 'background-color: #e3f2fd; color: black; font-weight: bold;'
        return style_df
    
    if pivot is None or pivot == (-1, -1):
        styler = styler.apply(highlight_objective, axis=None)

    # Mostrar caption se fornecido
    if caption:
        st.markdown(f"**{caption}**")
    
    # Exibir o tableau
    st.dataframe(styler, width='stretch')
    
    # Adicionar legenda explicativa se houver pivot
    if show_legend and pivot and pivot != (-1, -1):
        st.markdown("""
        **Legenda:**
        - 🟨 **Amarelo Forte**: Elemento pivot
        - 🟡 **Amarelo Claro**: Linha e coluna do pivot
        - 🔵 **Azul Claro**: Linha da função objetivo (Z)
        """)


def show_tableau_with_basis_info(T, basis_vars=None, caption="", pivot=None, show_legend=True):
    """
    Mostra o tableau com informações adicionais sobre a base.
    
    Args:
        T: Tableau do simplex
        basis_vars: Lista com tuplas (nome_variavel, valor) das variáveis básicas
        caption: Título do tableau
        pivot: Elemento pivot para destacar
        show_legend: Se deve mostrar a legenda de cores
    """
    # Mostrar tableau principal com índices corretos
    show_tableau(T, caption, pivot, basis_vars, show_legend=show_legend)
    
    # Mostrar informações da base se fornecidas
    if basis_vars:
        st.markdown("---")
        st.markdown("#### 📋 **Status da Base Atual**")
        
        # Separar variáveis básicas com valor significativo
        significant_vars = [(name, val) for name, val in basis_vars if abs(val) > 1e-6]
        zero_vars = [(name, val) for name, val in basis_vars if abs(val) <= 1e-6]
        
        if significant_vars:
            st.markdown("**Variáveis Básicas (≠ 0):**")
            cols = st.columns(min(len(significant_vars), 4))
            for i, (var_name, value) in enumerate(significant_vars):
                with cols[i % len(cols)]:
                    if "x" in var_name:  # Variável de decisão
                        st.success(f"**{var_name}** = {value:.3f}")
                    else:  # Variável de folga
                        st.info(f"**{var_name}** = {value:.3f}")
        
        if zero_vars:
            zero_names = [name for name, _ in zero_vars]
            st.markdown(f"**Variáveis Básicas (= 0):** {', '.join(zero_names)}")


def extract_basis_variables(T, current_basis, n_original_vars):
    """
    Extrai informações das variáveis básicas do tableau.
    
    Args:
        T: Tableau atual (numpy array)
        current_basis: Lista de índices das variáveis básicas
        n_original_vars: Número de variáveis originais do problema
    
    Returns:
        Lista de tuplas (nome_variavel, valor)
    """
    basis_info = []
    
    for i, var_idx in enumerate(current_basis):
        # Determinar nome da variável
        if var_idx < n_original_vars:
            var_name = f"x{var_idx+1}"
        else:
            var_name = f"s{var_idx-n_original_vars+1}"
        
        # Obter valor da variável (RHS da linha correspondente)
        value = T[i+1, -1]  # i+1 porque a primeira linha é Z
        
        basis_info.append((var_name, value))
    
    return basis_info


def create_iteration_summary(iteration_num, entering_var, leaving_var, pivot_element, ratios_info):
    """
    Cria um resumo visual da iteração do Simplex.
    
    Args:
        iteration_num: Número da iteração
        entering_var: Variável que entra na base
        leaving_var: Variável que sai da base
        pivot_element: Valor do elemento pivot
        ratios_info: Lista de informações sobre as razões
    """
    st.markdown(f"### 🔄 Resumo da Iteração {iteration_num}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🔴 Variável que Sai**")
        st.info(leaving_var)
    
    with col2:
        st.markdown("**⚡ Elemento Pivot**")
        st.warning(f"{pivot_element:.3f}")
    
    with col3:
        st.markdown("**🟢 Variável que Entra**")
        st.success(entering_var)
    
    # Mostrar informações das razões diretamente (sem expander aninhado)
    if ratios_info:
        st.markdown("**📊 Detalhes do Teste da Razão:**")
        for ratio_info in ratios_info:
            st.write(f"• {ratio_info}")


def show_final_solution(solution, objective_value, basis_info=None, maximize=True, method="Simplex", iterations=0):
    """
    Mostra a solução final de forma organizada e destacada.
    
    Args:
        solution: Lista com valores das variáveis
        objective_value: Valor ótimo da função objetivo
        basis_info: Informações sobre as variáveis básicas (não usado mais na UI simplificada, mantido para compatibilidade)
        maximize: Se o problema é de maximização
        method: Nome do método utilizado
        iterations: Número total de iterações
    """
    # Linha única com: Valor Z | Método | Iterações
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label=f"**Valor {'Máximo' if maximize else 'Mínimo'} (Z)**",
            value=f"{objective_value:.3f}",
            delta=None
        )
        
    with col2:
        st.metric(label="**Método**", value=method)
        
    with col3:
        st.metric(label="**Iterações**", value=str(iterations))
        
    # Valores das variáveis
    st.markdown("### 📊 Valores das Variáveis")
    
    # Organizar em colunas para melhor visualização
    n_vars = len(solution)
    cols_per_row = min(4, n_vars)
    rows_needed = (n_vars + cols_per_row - 1) // cols_per_row
    
    for row in range(rows_needed):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            var_idx = row * cols_per_row + col_idx
            if var_idx < n_vars:
                with cols[col_idx]:
                    value = solution[var_idx]
                    # Destacar variáveis básicas (não-zero) em verde
                    if abs(value) > 1e-6:
                        st.success(f"**x{var_idx+1} = {value:.3f}**")
                    else:
                        st.info(f"x{var_idx+1} = {value:.3f}")


def show_optimization_summary(method="Simplex", iterations=0, status="Optimal"):
    """
    Mostra um resumo do processo de otimização.
    
    Args:
        method: Método utilizado (Simplex, Branch&Bound, etc.)
        iterations: Número de iterações realizadas
        status: Status final (Optimal, Unbounded, Infeasible, etc.)
    """
    st.markdown("### 📈 Resumo da Otimização")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("**Método**", method)
    
    with col2:
        st.metric("**Iterações**", iterations)
    
    with col3:
        # Escolher cor baseada no status
        if status == "Optimal":
            st.success(f"**Status:** {status}")
        elif status == "Unbounded":
            st.error(f"**Status:** {status}")
        elif status == "Infeasible":
            st.warning(f"**Status:** {status}")
        else:
            st.info(f"**Status:** {status}")


def analyze_tableau_basis(T, n_original_vars):
    """
    Analisa o tableau para identificar automaticamente as variáveis básicas.
    
    Args:
        T: Tableau atual
        n_original_vars: Número de variáveis originais
    
    Returns:
        Lista de tuplas (nome_variavel, valor) das variáveis básicas
    """
    basis_info = []
    rows, cols = T.shape
    
    # Para cada linha (exceto Z)
    for row_idx in range(1, rows):
        rhs_value = T[row_idx, -1]
        
        # Procurar coluna unitária nesta linha
        for col_idx in range(cols - 1):  # Excluir RHS
            col = T[:, col_idx]
            
            # Verificar se é coluna unitária (um 1, resto zeros)
            if (abs(col[row_idx] - 1.0) < 1e-6 and 
                np.sum(np.abs(col) > 1e-6) == 1):
                
                # Determinar nome da variável
                if col_idx < n_original_vars:
                    var_name = f"x{col_idx+1}"
                else:
                    var_name = f"s{col_idx-n_original_vars+1}"
                
                basis_info.append((var_name, rhs_value))
                break
        else:
            # Se não encontrou coluna unitária, usar índice genérico
            basis_info.append((f"R{row_idx}", rhs_value))
    
    return basis_info


def format_tableau_description(iteration_num, entering_var, leaving_var, ratios):
    """
    Formata a descrição de uma iteração do Simplex com markdown estruturado.
    
    Args:
        iteration_num: Número da iteração
        entering_var: Variável que entra
        leaving_var: Variável que sai
        ratios: Lista de razões calculadas
    
    Returns:
        String formatada em markdown
    """
    description = f"""
## 🔄 **ITERAÇÃO {iteration_num}**

### 1️⃣ **Seleção da Variável que Entra**
• **Critério:** Custo reduzido mais negativo
• **Variável escolhida:** **{entering_var}**

### 2️⃣ **Teste da Razão Mínima**
• **Objetivo:** Determinar qual variável sai da base
• **Razões calculadas:**
"""
    
    for i, ratio in enumerate(ratios):
        if ratio == float('inf'):
            description += f"  - Linha {i+1}: ∞ (entrada ≤ 0)\n"
        else:
            description += f"  - Linha {i+1}: {ratio:.3f}\n"
    
    description += f"""
### 3️⃣ **Seleção da Variável que Sai**
• **Menor razão positiva:** Linha com **{leaving_var}**
• **Motivo:** Evita violação das restrições

### 4️⃣ **Operação de Pivoteamento**
• **Resultado:** **{entering_var}** substitui **{leaving_var}** na base
"""
    
    return description