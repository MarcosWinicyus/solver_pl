from core.simplex_solver import SimplexSolver
from core.branch_bound_solver import BranchBoundSolver

def test_simplex_negative_rhs():
    print("--- Testing Simplex with Negative RHS ---")
    # Max Z = x1 + x2
    # s.t.
    # x1 + x2 >= 2  => -x1 - x2 <= -2
    c = [1, 1]
    A = [[-1, -1]]
    b = [-2]
    
    solver = SimplexSolver()
    solver.solve(c, A, b)
    
    if solver.optimal:
        sol, z = solver.get_solution()
        print(f"Solution: {sol}, Z: {z}")
        # Expected: Should handle it, but likely will fail or give wrong result because origin is infeasible
        # x1=0, x2=0 => 0 <= -2 (False)
    else:
        print("Solver failed or unbounded")
        print(solver.decisions[-1] if solver.decisions else "No decisions")

def test_bab_ge_constraint():
    print("\n--- Testing Branch & Bound with >= Constraint ---")
    # Max Z = x1
    # s.t.
    # x1 <= 5.5
    # x1 integer
    # Branching should try x1 <= 5 and x1 >= 6
    # x1 >= 6 will be -x1 <= -6.
    
    c = [1]
    A = [[1]]
    b = [5.5]
    
    solver = BranchBoundSolver()
    solver.solve(c, A, b, integer_vars=[0])
    
    print("Steps:")
    for step in solver.steps:
        print(step)
        
    if solver.best_solution:
        print(f"Best Solution: {solver.best_solution}, Value: {solver.best_value}")
    else:
        print("No solution found")

if __name__ == "__main__":
    test_simplex_negative_rhs()
    test_bab_ge_constraint()
