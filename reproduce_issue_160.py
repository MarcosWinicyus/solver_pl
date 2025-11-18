from core.branch_bound_solver import BranchBoundSolver

def test_issue_160():
    print("--- Testing Issue: Expected 160, Got 150 ---")
    # Max Z = 70x1 + 80x2 + 45x3 + 55x4
    c = [70, 80, 45, 55]
    
    # Constraints
    # 1) 4x1 + 6x2 + 3x3 + 5x4 <= 10
    # 2) x1 <= 1
    # 3) x3 >= 1  => -x3 <= -1
    
    A = [
        [4, 6, 3, 5],
        [1, 0, 0, 0],
        [0, 0, -1, 0]
    ]
    b = [10, 1, -1]
    
    solver = BranchBoundSolver()
    # All variables are integers
    solver.solve(c, A, b, integer_vars=[0, 1, 2, 3])
    
    if solver.best_solution:
        print(f"Best Solution Found: {solver.best_solution}")
        print(f"Best Value Found: {solver.best_value}")
        
        # Check if it matches expected
        expected_val = 160
        if abs(solver.best_value - expected_val) < 1e-5:
            print("✅ SUCCESS: Found optimal value 160")
        else:
            print(f"❌ FAILURE: Expected 160, got {solver.best_value}")
            
        print("\nSteps taken:")
        for s in solver.steps:
            print(s)
    else:
        print("No solution found")

if __name__ == "__main__":
    test_issue_160()
