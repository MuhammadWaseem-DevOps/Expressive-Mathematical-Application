import sys
import os

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from Services.expression_evaluator import ExpressionEvaluator 
from Services.symbolic_computer import SymbolicComputer
from unittest.mock import MagicMock
import tkinter as tk
import numpy as np
from Services.graph_plotter import GraphPlotter


@pytest.fixture
def graph_plotter():
    root = tk.Tk()
    canvas = tk.Canvas(root)
    mock_dao = MagicMock()
    user_id = 1
    plotter = GraphPlotter(canvas, mock_dao, user_id)
    yield plotter
    root.destroy()

def test_plot_function_and_save_data(graph_plotter):
    function = "x**2"
    graph_plotter.plot_function(function, 'x', -10, 10, 'Polynomial')
    x_data = graph_plotter.ax.lines[0].get_xdata()
    y_data = graph_plotter.ax.lines[0].get_ydata()
    expected_x = np.linspace(-10, 10, 400)
    expected_y = expected_x ** 2
    print("x_data matches expected:", np.allclose(x_data, expected_x))
    print("y_data matches expected:", np.allclose(y_data, expected_y))
    print("DAO insert called:", graph_plotter.dao.insert.called)

def test_plot_implicit_function_and_save_data(graph_plotter):
    function = "X**2 + Y**2 - 25"
    graph_plotter.plot_implicit(function, -10, 10, -10, 10)
    contours = graph_plotter.ax.collections
    print("Contours exist:", len(contours) > 0)
    print("DAO insert called:", graph_plotter.dao.insert.called)

def test_zoom_in_functionality(graph_plotter):
    graph_plotter.plot_function("x**2", 'x', -10, 10, 'Polynomial')
    initial_xlim = graph_plotter.ax.get_xlim()
    initial_ylim = graph_plotter.ax.get_ylim()
    graph_plotter.zoom_in()
    zoomed_xlim = graph_plotter.ax.get_xlim()
    zoomed_ylim = graph_plotter.ax.get_ylim()
    print("X-axis zoomed in:", zoomed_xlim[1] - zoomed_xlim[0] < initial_xlim[1] - initial_xlim[0])
    print("Y-axis zoomed in:", zoomed_ylim[1] - zoomed_ylim[0] < initial_ylim[1] - initial_ylim[0])

def test_zoom_out_functionality(graph_plotter):
    graph_plotter.plot_function("x**2", 'x', -10, 10, 'Polynomial')
    initial_xlim = graph_plotter.ax.get_xlim()
    initial_ylim = graph_plotter.ax.get_ylim()
    graph_plotter.zoom_out()
    zoomed_xlim = graph_plotter.ax.get_xlim()
    zoomed_ylim = graph_plotter.ax.get_ylim()
    print("X-axis zoomed out:", zoomed_xlim[1] - zoomed_xlim[0] > initial_xlim[1] - initial_xlim[0])
    print("Y-axis zoomed out:", zoomed_ylim[1] - zoomed_ylim[0] > initial_ylim[1] - initial_ylim[0])

@pytest.fixture
def symbolic_computer():
    return SymbolicComputer()

def test_solve_equation(symbolic_computer):
    equation = "x^2 - 4 = 0"
    symbol = "x"
    result, steps = symbolic_computer.solve_equation(equation, symbol)
    print("Equation result:", result)

def test_derivative(symbolic_computer):
    function = "x**3 + 2*x**2 + x"
    symbol = "x"
    result, steps = symbolic_computer.derivative(function, symbol)
    print("Derivative result:", result)

def test_integral(symbolic_computer):
    function = "x**2"
    symbol = "x"
    result, steps = symbolic_computer.integral(function, symbol)
    print("Integral result:", result)

def test_limit(symbolic_computer):
    function = "1/x"
    symbol = "x"
    result, steps = symbolic_computer.limit(function, symbol, 0)
    print("Limit result:", result)

@pytest.fixture
def expression_evaluator():
    mock_dao = MagicMock()
    return ExpressionEvaluator(dao=mock_dao, user_id=1)

def test_evaluate_simple_expression(expression_evaluator):
    expr = "3 + 5"
    result, steps, _ = expression_evaluator.evaluate(expr)
    print("Simple expression result:", result)

def test_evaluate_with_functions(expression_evaluator):
    expr = "sqrt(16) + log(2.718281828459045)"
    result, steps, _ = expression_evaluator.evaluate(expr)
    print("Expression with functions result:", result)

def test_variable_assignment(expression_evaluator):
    assign_expr = "x = 10"
    use_expr = "x * 2"
    expression_evaluator.evaluate(assign_expr)
    result, steps, _ = expression_evaluator.evaluate(use_expr)
    print("Variable assignment result:", result)

def test_complex_operations(expression_evaluator):
    expr = "ComplexNumber(1, 2) + ComplexNumber(3, 4)"
    result, steps, _ = expression_evaluator.evaluate(expr)
    print("Complex operations result:", result)
