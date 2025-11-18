import streamlit as st

# Importações das interfaces
from ui.home_page import home_page
from ui.library_page import library_page
from ui.history_page import history_page
from ui.simplex_page import simplex_ui
from ui.branch_and_bound_page import bab_ui

# Configuração da página
st.set_page_config(
    page_title="Sistema de Otimização Visual",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Lógica de redirecionamento (deve vir antes dos widgets)
if "pending_redirect" in st.session_state:
    st.session_state["navigation"] = st.session_state["pending_redirect"]
    del st.session_state["pending_redirect"]

# CSS customizado para melhorar a aparência
st.markdown("""
<style>
    /* Destacar botões principais */
    .stButton > button[kind="primary"] {
        background: linear-gradient(45deg, #1f77b4, #17a2b8);
        border: none;
        font-weight: bold;
        padding: 0.75rem 2rem;
    }
</style>
""", unsafe_allow_html=True)



# Definição das páginas
PAGES = {
    "🏠 Home": home_page,
    "📚 Biblioteca de Problemas": library_page,
    "📐 Método Simplex": simplex_ui,
    "🌳 Branch & Bound": bab_ui,
    "🕑 Histórico": history_page
}

# Header principal
# st.markdown('<div class="main-header">', unsafe_allow_html=True)
# st.title("📊 Sistema de Otimização Visual")
# st.markdown("*Plataforma interativa para aprendizado e resolução de problemas de Programação Linear*")
# st.markdown('</div>', unsafe_allow_html=True)

# Sidebar para navegação
st.sidebar.title("📊 Sistema de Otimização Visual")
st.sidebar.markdown("*Plataforma Open Source interativa para aprendizado e resolução de problemas de Programação Linear*")
st.sidebar.markdown("---")

# Escolha da seção
choice = st.sidebar.radio(
    "Escolha a seção:",
    list(PAGES.keys()),
    format_func=lambda x: x,
    help="Selecione o módulo que deseja utilizar",
    key="navigation"
)

# Informações na sidebar
st.sidebar.markdown("---")
# st.sidebar.markdown("### ℹ️ Informações")
# st.sidebar.info(
#     "**Sistema desenvolvido para:**\n"
#     "- Aprendizado didático\n"
#     "- Resolução de problemas de PL\n"
#     "- Visualização de algoritmos\n"
#     "- Análise de resultados"
# )

# Status da sessão
if "history" in st.session_state and st.session_state["history"]:
    num_problems = len(st.session_state["history"])
    st.sidebar.success(f"✅ {num_problems} problema(s) resolvido(s) nesta sessão")
else:
    st.sidebar.warning("📝 Nenhum problema resolvido ainda")

# Limpar histórico
if st.sidebar.button("🗑️ Limpar Histórico", help="Remove todos os problemas salvos"):
    if "history" in st.session_state:
        st.session_state["history"] = []
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 Versão")
st.sidebar.text("v0.3 - Outubro 2025")

# Executar a página selecionada
try:
    PAGES[choice]()
except Exception as e:
    st.error(f"❌ Erro ao carregar a página: {str(e)}")
    st.exception(e)
    st.info("💡 Tente recarregar a página ou selecionar outra seção.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    "Sistema de Otimização Visual - Desenvolvido para fins educacionais"
    "</div>",
    unsafe_allow_html=True
)