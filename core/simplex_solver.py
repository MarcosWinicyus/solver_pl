import math
from typing import List, Tuple

import numpy as np


class SimplexSolver:
    """Primal Simplex com método Big-M para lidar com bases iniciais inviáveis.
    
    Melhorias:
    * Suporte a RHS negativo (converte para restrição >= e usa variáveis artificiais).
    * Método Big-M para penalizar variáveis artificiais.
    * Logs detalhados mantidos e adaptados para novas variáveis.
    """

    def __init__(self) -> None:
        self.tableaux: List[np.ndarray] = []
        self.steps: List[str] = []
        self.decisions: List[str] = []
        self.pivots: List[Tuple[int, int]] = []
        self.optimal: bool = False
        self.unbounded: bool = False
        self.infeasible: bool = False
        self._maximize: bool = True
        self._current_basis: List[int] = []
        self._variable_names: List[str] = []
        self._artificial_indices: List[int] = []

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
        
        M = 1e6  # Penalidade Big-M

        # Ajustar função objetivo para minimização interna (padrão do tableau)
        # Se Max Z, tableau usa linha -Z + cx = 0 -> Z - cx = 0.
        # Aqui vamos manter a convenção: Row 0 representa a equação da função objetivo.
        # Para Max Z = cx, queremos Z - cx = 0.
        # Para Min Z = cx, queremos Z - cx = 0 (mas vamos trabalhar com Max -Z).
        
        # Simplificação: Vamos trabalhar sempre maximizando.
        # Se o usuário quer minimizar, invertemos c no final.
        
        # Vetor c interno:
        # Se Maximize: coeficientes positivos no vetor c significam que queremos aumentá-los.
        # No tableau (formato Z - cx = 0), os coeficientes aparecem com sinal trocado.
        # Ex: Max Z = 2x1 + 3x2 -> Z - 2x1 - 3x2 = 0.
        # T[0] = [-2, -3, ...]
        
        c_input = np.array(c, dtype=float)
        if not maximize:
            c_input = -c_input
            
        # Converter para lista para manipulação
        c_list = list(c_input)
        
        m = len(A)
        n = len(c)
        
        # Identificar restrições que precisam de artificiais (b < 0)
        # Se Ax <= b e b < 0 -> -Ax >= -b (b torna-se positivo)
        # Adiciona surplus (-1) e artificial (+1)
        
        constraints_info = [] # (coeffs, rhs, type)
        
        n_slack = 0
        n_surplus = 0
        n_artificial = 0
        
        for i in range(m):
            row = list(A[i])
            rhs = b[i]
            
            if rhs < 0:
                # Converter para >= com RHS positivo
                row = [-x for x in row]
                rhs = -rhs
                constraints_info.append({
                    "coeffs": row,
                    "rhs": rhs,
                    "type": "ge", # >=
                    "slack_idx": -1,
                    "art_idx": -1
                })
                n_surplus += 1
                n_artificial += 1
            else:
                # Mantém <=
                constraints_info.append({
                    "coeffs": row,
                    "rhs": rhs,
                    "type": "le", # <=
                    "slack_idx": -1,
                    "art_idx": -1
                })
                n_slack += 1

        # Construir colunas
        # Ordem: [x1...xn] [s1...s_total] [a1...a_total]
        
        total_vars = n + n_slack + n_surplus + n_artificial
        T = np.zeros((m + 1, total_vars + 1))
        
        # Nomes das variáveis
        self._variable_names = [f"x{i+1}" for i in range(n)]
        
        # Mapear índices
        current_col = n
        
        # Adicionar Slacks/Surplus
        for i in range(m):
            info = constraints_info[i]
            if info["type"] == "le":
                info["slack_idx"] = current_col
                self._variable_names.append(f"s{i+1}")
                current_col += 1
            else:
                info["slack_idx"] = current_col
                self._variable_names.append(f"e{i+1}") # e para excesso/surplus
                current_col += 1
                
        # Adicionar Artificiais
        for i in range(m):
            info = constraints_info[i]
            if info["type"] == "ge":
                info["art_idx"] = current_col
                self._variable_names.append(f"a{i+1}")
                self._artificial_indices.append(current_col)
                current_col += 1
                
        # Preencher Tableau
        # Linha 0 (Objetivo): -c_j
        for j in range(n):
            T[0, j] = -c_list[j]
            
        # Penalidade M para artificiais na função objetivo (Max Z = cx - M*a)
        # No tableau: Z - cx + M*a = 0 -> Coeff de a é +M
        for idx in self._artificial_indices:
            T[0, idx] = M
            
        # Preencher restrições
        basis = []
        
        for i in range(m):
            info = constraints_info[i]
            row_idx = i + 1
            
            # Coeficientes de x
            for j in range(n):
                T[row_idx, j] = info["coeffs"][j]
                
            # RHS
            T[row_idx, -1] = info["rhs"]
            
            # Slack/Surplus
            if info["type"] == "le":
                T[row_idx, info["slack_idx"]] = 1
                basis.append(info["slack_idx"])
            else:
                T[row_idx, info["slack_idx"]] = -1
                # Artificial
                T[row_idx, info["art_idx"]] = 1
                basis.append(info["art_idx"])
                
        self._current_basis = basis.copy()
        
        # Ajustar Linha 0 para zerar custos das variáveis básicas artificiais
        # Row0 = Row0 - M * Row_i
        for i in range(m):
            info = constraints_info[i]
            if info["type"] == "ge":
                # Esta linha tem variável artificial na base
                T[0] = T[0] - M * T[i+1]
                
        # Log Inicial
        basis_vars_names = [self._variable_names[i] for i in basis]
        initial_desc = (
            f"**Tableau Inicial (Método Big-M):**\n\n"
            f"• **Variáveis:** {', '.join(self._variable_names)}\n"
            f"• **Base Inicial:** {', '.join(basis_vars_names)}\n"
            f"• **Penalidade M:** {M}\n\n"
            f"**Ajustes Realizados:**\n"
            f"• Restrições com RHS negativo foram convertidas.\n"
            f"• Variáveis artificiais adicionadas onde necessário."
        )
        self._log_state(T, "Início Big-M", initial_desc, (-1, -1))
        
        # Loop Simplex
        for it in range(1, iteration_limit + 1):
            if self._is_optimal(T):
                # Verificar inviabilidade (variável artificial na base com valor > 0)
                if self._check_infeasibility(T):
                    infeasible_desc = (
                        "## ❌ PROBLEMA INVIÁVEL\n\n"
                        "O algoritmo convergiu, mas variáveis artificiais permanecem na base com valor positivo.\n"
                        "Isso indica que não existe solução que satisfaça todas as restrições."
                    )
                    self._log_state(T, "Inviável", infeasible_desc, (-1, -1))
                    self.infeasible = True
                    return

                self.optimal = True
                self._log_success(T)
                return

            pc = self._pivot_col(T)
            pr = self._pivot_row(T, pc)
            
            if pr == -1:
                self.unbounded = True
                self._log_unbounded(T, pc)
                return
                
            # Executar pivot
            self._log_iteration(T, it, pr, pc)
            T = self._pivot(T, pr, pc)
            self._current_basis[pr - 1] = pc
            
        # Limite atingido
        self._log_timeout(T, iteration_limit)

    # ------------------------------------------------------------------
    
    def _log_iteration(self, T, it, pr, pc):
        entering = self._variable_names[pc]
        leaving = self._variable_names[self._current_basis[pr-1]]
        
        desc = (
            f"## 🔄 ITERAÇÃO {it}\n\n"
            f"• **Entra:** {entering} (Custo reduzido: {T[0, pc]:.2f})\n"
            f"• **Sai:** {leaving}\n"
            f"• **Pivot:** Linha {pr}, Coluna {pc+1}"
        )
        self._log_state(T, f"Iteração {it}", desc, (pr, pc))

    def _log_success(self, T):
        basis_names = [self._variable_names[i] for i in self._current_basis]
        desc = (
            f"## ✅ SOLUÇÃO ÓTIMA!\n\n"
            f"**Base Final:** {', '.join(basis_names)}\n"
            f"**Valor da Função Objetivo:** {abs(T[0, -1]):.4f}"
        )
        self._log_state(T, "Ótimo Encontrado", desc, (-1, -1))

    def _log_unbounded(self, T, pc):
        var = self._variable_names[pc]
        desc = f"## ❌ ILIMITADO\n\nA variável **{var}** pode crescer indefinidamente."
        self._log_state(T, "Ilimitado", desc, (-1, -1))
        
    def _log_timeout(self, T, limit):
        self._log_state(T, "Timeout", f"Limite de {limit} iterações atingido.", (-1, -1))

    def _log_state(self, tableau, step, decision, pivot):
        self.tableaux.append(tableau.copy())
        self.steps.append(step)
        self.decisions.append(decision)
        self.pivots.append(pivot)

    def _check_infeasibility(self, T):
        # Verifica se alguma variável artificial está na base com valor > tolerância
        for i, var_idx in enumerate(self._current_basis):
            if var_idx in self._artificial_indices:
                if T[i+1, -1] > 1e-6:
                    return True
        return False

    @staticmethod
    def _is_optimal(T):
        # Maximização: todos custos reduzidos (Row 0) devem ser >= 0
        # (Considerando tolerância numérica)
        return np.all(T[0, :-1] >= -1e-7)

    @staticmethod
    def _pivot_col(T):
        # Escolhe o mais negativo
        costs = T[0, :-1]
        candidates = np.where(costs < -1e-7)[0]
        if len(candidates) == 0:
            return -1
        # Regra de Bland: menor índice em caso de empate (já garantido pelo argmin no primeiro menor)
        # Mas argmin pega o menor VALOR.
        # Para evitar ciclagem, idealmente pegamos o primeiro índice com valor negativo.
        # Mas Dantzig (menor valor) é mais rápido. Vamos manter Dantzig.
        return candidates[np.argmin(costs[candidates])]

    @staticmethod
    def _pivot_row(T, pc):
        # Razão mínima
        min_ratio = float('inf')
        pivot_row = -1
        
        for i in range(1, T.shape[0]):
            elem = T[i, pc]
            if elem > 1e-9:
                ratio = T[i, -1] / elem
                if ratio < min_ratio:
                    min_ratio = ratio
                    pivot_row = i
        
        return pivot_row

    @staticmethod
    def _pivot(T, pr, pc):
        T2 = T.copy()
        pivot_val = T[pr, pc]
        T2[pr] = T[pr] / pivot_val
        
        for i in range(T.shape[0]):
            if i != pr:
                factor = T[i, pc]
                T2[i] = T[i] - factor * T2[pr]
        return T2

    def get_solution(self):
        if not self.optimal or self.infeasible:
            return None, None
            
        T = self.tableaux[-1]
        n_vars = len(self._variable_names)
        sol = {}
        
        for i, var_idx in enumerate(self._current_basis):
            name = self._variable_names[var_idx]
            val = T[i+1, -1]
            sol[name] = val
            
        # Construir vetor solução apenas para as variáveis de decisão originais (x...)
        # Assumindo que x são os primeiros
        # Precisamos saber quantas variáveis de decisão existem.
        # Elas começam com 'x'.
        
        x_vars = [v for v in self._variable_names if v.startswith('x')]
        final_sol = []
        for v in x_vars:
            final_sol.append(sol.get(v, 0.0))
            
        z = T[0, -1]
        if not self._maximize:
            z = -z  # Inverter sinal para minimização (já que resolvemos Max -Z)
            
        return final_sol, z

    def get_basis_info(self):
        if not self.optimal:
            return None
        T = self.tableaux[-1]
        info = []
        for i, idx in enumerate(self._current_basis):
            name = self._variable_names[idx]
            val = T[i+1, -1]
            info.append((name, val))
        return info