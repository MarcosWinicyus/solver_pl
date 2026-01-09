# Sistema de Otimização Visual 📊

## Sobre o Projeto

O **Sistema de Otimização Visual** (Solver PL) é uma plataforma interativa e didática desenvolvida para auxiliar no ensino e aprendizagem de Pesquisa Operacional. Ele foca na resolução e visualização de problemas de **Programação Linear (PL)** e **Programação Inteira (PLI)**.

Construído com **Python** e **Streamlit**, o sistema oferece visualizações ricas (gráficos 2D/3D, árvores de decisão, tableaux passo a passo) para tornar conceitos matemáticos abstratos em experiências tangíveis.

---

## 🚀 Funcionalidades Principais

### 📐 Simplex
- **Resolução Passo a Passo:** Acompanhe cada iteração do algoritmo Simplex.
- **Visualização 3D/2D:** Gráficos interativos da região factível com identificação de vértices e caminho da solução.
- **Tableau Interativo:** Exibição detalhada das variáveis básicas, não.básicas e operações de pivoteamento.
- **Identificação de Casos:** Detecta soluções ótimas, múltiplas soluções, problemas ilimitados e inviáveis.

### 🌐 Internacionalização (Multi-Idioma)
O projeto suporta múltiplos idiomas via arquivos JSON.
- **Idiomas Suportados:** Português (pt), Inglês (en), Espanhol (es).
- **Contribuição:** Para adicionar um novo idioma, basta criar um arquivo `.json` em `ui/locales/` (ex: `fr.json`) espelhando a estrutura de `en.json` e submeter um Pull Request. O sistema detectará automaticamente.

### 🌳 Branch & Bound
- **Programação Inteira:** Algoritmo completo para resolver PLI.
- **Árvore de Decisão Visual:** Grafo interativo gerado em tempo real mostrando nós, podas (bound, integridade, inviabilidade) e ramificações.
- **Estratégias de Busca:** Suporte a BFS, DFS e Best-Bound.

### 🛠️ Ferramentas de Análise
- **🔄 Conversor Primal-Dual:** Transforme problemas instantaneamente e resolva o Dual.
- **📊 Análise de Sensibilidade:** Calcule preços sombra (Shadow Prices) e intervalos de estabilidade para coeficientes da função objetivo ($c_j$) e restrições ($b_i$).
- **📝 Forma Padrão:** Conversor automático para a forma canônica (Maximização, Igualdades, RHS $\ge$ 0) com passo a passo didático.

### 📚 Recursos Adicionais
- **Biblioteca de Problemas:** Acervo com problemas clássicos (Dieta, Mochila, Mix de Produção) prontos para teste.
- **Histórico de Sessão:** Seus problemas resolvidos ficam salvos automaticamente para comparação e revisão.

---

## 🛠️ Tecnologias

- **Frontend:** [Streamlit](https://streamlit.io/)
- **Cálculo Numérico:** [NumPy](https://numpy.org/) e [Pandas](https://pandas.pydata.org/)
- **Visualização:** [Plotly](https://plotly.com/) (Gráficos) e [St-Link-Analysis](https://github.com/Altxator/st-link-analysis) (Grafos/Árvores)

---

## ⚡ Como Executar

### Pré-requisitos
- Python 3.8+

### Passo a Passo

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositorio>
   cd solver_pl
   ```

2. **Crie um ambiente virtual**
   ```bash
   # MacOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   
   # Windows
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute a aplicação**
   ```bash
   streamlit run app.py
   ```

---

## 📂 Estrutura do Projeto

```
solver_pl/
├── app.py                  # Entrypoint principal (Navegação)
├── core/                   # Lógica matemática (Solvers)
│   ├── simplex_solver.py       # Simplex Primal
│   ├── branch_bound_solver.py  # Branch & Bound
├── ui/                     # Interface do Usuário (Páginas)
│   ├── home_page.py            # Dashboard Principal
│   ├── simplex_page.py         # UI Simplex
│   ├── branch_and_bound_page.py# UI Branch & Bound
│   ├── sensitivity_page.py     # Análise de Sensibilidade
│   ├── Standard_form_page.py   # Conversor Forma Padrão
│   ├── duality_page.py         # Conversor Dual
│   ├── library_page.py         # Biblioteca de Problemas
│   └── plots.py                # Geração de Gráficos 2D/3D
```

---

*Desenvolvido com ❤️ para fins educacionais - v0.5 (Janeiro 2026)*
