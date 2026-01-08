import streamlit as st

# Configuração da página deve ser a primeira chamada
st.set_page_config(
    page_title="Sistema de Otimização Visual",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Importações das interfaces
from ui.home_page import home_page
from ui.library_page import library_page
from ui.history_page import history_page
from ui.simplex_page import simplex_ui
from ui.branch_and_bound_page import bab_ui
from ui.sensitivity_page import sensitivity_ui
from ui.duality_page import duality_ui

from ui.standard_form_page import standard_form_ui

# CSS customizado Global
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

# --- Definição das Páginas (st.Page) ---

# Principal
p_home = st.Page(home_page, title="Home", icon="🏠")
p_library = st.Page(library_page, title="Biblioteca de Problemas", icon="📚")
p_history = st.Page(history_page, title="Histórico", icon="🕑")

# Solvers
p_simplex = st.Page(simplex_ui, title="Método Simplex", icon="📐")
p_bab = st.Page(bab_ui, title="Branch & Bound", icon="🌳")

# Ferramentas
p_duality = st.Page(duality_ui, title="Dualidade (Primal-Dual)", icon="🔄")
p_sensitivity = st.Page(sensitivity_ui, title="Análise de Sensibilidade", icon="📊")
p_std_form = st.Page(standard_form_ui, title="Forma Padrão", icon="📝")

# Navegação Organizada
pg = st.navigation({
    "": [p_home, p_library, p_history],
    "Solvers": [p_simplex, p_bab],
    "Ferramentas": [p_duality, p_sensitivity, p_std_form],
}, position="top")

# --- Lógica de Redirecionamento (Compatibilidade) ---
# Mapeia as strings antigas usadas em library_page.py e duality_page.py para os objetos st.Page
REDIRECT_MAP = {
    "📐 Método Simplex": p_simplex,
    "🌳 Branch & Bound": p_bab,
    "Simplex": p_simplex,
    "Branch & Bound": p_bab
}

if "pending_redirect" in st.session_state:
    target = st.session_state["pending_redirect"]
    del st.session_state["pending_redirect"]
    
    if target in REDIRECT_MAP:
        st.switch_page(REDIRECT_MAP[target])
    else:
        # Tenta achar por título exato se não estiver no mapa
        pass

# Executar a navegação
pg.run()