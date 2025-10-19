import numpy as np
from core.simplex_solver import SimplexSolver

def test_pivot_col_selects_most_negative():
    # Costs -1 and -3, last column is RHS (ignored)
    tableau = np.array([[-1.0, -3.0, 0.0]])
    col = SimplexSolver._pivot_col(tableau)
    assert col == 1

