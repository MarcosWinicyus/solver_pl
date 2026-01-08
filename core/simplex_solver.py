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
        self.constraints_info = [] # Metadata for sensitivity analysis

    # ------------------------------------------------------------------
    def initialize(
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
        self.original_c = c_list # Store for sensitivity
        
        m = len(A)
        n = len(c)
        
        # Identificar restrições que precisam de artificiais (b < 0)
        # Se Ax <= b e b < 0 -> -Ax >= -b (b torna-se positivo)
        # Adiciona surplus (-1) e artificial (+1)
        
        self.constraints_info = [] # (coeffs, rhs, type)
        
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
                self.constraints_info.append({
                    "coeffs": row,
                    "rhs": rhs,
                    "type": "ge", # >=
                    "slack_idx": -1,
                    "art_idx": -1,
                    "original_idx": i
                })
                n_surplus += 1
                n_artificial += 1
            else:
                # Mantém <=
                self.constraints_info.append({
                    "coeffs": row,
                    "rhs": rhs,
                    "type": "le", # <=
                    "slack_idx": -1,
                    "art_idx": -1,
                    "original_idx": i
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
            info = self.constraints_info[i]
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
            info = self.constraints_info[i]
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
            info = self.constraints_info[i]
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
            info = self.constraints_info[i]
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
        
        # Salvar estado para step-by-step
        self.T = T
        self.iteration_count = 0
        self.finished = False
        self.iteration_limit = iteration_limit

    def step(self) -> bool:
        """Executa um passo do algoritmo Simplex. Retorna True se continuar, False se terminou."""
        if self.finished:
            return False

        self.iteration_count += 1
        T = self.T

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
                self.finished = True
                return False

            self.optimal = True
            self._log_success(T)
            self.finished = True
            return False

        if self.iteration_count > self.iteration_limit:
             # Limite atingido
            self._log_timeout(T, self.iteration_limit)
            self.finished = True
            return False

        pc = self._pivot_col(T)
        pr = self._pivot_row(T, pc)
        
        if pr == -1:
            self.unbounded = True
            self._log_unbounded(T, pc)
            self.finished = True
            return False
            
        # Executar pivot
        self._log_iteration(T, self.iteration_count, pr, pc)
        self.T = self._pivot(T, pr, pc)
        self._current_basis[pr - 1] = pc
        return True

    def solve(
        self,
        c: List[float],
        A: List[List[float]],
        b: List[float],
        maximize: bool = True,
        iteration_limit: int = 100,
    ) -> None:
        self.initialize(c, A, b, maximize, iteration_limit)
        while self.step():
            pass

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

    def get_sensitivity_analysis(self):
        """Retorna análise de sensibilidade para RHS e Função Objetivo."""
        if not self.optimal or self.infeasible or not self.tableaux:
            return None

        T = self.tableaux[-1]
        m, n = T.shape[0] - 1, len(self.original_c) # n original vars
        
        analysis = {
            "rhs": [],
            "objective": []
        }
        
        # 1. Análise de RHS (Shadow Prices e Intervalos)
        for i, info in enumerate(self.constraints_info):
            slack_idx = info["slack_idx"]
            
            # Shadow Price (Preço Sombra)
            # Para restrição <= (slack): Shadow Price = valor na linha 0 correspondente à slack.
            # Para restrição >= (surplus): Surplus tem coeff -1 na matriz, então cuidado.
            # O tableau final tem custos reduzidos.
            # Dual variable y_i = reduced cost of slack_i? 
            # In optimal tableau, reduced cost of slack s_i is y_i.
            # Mas cuidado com Max/Min e sinais.
            # Assumindo Max Z padrão.
            shadow_price = T[0, slack_idx]
            
            # Intervalo de Estabilidade do RHS (b_i)
            # b_new = b + delta
            # Condição: B^-1 (b + delta*e_i) >= 0
            # Sendo S_i a coluna da slack no tableau ótimo (= B^-1 * e_i se slack coeff fosse I)
            # Se for <=, slack column S_i corresponde ao vetor coluna da inversa da base para aquela restrição.
            # b* (atual) = T[1:, -1]
            # Column S_i = T[1:, slack_idx]
            # Novo RHS das restrições básicas: b* - delta * S_i >= 0
            # delta * S_i <= b*
            
            b_current = T[1:, -1]
            col_slack = T[1:, slack_idx]
            
            # Encontrar limites para Delta
            delta_min = -float('inf')
            delta_max = float('inf')
            
            for r in range(m):
                s_val = col_slack[r]
                b_val = b_current[r]
                
                if abs(s_val) < 1e-9:
                    continue
                
                # delta * s_val <= b_val
                if s_val > 0:
                    # delta <= b_val / s_val
                    upper = b_val / s_val
                    delta_max = min(delta_max, upper)
                else:
                    # delta * (neg) <= b_val -> delta >= b_val / s_val
                    lower = b_val / s_val
                    delta_min = max(delta_min, lower)
            
            # Ajustar para valores originais
            original_rhs = info["rhs"]
            
            # Se restrição era >=, o slack era surplus (coeff -1), a lógica inverte?
            # Na verdade, a coluna da variável de folga/excesso carrega a informação da inversa.
            # Se for >=, shadow price costuma ser negativo num problema de Max (penaliza).
            # O valor no tableau (custo reduzido) deve refletir isso.
            
            analysis["rhs"].append({
                "id": i+1,
                "shadow_price": shadow_price,
                "current_value": original_rhs,
                "min": original_rhs + delta_min if delta_min != -float('inf') else "-∞",
                "max": original_rhs + delta_max if delta_max != float('inf') else "+∞",
                "type": info["type"]
            })

        # 2. Análise da Função Objetivo (Coeficientes c_j)
        # Intervalos de otimalidade
        
        # Identificar variáveis básicas e não-básicas originais
        basic_indices = set(self._current_basis)
        
        for j in range(n):
            var_name = self._variable_names[j] # x1, x2...
            c_orig = self.original_c[j]
            
            if j in basic_indices:
                # Variável Básica
                # A mudança em c_j afeta os custos reduzidos das não-básicas.
                # Delta c_j
                # c'_j = c_j + delta
                # Novo custo reduzido das não básicas k: r'_k = r_k - delta * y_kj
                # Onde y_kj é o elemento do tableau na linha da variável básica x_j e coluna k.
                # Precisamos saber em qual linha 'r' do tableau a variável x_j é básica.
                
                # Buscar linha onde x_j é básica
                try:
                    row_idx = self._current_basis.index(j) # 0 a m-1
                except ValueError:
                    continue # Não deveria ocorrer se j in basic_indices
                
                # Linha do tableau (row_idx + 1)
                row_vals = T[row_idx + 1, :]
                
                delta_min = -float('inf')
                delta_max = float('inf')
                
                # Iterar sobre não-básicas
                for k in range(len(self._variable_names)): # Todas vars
                    if k not in basic_indices:
                        # reduced_cost_k >= 0 (para manter otimalidade Max)
                        # r_k - delta * row_vals[k] >= 0
                        # delta * row_vals[k] <= r_k
                        
                        r_k = T[0, k]
                        y_kj = row_vals[k]
                        
                        if abs(y_kj) < 1e-9:
                            continue
                            
                        if y_kj > 0:
                            # delta <= r_k / y_kj
                            upper = r_k / y_kj
                            delta_max = min(delta_max, upper)
                        else:
                            # delta * neg <= r_k -> delta >= r_k / y_kj (lembrando que y_kj é neg, inverte sentido dividindo)
                            lower = r_k / y_kj
                            delta_min = max(delta_min, lower)
                            
                analysis["objective"].append({
                    "var": var_name,
                    "current_cost": c_orig,
                    "min": c_orig + delta_min if delta_min != -float('inf') else "-∞",
                    "max": c_orig + delta_max if delta_max != float('inf') else "+∞",
                    "status": "Básica"
                })
                
            else:
                # Variável Não-Básica
                # Pode aumentar até igualar o custo reduzido
                # Reduced cost r_j = z_j - c_j >= 0
                # Se aumentarmos c_j em delta -> novo r'_j = z_j - (c_j + delta) = r_j - delta
                # Otimalidade: r'_j >= 0 -> r_j - delta >= 0 -> delta <= r_j
                # Diminuir c_j (delta negativo) não afeta otimalidade (r_j aumenta).
                
                reduced_cost = T[0, j]
                
                analysis["objective"].append({
                    "var": var_name,
                    "current_cost": c_orig,
                    "min": "-∞",
                    "max": c_orig + reduced_cost,
                    "status": "Não-Básica"
                })

        return analysis