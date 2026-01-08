import streamlit as st
import json
from typing import Dict, Any

def history_page():
    st.markdown("<h1 style='text-align: center;'>🕑 Histórico de Problemas</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- Ações (Top Bar) ---
    col_act1, col_act2 = st.columns(2)
    
    with col_act1:
        # Exportar
        history = st.session_state.get("history", [])
        st.download_button(
            label="⬇️ Baixar Histórico (JSON)",
            data=json.dumps(history, indent=2),
            file_name="historico_otimizacao.json",
            mime="application/json",
            use_container_width=True,
            disabled=len(history) == 0
        )

    with col_act2:
        # Importar (dentro de um popover/expander discreto)
        with st.expander("📤 Importar (Upload)"):
            uploaded_file = st.file_uploader("Selecione arquivo JSON", type=["json"], label_visibility="collapsed")
            if uploaded_file is not None:
                try:
                    data = json.load(uploaded_file)
                    if isinstance(data, list):
                        st.session_state.setdefault("history", []).extend(data)
                        st.toast(f"✅ {len(data)} itens importados!", icon="📥")
                        st.rerun() # Refresh imediato
                    else:
                        st.error("Formato inválido.")
                except Exception as e:
                    st.error(f"Erro: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Listagem de Histórico ---
    if not history:
        st.info("📝 Nenhum problema resolvido nesta sessão.")
        return

    # CSS para alinhar botão
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] {
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    for idx, item in enumerate(reversed(history)):
        real_idx = len(history) - 1 - idx
        
        # Dados para exibição
        method = item.get("method", "Desconhecido")
        z_val = item.get("z")
        z_str = f"{z_val:.4f}" if isinstance(z_val, (int, float)) else "N/A"
        icon = "📐" if "Simplex" in method else "🌳"
        
        with st.container():
             col_main, col_btn = st.columns([0.85, 0.15])
             
             with col_main:
                 with st.expander(f"{icon} Problema #{real_idx + 1} — Z = {z_str}"):
                     st.caption(f"**Método:** {method}")
                     
                     c_desc, c_json = st.columns(2)
                     with c_desc:
                         n_vars = len(item.get("c", []))
                         n_cons = len(item.get("A", []))
                         st.markdown(f"**Dimensões:**\n- {n_vars} Variáveis\n- {n_cons} Restrições")
                         st.markdown(f"**Objetivo:** {'Maximizar' if item.get('maximize', True) else 'Minimizar'}")
                     
                     with c_json:
                         st.markdown("**Modelagem Matemática:**")
                         
                         # Extrair dados
                         c = item.get("c", [])
                         A = item.get("A", [])
                         b = item.get("b", [])
                         is_max = item.get("maximize", True)
                         
                         # Função Objetivo
                         obj_str = " + ".join([f"{val}x_{j+1}" for j, val in enumerate(c)])
                         st.latex(f"{'Max' if is_max else 'Min'} \ Z = {obj_str}")
                         
                         # Restrições
                         st.markdown("Sujeito a:")
                         for r_idx, row in enumerate(A):
                             lhs = " + ".join([f"{val}x_{j+1}" for j, val in enumerate(row)])
                             rhs = b[r_idx]
                             # Tentar inferir o sinal se salvo (futuro), por enquanto assume <= padrão do Simplex
                             # mas o histórico salva A e b. Se veio do B&B pode ter = ou >=. 
                             # O histórico simples atual salva A já convertido? 
                             # O SimplexSolver salva A original se passado, mas aqui salvamos "c", "A", "b" dict.
                             # Vamos assumir <= para visualização histórica básica ou usar genericamente
                             st.latex(f"{lhs} \le {rhs}")
                         
                         st.latex("x_j \ge 0")

             with col_btn:
                 if st.button("🔄 Carregar", key=f"load_hist_{real_idx}", help=f"Restaurar Problema #{real_idx + 1}"):
                     _load_history_item(item)
        
        # Espaçamento leve entre itens (sem divider)
        st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)

def _load_history_item(item: Dict[str, Any]):
    """Carrega um item do histórico para o solver."""
    
    # Preparar dados para o formato de 'problem'
    problem_data = {
        "c": item.get("c"),
        "A": item.get("A"),
        "b": item.get("b"),
        "maximize": item.get("maximize", True), # Default True se não existir
        "int_vars": item.get("integer_vars", [])
    }
    
    st.session_state["problem"] = problem_data
    
    # Determinar página alvo
    target = "📐 Método Simplex"
    if "Branch" in item.get("method", ""):
        target = "🌳 Branch & Bound"
        
    st.session_state["pending_redirect"] = target
    
    st.toast(f"Problema #{item.get('method')} carregado! Redirecionando...", icon="🚀")
    st.rerun()