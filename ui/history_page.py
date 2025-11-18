import streamlit as st
import json
from typing import Dict, Any

def history_page():
    st.header("🕑 Histórico de Problemas")
    
    # --- Importar Histórico ---
    with st.expander("📤 Importar Histórico (JSON)"):
        uploaded_file = st.file_uploader("Carregar arquivo JSON", type=["json"])
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                if isinstance(data, list):
                    # Mesclar ou substituir? Vamos adicionar.
                    st.session_state.setdefault("history", []).extend(data)
                    st.success(f"✅ {len(data)} itens importados com sucesso!")
                else:
                    st.error("❌ O arquivo JSON deve conter uma lista de problemas.")
            except Exception as e:
                st.error(f"❌ Erro ao ler arquivo: {e}")

    # --- Exibir e Exportar Histórico ---
    history = st.session_state.get("history", [])
    
    if not history:
        st.info("📝 Nenhum problema resolvido nesta sessão.")
        return

    # Botão de Download no topo
    st.download_button(
        label="⬇️ Baixar Histórico Completo (JSON)",
        data=json.dumps(history, indent=2),
        file_name="historico_otimizacao.json",
        mime="application/json",
    )
    
    st.divider()

    # Listar itens (do mais recente para o mais antigo)
    for idx, item in enumerate(reversed(history)):
        real_idx = len(history) - 1 - idx
        
        # Determinar título e ícone
        method = item.get("method", "Desconhecido")
        z_val = item.get("z")
        z_str = f"{z_val:.4f}" if isinstance(z_val, (int, float)) else "N/A"
        
        icon = "📐" if "Simplex" in method else "🌳"
        
        with st.container():
            col_info, col_action = st.columns([4, 1])
            
            with col_info:
                st.subheader(f"{icon} Problema #{real_idx + 1}")
                st.caption(f"**Método:** {method} | **Z:** {z_str}")
                
                # Detalhes resumidos
                n_vars = len(item.get("c", []))
                n_cons = len(item.get("A", []))
                st.text(f"Variáveis: {n_vars} | Restrições: {n_cons}")
                
                with st.expander("Ver Detalhes JSON"):
                    st.json(item)

            with col_action:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔄 Carregar", key=f"load_hist_{real_idx}"):
                    _load_history_item(item)
            
            st.divider()

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