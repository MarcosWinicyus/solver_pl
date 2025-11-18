# Sistema de Otimização Visual 📊

## Sobre o Projeto

O **Sistema de Otimização Visual** é uma plataforma interativa e educacional desenvolvida para auxiliar no aprendizado e resolução de problemas de Programação Linear (PL) e Programação Inteira.

Construído com Python e Streamlit, o sistema oferece uma interface amigável para modelar, resolver e visualizar problemas de otimização, tornando conceitos complexos mais acessíveis para estudantes e profissionais.

## Funcionalidades Principais

### 📐 Método Simplex
- Resolução passo a passo de problemas de Programação Linear.
- Visualização das iterações e do Tableau Simplex.
- Identificação de soluções ótimas, múltiplas soluções, soluções ilimitadas e problemas inviáveis.

### 🌳 Branch & Bound
- Resolução de problemas de Programação Linear Inteira.
- Visualização da árvore de decisão do algoritmo Branch & Bound.
- Acompanhamento das podas e ramificações para encontrar a solução inteira ótima.

### 🕑 Histórico de Sessão
- Registro automático dos problemas resolvidos durante a sessão.
- Possibilidade de revisar resoluções anteriores.

## Tecnologias Utilizadas

- **[Streamlit](https://streamlit.io/)**: Framework para criação da interface web interativa.
- **[NumPy](https://numpy.org/)**: Computação numérica e manipulação de arrays.
- **[Pandas](https://pandas.pydata.org/)**: Estruturação e manipulação de dados.
- **[Plotly](https://plotly.com/)**: Criação de gráficos interativos e visualizações.

## Como Executar

1.  **Clone o repositório**
    ```bash
    git clone <url-do-repositorio>
    cd solver_pl
    ```

2.  **Crie e ative um ambiente virtual (recomendado)**
    ```bash
    python -m venv .venv
    # No Windows:
    .venv\Scripts\activate
    # No Linux/Mac:
    source .venv/bin/activate
    ```

3.  **Instale as dependências**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação**
    ```bash
    streamlit run app.py
    ```

## Estrutura do Projeto

- `app.py`: Ponto de entrada da aplicação e configuração principal.
- `core/`: Contém a lógica dos algoritmos de otimização.
    - `simplex_solver.py`: Implementação do Método Simplex.
    - `branch_bound_solver.py`: Implementação do algoritmo Branch & Bound.
- `ui/`: Componentes da interface do usuário.
    - `simplex_page.py`: Interface para o solver Simplex.
    - `branch_and_bound_page.py`: Interface para o solver Branch & Bound.
    - `history_page.py`: Página de histórico.
    - `plots.py` e `tableau_display.py`: Auxiliares para visualização.

## Objetivo

Este projeto tem como objetivo principal servir como uma ferramenta didática, permitindo que usuários não apenas obtenham respostas para seus problemas de otimização, mas também compreendam o processo de resolução através de visualizações claras e detalhadas.

---
*Desenvolvido para fins educacionais - v0.3 (Outubro 2025)*
