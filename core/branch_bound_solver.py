
from __future__ import annotations

import math
from copy import deepcopy
from typing import Dict, List

from .simplex_solver import SimplexSolver


class BranchBoundSolver:
    """Branch‑and‑Bound usando Simplex como relaxação linear.

    *Compatível com Python ≥ 3.7 (removido o uso do operador walrus).*"""

    def __init__(self) -> None:
        self.nodes: List[Dict] = []
        self.best_solution: List[float] | None = None
        self.best_value: float = float("-inf")
        self.steps: List[str] = []

    # ------------------------------------------------------------------ PUBLIC API
    def solve(
        self,
        c: List[float],
        A: List[List[float]],
        b: List[float],
        integer_vars: List[int] | None = None,
        node_limit: int = 100,
    ) -> None:
        """Resolve o PLI por Branch & Bound.

        Parameters
        ----------
        c, A, b : listas
            Definição do problema Ax ≤ b, x ≥ 0, max cᵀx.
        integer_vars : list[int], opcional
            Índices (0‑based) das variáveis que devem ser inteiras. Por padrão
            torna‑se todas as variáveis de decisão.
        node_limit : int, default 100
            Limite duro de nós na árvore (evita loops infinitos).
        """

        # Reset state ---------------------------------------------------
        self.nodes.clear()
        self.steps.clear()
        self.best_solution = None
        self.best_value = float("-inf")

        if integer_vars is None:
            integer_vars = list(range(len(c)))

        # ----------------------------------------------------------- Raiz
        root_simplex = SimplexSolver()
        root_simplex.solve(c, A, b, maximize=True)
        if not root_simplex.optimal or root_simplex.unbounded:
            self.steps.append("Problema relaxado sem solução ótima ou ilimitado.")
            return

        root_sol, root_val = root_simplex.get_solution()
        self._add_node(
            node_id=0,
            parent=None,
            bounds={},
            sol=root_sol,
            val=root_val,
            int_vars=integer_vars,
        )
        if self._is_int(root_sol, integer_vars):
            self.best_solution, self.best_value = root_sol, root_val
            self.steps.append("Solução inteira já na raiz.")
            return

        # ---------------------------------------------------- Exploração
        queue: List[int] = [0]
        next_id = 1
        while queue and next_id < node_limit:
            current_id = queue.pop(0)
            node = self.nodes[current_id]
            # poda por processamento ou bound
            if node["processed"] or node["value"] <= self.best_value:
                continue
            node["processed"] = True

            frac_idx = self._first_frac(node["solution"], integer_vars)
            if frac_idx == -1:  # não deveria ocorrer, mas por segurança
                continue

            x_val = node["solution"][frac_idx]
            self.steps.append(f"Branch em x{frac_idx+1} = {x_val:.3f}")

            for op, bound in (("<=", math.floor(x_val)), (">=", math.ceil(x_val))):
                new_bounds = deepcopy(node["bounds"])
                new_bounds[frac_idx] = (op, bound)

                sub_A, sub_b = self._apply_bounds(A, b, new_bounds)
                relax = SimplexSolver()
                relax.solve(c, sub_A, sub_b, maximize=True)

                if not relax.optimal or relax.unbounded:
                    self.steps.append(f"Sub‑infeasível x{frac_idx+1} {op} {bound}")
                    self._add_node(
                        node_id=next_id,
                        parent=current_id,
                        bounds=new_bounds,
                        sol=None,
                        val=float("-inf"),
                        feasible=False,
                        int_vars=integer_vars,
                    )
                    next_id += 1
                    continue

                sub_sol, sub_val = relax.get_solution()
                new_node = self._add_node(
                    node_id=next_id,
                    parent=current_id,
                    bounds=new_bounds,
                    sol=sub_sol,
                    val=sub_val,
                    int_vars=integer_vars,
                )

                # actualização da melhor solução inteira
                if new_node["integer_feasible"] and sub_val > self.best_value:
                    self.best_solution, self.best_value = sub_sol, sub_val
                    self.steps.append(f"🎯 Melhor inteira atualizada: Z = {sub_val:.3f}")
                # Enfileira nós fracionários promissores
                elif not new_node["integer_feasible"] and sub_val > self.best_value:
                    queue.append(next_id)

                next_id += 1

    # ------------------------------------------------------------------ helpers
    def _add_node(
        self,
        node_id: int,
        parent: int | None,
        bounds: Dict[int, tuple[str, float]],
        sol: List[float] | None,
        val: float,
        int_vars: List[int] | None = None,
        feasible: bool = True,
    ) -> Dict:
        """Cria e armazena um nó na lista self.nodes."""
        if int_vars is None:
            int_vars = []

        int_feasible = sol is not None and self._is_int(sol, int_vars)

        node = {
            "id": node_id,
            "parent": parent,
            "bounds": bounds,
            "solution": sol,
            "value": val,
            "feasible": feasible,
            "integer_feasible": int_feasible,
            "processed": False,
        }
        self.nodes.append(node)
        return node

    @staticmethod
    def _is_int(sol: List[float], ivars: List[int]) -> bool:
        """Checa se *todas* variáveis em *ivars* são inteiras em *sol*."""
        return all(abs(sol[i] - round(sol[i])) < 1e-6 for i in ivars)

    @staticmethod
    def _first_frac(sol: List[float], ivars: List[int]) -> int:
        """Retorna índice da primeira variável fracionária ou −1 se nenhuma."""
        for i in ivars:
            if abs(sol[i] - round(sol[i])) > 1e-6:
                return i
        return -1

    # ---------- util para adicionar bounds extra ao problema original ----
    @staticmethod
    def _apply_bounds(
        A: List[List[float]],
        b: List[float],
        bounds: Dict[int, tuple[str, float]],
    ) -> tuple[List[List[float]], List[float]]:
        new_A, new_b = deepcopy(A), deepcopy(b)
        n = len(A[0])
        for var_idx, (op, val) in bounds.items():
            row = [0.0] * n
            if op == "<=":
                row[var_idx] = 1.0
                rhs = val
            else:  # ">=" → -x ≤ -val
                row[var_idx] = -1.0
                rhs = -val
            new_A.append(row)
            new_b.append(rhs)
        return new_A, new_b