import sys
import os

# Ensure the current directory is included in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Controllers.main_controller import MainController
from Services.authentication import AuthenticationService
from Services.expression_evaluator import ExpressionEvaluator
from Services.graph_plotter import GraphPlotter
from Services.symbolic_computer import SymbolicComputer
from Services.profile_manager import ProfileManager
from Services.dao import SQLiteDataAccessObject
from Services.error_handler import ErrorHandler
from Services.computation_history import ComputationHistory
from Services.data_exporter import DataExporter
from Gui.userview import TkinterGUI
from Services.dao import SQLiteDataAccessObject
import tkinter as tk
import sympy as sp
import re

import unittest
from Services.symbolic_computer import SymbolicComputer, Token, Number, Constant, Operator, Function, Variable, Parenthesis
'''
def test_integration():
    sc = SymbolicComputer()
    result, steps = sc.integral("2*x**3 - 4*x**2 + x - 1", "x")
    assert str(result) == "x**4/2 - 4*x**3/3 + x**2/2 - x", "Integration failed"
    assert "Taking integral" in steps, "Step-by-step explanation missing in integration"

def test_differentiation():
    sc = SymbolicComputer()
    result, steps = sc.derivative("x**3 - 2*x**2 + 3*x - 5", "x")
    assert str(result) == "3*x**2 - 4*x + 3", "Differentiation failed"
    assert "Taking derivative" in steps, "Step-by-step explanation missing in differentiation"
def test_equation_solving():
    sc = SymbolicComputer()
    result, steps = sc.solve_equation("x**2 - 4 = 0", "x")
    # Convert result to a set to avoid issues with ordering
    assert set(result) == {2, -2}, "Equation solving failed"
    assert "Setting up the equation" in steps, "Step-by-step explanation missing in equation solving"


def test_matrix_operations():
    sc = SymbolicComputer()
    results = sc.matrix_operations("[[1, 2], [3, 4]]")
    assert str(results['determinant']) == "-2", "Matrix determinant calculation failed"
    assert results['inverse'] is not None, "Matrix inverse calculation failed"
    assert len(results['eigenvalues']) == 2, "Eigenvalue calculation failed"
    assert "Matrix" in results['steps'], "Step-by-step explanation missing in matrix operations"

def test_series_expansion():
    sc = SymbolicComputer()
    result, steps = sc.series_expansion("exp(x)", "x", 0, 4)
    assert "1 + x + x**2/2 + x**3/6 + O(x**4)" in str(result), "Series expansion failed"
    assert "Computing series expansion" in steps, "Step-by-step explanation missing in series expansion"

def test_limit():
    sc = SymbolicComputer()
    result, steps = sc.limit("sin(x)/x", "x", 0)
    assert str(result) == "1", "Limit calculation failed"
    assert "Taking limit" in steps, "Step-by-step explanation missing in limit calculation"

def test_laplace_transform():
    sc = SymbolicComputer()
    result, steps = sc.laplace_transform("exp(-x)", "x")
    
    # The result is typically a tuple (expression, variable, condition)
    # We're primarily interested in the first element, the Laplace transform itself
    transform = result[0] if isinstance(result, tuple) else result
    
    # Expected result is 1/(s + 1) since L{exp(-x)} = 1/(s + 1)
    expected_transform = 1 / (sp.Symbol('s') + 1)
    
    assert transform == expected_transform, "Laplace transform failed"
    assert "Computing Laplace transform" in steps, "Step-by-step explanation missing in Laplace transform"

def test_ode_solver():
    sc = SymbolicComputer()
    
    # Define symbols and function
    x = sp.Symbol('x')
    y = sp.Function('y')(x)
    
    # Construct the ODE: y'' - 3*y' + 2*y = 0
    equation = sp.Eq(sp.Derivative(y, x, x) - 3*sp.Derivative(y, x) + 2*y, 0)
    
    # Now solve the ODE
    result, steps = sc.ode_solver(str(equation), "y")
    
    # Check if the result is a solution (contains Eq)
    assert "Eq" in str(result), "ODE solving failed"
    assert "Solving ordinary differential equation" in steps, "Step-by-step explanation missing in ODE solving"



def test_pde_solver():
    sc = SymbolicComputer()
    
    # Define the symbols and function
    x, t = sp.symbols('x t')
    u = sp.Function('u')(x, t)
    
    # Construct the PDE: u_t - u_xx = 0 (heat equation form)
    equation = sp.Eq(sp.Derivative(u, t) - sp.Derivative(u, x, x), 0)
    
    # Now solve the PDE
    result, steps = sc.pde_solver(equation, "u")
    
    # Print the result and steps for debugging
    print("Result:", result)
    print("Steps:\n", steps)
    
    # Adjusted assertion to handle the known limitation of SymPy
    assert "Cannot solve" in str(result), "PDE solving failed, but expected due to known limitations"
    assert "Solving partial differential equation" in steps, "Step-by-step explanation missing in PDE solving"

def test_tangent_line():
    sc = SymbolicComputer()
    result, steps = sc.tangent_line("x**2", "x", 1)
    assert str(result) == "2*x - 1", "Tangent line calculation failed"
    assert "Computing tangent line" in steps, "Step-by-step explanation missing in tangent line calculation"

def test_exact_diff_eq():
    sc = SymbolicComputer()
    
    # Define the symbols
    x, y = sp.symbols('x y')
    
    # Define P and Q for the exact differential equation
    P = 3*x**2 + 2*y
    Q = 2*x + x**3
    
    # Solve the exact differential equation
    result, steps = sc.solve_exact_diff_eq(P, Q, x, y)
    
    # Print the result and steps for debugging
    print("Result:", result)
    print("Steps:\n", steps)
    
    # Adjusted assertions based on the non-exactness of the equation
    assert result is None, "Expected no solution for a non-exact equation"
    assert "This is not an exact differential equation." in steps, "Expected an explanation of non-exactness"


def test_practice_problems():
    sc = SymbolicComputer()
    problems = sc.practice_problems('calculus')
    assert len(problems) > 0, "Practice problems retrieval failed"
    result, steps = sc.solve_practice_problem(problems[0])
    assert "diff" in problems[0] or "integrate" in problems[0], "Practice problem solving failed"

def run_tests():
    test_integration()
    test_differentiation()
    test_equation_solving()
    test_matrix_operations()
    test_series_expansion()
    test_limit()
    test_laplace_transform()
    test_ode_solver()
    test_pde_solver()
    test_tangent_line()
    test_exact_diff_eq()
    test_practice_problems()
    print("All test cases passed successfully.")


def run_test():
    evaluator = ExpressionEvaluator()

    test_cases = {
        "x = 3; x^2 - 4*x + 4": 1.0,
        "x = -2; 2*x^3 + 3*x^2 - x + 1": -15.0,
        "x = 2; (x^2 - 4)/(x - 2)": 'undefined',  # Division by zero
        "x = 3; (x^2 - 9)/(x - 3)": 6.0,
        "2^3^2": 512.0,
        "3^2^2": 81.0,
        "log(8, 2)": 3.0,
        "log(27, 3)": 3.0,
        "sqrt(16)": 4.0,
        "sqrt(2) * sqrt(8)": 4.0,
        "x = 4; 2*x - 5 > 3": True,
        "x = 1; x^2 + 2*x - 3 >= 0": True,
        "x = -5; abs(x + 2)": 3.0,
        "abs(2 - 7)": 5.0,
        "f(x) = x^2 if x > 0 else -x^2; f(3)": 9.0,
        "f(x) = x^2 if x > 0 else -x^2; f(-2)": -4.0,
        "sin(pi/2)": 1.0,
        "cos(0)": 1.0,
        "tan(pi/4)": 1.0,
        "x = pi/3; sin(x) + cos(x)": 1.0,
        "A = True; B = False; A and not B": True,
        "A = True; B = False; A or B and A": True
    }

    for expression, expected in test_cases.items():
        try:
            result = evaluator.evaluate(expression)
            assert result == expected, f"FAILED: {expression}, Expected: {expected}, Got: {result}"
            print(f"PASSED: {expression} = {result}")
        except Exception as e:
            print(f"ERROR: {expression} threw an exception: {e}")'''
if __name__ == "__main__":
    # Correctly specify the database path
    db_path = 'my_project_database.db'  # Path to the database file

    # Initialize the SQLiteDataAccessObject with a valid db_name
    dao = SQLiteDataAccessObject(db_name=db_path)

    # Initialize the services
    auth_service = AuthenticationService(db_path)
    expression_evaluator = ExpressionEvaluator()
    symbolic_computer = SymbolicComputer()
    profile_manager = ProfileManager(db=dao)
    error_handler = ErrorHandler()
    computation_history = ComputationHistory()
    data_exporter = DataExporter()

    # GUI Initialization without passing the parent argument
    app = TkinterGUI(
        auth_service=auth_service,
        expression_evaluator=expression_evaluator,
        symbolic_computer=symbolic_computer,
        profile_manager=profile_manager,
        error_handler=error_handler,
        computation_history=computation_history,
        data_exporter=data_exporter,
        db_path=db_path
    )
    app.mainloop()

    # Close the database connection
    dao.close()