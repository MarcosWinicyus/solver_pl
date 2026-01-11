# Features Documentation - Solver LP
*Didactic Platform for Teaching Operations Research*

This document details the functional and non-functional features of the "Solver LP" platform, serving as a basis for the presentation of results and scope in the Course Completion Work (TCC).

---

## 1. Overview
**Solver LP** is an interactive web application developed with **Python** and **Streamlit**, designed to assist in teaching and learning Linear Programming (LP) and Integer Programming (IP). Unlike commercial solvers (such as Gurobi or CPLEX), the focus of this tool is the **visualization of the resolution process**, allowing students to understand the algorithmic logic behind the Simplex Method and Branch & Bound.

---

## 2. Functional Requirements (FR)
The functionalities represent what the system is operationally capable of doing.

### 2.1 Solvers and Algorithms
The mathematical core of the application.

*   **FR01 - Resolution via Simplex Method (Primal)**:
    *   Support for Maximization and Minimization problems.
    *   Handling of $\le$, $\ge$, and $=$ constraints.
    *   Automatic identification of special cases: Optimal Solution, Unbounded Solution, and Infeasibility.
    *   **Didactic Mode**: Step-by-step display of each iteration, detailing who enters the base, who leaves, and the calculation of the pivot element.
    *   **Tableau Visualization**: Display of the full matrix (Tableau) at each step.

*   **FR02 - Resolution via Branch & Bound (Integer Programming)**:
    *   Allows defining which problem variables must be **integers**.
    *   **Search Strategies**: The user can choose between:
        *   *Breadth-First Search (BFS)*.
        *   *Depth-First Search (DFS)*.
        *   *Best-Bound*.
    *   **Interactive Execution**: The algorithm can be executed node by node (step-by-step) or directly to the solution.

### 2.2 Visualization and Charts
Tools to turn abstract mathematical concepts into tangible visuals.

*   **FR03 - 2D Feasible Region**: For problems with 2 variables, plots the solution area, constraints (lines), and highlights the optimal point.
*   **FR04 - 3D Feasible Region**: For problems with 3 variables, generates an interactive 3D chart (rotatable) of the solution region.
*   **FR05 - Decision Tree (Branch & Bound)**: Generates a real-time interactive graph showing:
    *   Node hierarchy (parent/child).
    *   Status of each node (Root, Optimal, Integer, Pruned, Infeasible, Fractional).
    *   Objective Function Value (Z) at each node.
    *   Reason for branching or pruning.

### 2.3 Analysis Tools (Post-Optimization)
*   **FR06 - Primal-Dual Converter**:
    *   Automatically generates the Dual model from an inserted Primal.
    *   Applies canonical transformation rules (Variable signs $\leftrightarrow$ Constraint types).
*   **FR07 - Sensitivity Analysis**:
    *   Calculates **Shadow Prices** for each constraint (marginal value of the resource).
    *   Determines **Reduced Costs** for non-basic variables.
    *   Defines **Stability Intervals** (Min/Max) for objective function coefficients ($c_j$) and for the right-hand side of constraints ($b_i$), where the optimal basis remains unchanged.
*   **FR08 - Standard Form Converter**:
    *   Transforms any inserted problem into the canonical Simplex form.
    *   Automatically adds **slack** variables ($s_i$) for $\le$ constraints.
    *   Adds **surplus** variables ($e_i$) for $\ge$ constraints.
    *   Handles equality constraints and negative RHS.

### 2.4 Session and Data Management
*   **FR09 - Problem Library**:
    *   Access to a collection of pre-registered classic problems (e.g., Diet Problem, Production Mix, Knapsack, Cutting Stock).
    *   Immediate loading of data (matrix A, vector b, vector c) to the solver.
*   **FR10 - Session History**:
    *   Automatic recording of all problems solved in the current session.
    *   Summary display with method used, Z value, and mathematical model.
    *   **Restore** Functionality: Clicking on a history item makes the problem "active" in the system again.
*   **FR11 - Import and Export**:
    *   Allows downloading the full history in **JSON** format.
    *   Allows uploading a JSON file to restore a previous session on another computer or time.

---

## 3. Non-Functional Requirements (NFR)
Quality attributes that differentiate the user experience and grid system architecture.

*   **NFR01 - State Persistence (State Management)**:
    *   *Description*: The system keeps the problem state "active" in session memory.
    *   *Benefit*: The user can load a problem in the "Library", go to the "Simplex" tab to solve it, then navigate to "Duality" to see the dual, and return to "Sensitivity Analysis" **without ever needing to retype the data**. The context navigates with the user.
    *   *Flexible Editing*: A solved problem can be edited (e.g., add a new constraint or variable to an existing problem) without losing previous data.

*   **NFR02 - Didactics and Transparency**:
    *   The system is not a "black box". All matrix operations are exposed. "Didactic Mode" prioritizes explanation (text + visual) over pure execution speed.

*   **NFR03 - Internationalization (i18n)**:
    *   Architecture prepared for multiple languages.
    *   Current support already implemented for: **Portuguese (PT)**, **English (EN)**, and **Spanish (ES)**.
    *   Dynamic language detection and switching without reloading the application from scratch.

*   **NFR04 - Usability and Interface**:
    *   Responsive layout (adaptable to different screen widths).
    *   Use of clear visual elements (semantic colors: Green for base entry/solution, Red for exit/infeasibility).
    *   Immediate feedback via "Toasts" (floating notifications) for actions like loading or importing files.
    *   Use of LaTeX for elegant mathematical rendering of formulas.