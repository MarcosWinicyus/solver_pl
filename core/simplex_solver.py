import math
from typing import List, Tuple

import numpy as np


class SimplexSolver:
    """Primal Simplex com log didático e explicações detalhadas.

    Corrigido:
    * Critério de otimalidade – usa tolerância 1e-8.
    * Seleção de linha‑pivot isolada em método _pivot_row para maior clareza.
    * Descrições mais didáticas dos passos e decisões.
    * Correção do bug que parava na primeira iteração.
    * Explicações detalhadas sobre entrada/saída da base.
    """

    def __init__(self) -> None:
        self.tableaux: List[np.ndarray] = []
        self.steps: List[str] = []
        self.decisions: List[str] = []
        self.pivots: List[Tuple[int, int]] = []
        self.optimal: bool = False
        self.unbounded: bool = False
        self._maximize: bool = True
        self._current_basis: List[int] = []

    # ------------------------------------------------------------------
    def solve(
        self,
        c: List[float],
        A: List[List[float]],
        b: List[float],
        maximize: bool = True,
        iteration_limit: int = 100,
    ) -> None:
        # Reset total
        self.__init__()
        self._maximize = maximize

        c_int = [-x for x in c] if maximize else list(c)
        m, n = len(A), len(c_int)
        T = np.zeros((m + 1, n + m + 1))
        T[0, :n] = c_int
        for i in range(m):
            T[i + 1, :n] = A[i]
            T[i + 1, n + i] = 1
            T[i + 1, -1] = b[i]

        # Base inicial: variáveis de folga
        basis = [n + i for i in range(m)]
        self._current_basis = basis.copy()

        # Criar descrição da base inicial
        basis_vars = [f"s{i+1}" for i in range(m)]
        initial_desc = (
            f"**Tableau Inicial Construído:**\n\n"
            f"• **{n} variáveis de decisão** (x₁, x₂, ..., x{n})\n"
            f"• **{m} variáveis de folga** (s₁, s₂, ..., s{m})\n\n"
            f"**Base Inicial:**\n"
            f"• Variáveis básicas: {', '.join(basis_vars)}\n"
            f"• Variáveis não-básicas: " + ", ".join([f"x{i+1}" for i in range(n)]) + " (todas = 0)\n\n"
            f"**Função Objetivo:**\n"
            f"• Tipo: {'Maximizar' if maximize else 'Minimizar'} Z\n"
            f"• Todas as variáveis de decisão iniciam fora da base"
        )

        self._log_state(T, "Tableau Inicial", initial_desc, (-1, -1))

        # Iterações do Simplex
        for it in range(1, iteration_limit + 1):
            # Verificar se é ótimo
            if self._is_optimal(T):
                current_basis_vars = []
                for idx in self._current_basis:
                    if idx < n:
                        current_basis_vars.append(f"x{idx+1}")
                    else:
                        current_basis_vars.append(f"s{idx-n+1}")
                
                optimal_desc = (
                    f"## ✅ SOLUÇÃO ÓTIMA ENCONTRADA!\n\n"
                    f"**Critério de Otimalidade Satisfeito:**\n"
                    f"• Todos os custos reduzidos são ≥ 0\n"
                    f"• Não há mais possibilidade de melhoria\n\n"
                    f"**Base Final:**\n"
                    f"• Variáveis básicas: {', '.join(current_basis_vars)}\n\n"
                    f"**Interpretação:**\n"
                    f"• O algoritmo convergiu para a solução ótima\n"
                    f"• Esta é a melhor solução possível para o problema"
                )
                self._log_state(T, "Solução Ótima", optimal_desc, (-1, -1))
                self.optimal = True
                break

            # Encontrar coluna pivot (variável que entra na base)
            pc = self._pivot_col(T)
            entering_var = f"x{pc+1}"
            
            # Encontrar linha pivot (variável que sai da base)
            pr = self._pivot_row(T, pc)
            if pr == -1:  # coluna sem entradas positivas ⇒ ilimitado
                unbounded_desc = (
                    f"## ❌ PROBLEMA ILIMITADO!\n\n"
                    f"**Diagnóstico:**\n"
                    f"• A variável **{entering_var}** pode crescer infinitamente\n"
                    f"• Todas as entradas da coluna {pc+1} são ≤ 0\n"
                    f"• Não existe limite superior para a função objetivo\n\n"
                    f"**Significado:**\n"
                    f"• O problema não possui solução ótima finita\n"
                    f"• A região factível é ilimitada na direção de crescimento"
                )
                self._log_state(T, "Problema Ilimitado", unbounded_desc, (-1, -1))
                self.unbounded = True
                return

            # Identificar variável que sai da base
            leaving_var_idx = self._current_basis[pr-1]
            if leaving_var_idx < n:
                leaving_var = f"x{leaving_var_idx+1}"
            else:
                leaving_var = f"s{leaving_var_idx-n+1}"

            # Calcular razões para explicação
            ratios = []
            ratio_explanations = []
            for i in range(1, m + 1):
                if T[i, pc] > 1e-10:
                    ratio = T[i, -1] / T[i, pc]
                    ratios.append(ratio)
                    var_idx = self._current_basis[i-1]
                    if var_idx < n:
                        var_name = f"x{var_idx+1}"
                    else:
                        var_name = f"s{var_idx-n+1}"
                    ratio_explanations.append(f"**Linha {i}** ({var_name}): {T[i, -1]:.3f} ÷ {T[i, pc]:.3f} = **{ratio:.3f}**")
                else:
                    ratios.append(math.inf)
                    var_idx = self._current_basis[i-1]
                    if var_idx < n:
                        var_name = f"x{var_idx+1}"
                    else:
                        var_name = f"s{var_idx-n+1}"
                    ratio_explanations.append(f"**Linha {i}** ({var_name}): ∞ (entrada ≤ 0)")

            min_ratio = min(ratios)
            min_ratio_line = ratios.index(min_ratio) + 1

            # Criar descrição detalhada da iteração
            iteration_desc = (
                f"## 🔄 ITERAÇÃO {it}\n\n"
                f"### 1️⃣ SELEÇÃO DA VARIÁVEL QUE ENTRA\n\n"
                f"**Critério:** Procuramos o custo reduzido mais negativo na linha Z\n\n"
                f"• **Coluna selecionada:** {pc+1} (variável **{entering_var}**)\n"
                f"• **Custo reduzido:** {T[0, pc]:.3f}\n"
                f"• **Decisão:** **{entering_var}** entra na base\n\n"
                f"---\n\n"
                f"### 2️⃣ TESTE DA RAZÃO MÍNIMA\n\n"
                f"**Objetivo:** Determinar qual variável deve sair da base\n\n"
                f"**Cálculo:** RHS ÷ elemento_coluna (apenas para elementos > 0)\n\n"
                + "\n".join([f"• {exp}" for exp in ratio_explanations]) + "\n\n"
                f"---\n\n"
                f"### 3️⃣ SELEÇÃO DA VARIÁVEL QUE SAI\n\n"
                f"• **Menor razão positiva:** {min_ratio:.3f} (linha {min_ratio_line})\n"
                f"• **Variável que sai:** **{leaving_var}**\n"
                f"• **Motivo:** Evita violação de restrições de não-negatividade\n\n"
                f"---\n\n"
                f"### 4️⃣ OPERAÇÃO DE PIVOTEAMENTO\n\n"
                f"• **Elemento pivot:** T[{pr}][{pc+1}] = **{T[pr, pc]:.3f}**\n"
                f"• **Operação 1:** Dividir linha {pr} pelo elemento pivot\n"
                f"• **Operação 2:** Zerar outras entradas da coluna {pc+1}\n"
                f"• **Resultado:** Nova base com **{entering_var}** no lugar de **{leaving_var}**"
            )

            # Realizar pivotamento
            T = self._pivot(T, pr, pc)
            self._current_basis[pr - 1] = pc
            
            self._log_state(T, f"Iteração {it}", iteration_desc, (pr, pc))
        
        else:  # loop não quebrou
            timeout_desc = (
                f"## ⏰ LIMITE DE ITERAÇÕES ATINGIDO\n\n"
                f"**Status:** O algoritmo foi interrompido após {iteration_limit} iterações\n\n"
                f"**Possíveis Causas:**\n"
                f"• Problema de ciclagem (degeneração)\n"
                f"• Problema mal condicionado\n"
                f"• Erro numérico acumulado\n\n"
                f"**Recomendação:** Verificar os dados de entrada do problema"
            )
            self.steps.append("Limite de Iterações")
            self.decisions.append(timeout_desc)
            self.pivots.append((-1, -1))
            self.tableaux.append(T.copy())

    # ------------------------------------------------------------------ auxiliares
    def _log_state(self, tableau, step, decision, pivot):
        """Armazena sincronicamente nas quatro listas."""
        self.tableaux.append(tableau.copy())
        self.steps.append(step)
        self.decisions.append(decision)
        self.pivots.append(pivot)

    @staticmethod
    def _is_optimal(T):
        """Verifica se todos os custos reduzidos são não-negativos."""
        return np.all(T[0, :-1] >= -1e-8)

    @staticmethod
    def _pivot_col(T):
        """Encontra a coluna com o custo reduzido mais negativo."""
        negative_costs = T[0, :-1] < -1e-8
        if not np.any(negative_costs):
            return -1
        return int(np.where(negative_costs)[0][0])

    @staticmethod
    def _pivot_row(T, pc):
        """Encontra a linha pivot usando o teste da razão mínima."""
        rows = []
        for i in range(1, T.shape[0]):
            if T[i, pc] > 1e-10:  # Apenas entradas positivas
                ratio = T[i, -1] / T[i, pc]
                if ratio >= 0:  # Apenas razões não-negativas
                    rows.append((ratio, i))
        
        if not rows:
            return -1  # Problema ilimitado
        
        # Retorna a linha com menor razão (desempate por menor índice)
        return min(rows, key=lambda x: (x[0], x[1]))[1]

    @staticmethod
    def _pivot(T, pr, pc):
        """Realiza as operações de pivot no tableau."""
        T2 = T.astype(float).copy()
        
        # Normalizar linha pivot
        pivot_element = T[pr, pc]
        T2[pr] = T[pr] / pivot_element
        
        # Eliminar outras entradas da coluna pivot
        for i in range(T.shape[0]):
            if i != pr:
                multiplier = T[i, pc]
                T2[i] = T[i] - multiplier * T2[pr]
        
        return T2

    def get_solution(self):
        """Extrai a solução ótima do tableau final."""
        if not self.optimal:
            return None
            
        T = self.tableaux[-1]
        n_vars = T.shape[1] - T.shape[0]  # número de variáveis originais
        sol = [0.0] * n_vars
        
        # Encontrar valores das variáveis básicas
        for j in range(n_vars):
            col = T[:, j]
            # Procurar por coluna unitária (uma entrada = 1, outras = 0)
            ones = np.isclose(col, 1, atol=1e-8)
            zeros = np.isclose(col, 0, atol=1e-8)
            
            if ones.sum() == 1 and zeros.sum() == T.shape[0] - 1:
                row_idx = int(np.where(ones)[0][0])
                sol[j] = T[row_idx, -1]
        
        # Valor da função objetivo
        z = T[0, -1]
        if self._maximize:
            z = -z  # Converter de volta para maximização
            
        return sol, z

    def get_basis_info(self):
        """Retorna informações sobre a base atual."""
        if not self.optimal:
            return None
            
        T = self.tableaux[-1]
        n_vars = T.shape[1] - T.shape[0]
        basis_info = []
        
        for i, var_idx in enumerate(self._current_basis):
            if var_idx < n_vars:
                var_name = f"x{var_idx+1}"
            else:
                var_name = f"s{var_idx-n_vars+1}"
            
            value = T[i+1, -1]
            basis_info.append((var_name, value))
        
        return basis_info

    def get_current_basis_names(self, n_original_vars):
        """Retorna os nomes das variáveis básicas atuais."""
        basis_names = []
        for var_idx in self._current_basis:
            if var_idx < n_original_vars:
                basis_names.append(f"x{var_idx+1}")
            else:
                basis_names.append(f"s{var_idx-n_original_vars+1}")
        return basis_names