import unittest
from sympy import Symbol, Matrix, pi, E, I
from Services.symbolic_computer import SymbolicComputer, Token, Number, Constant, Operator, Function, Variable, Node

class TestSymbolicComputer(unittest.TestCase):

    def setUp(self):
        self.computer = SymbolicComputer()

    def test_tokenize_expression(self):
        expression = "3 + 4 * x - 5 / y"
        tokens = self.computer.tokenize(expression)
        expected_tokens = [Number(3), Operator('+'), Number(4), Operator('*'), Variable('x'),
                           Operator('-'), Number(5), Operator('/'), Variable('y')]
        self.assertEqual([type(token) for token in tokens], [type(et) for et in expected_tokens])
        self.assertEqual([token.value for token in tokens], [et.value for et in expected_tokens])

    def test_tokenize_constant(self):
        expression = "pi * 2 + e"
        tokens = self.computer.tokenize(expression)
        expected_tokens = [Constant(pi), Operator('*'), Number(2), Operator('+'), Constant(E)]
        self.assertEqual([type(token) for token in tokens], [type(et) for et in expected_tokens])
        self.assertEqual([token.value for token in tokens], [et.value for et in expected_tokens])

    def test_to_postfix(self):
        expression = "3 + 4 * x - 5 / y"
        tokens = self.computer.tokenize(expression)
        postfix_tokens = self.computer.to_postfix(tokens)
        expected_postfix = ['3', '4', 'x', '*', '+', '5', 'y', '/', '-']
        self.assertEqual([token.value for token in postfix_tokens], expected_postfix)

    def test_build_tree_from_postfix(self):
        expression = "3 + 4 * x - 5 / y"
        tokens = self.computer.tokenize(expression)
        postfix_tokens = self.computer.to_postfix(tokens)
        tree = self.computer.build_tree_from_postfix(postfix_tokens)
        self.assertIsInstance(tree, Node)
        self.assertEqual(str(tree), "((3 + (4 * x)) - (5 / y))")

    def test_evaluate_expression_simple(self):
        expression = "2 + 3 * 4"
        result, _ = self.computer.evaluate_expression(expression)
        self.assertEqual(result, 14)

    def test_evaluate_expression_with_variables(self):
        expression = "2 * x + 3"
        result, _ = self.computer.evaluate_expression(expression)
        self.assertEqual(str(result), "2*x + 3")

    def test_evaluate_derivative(self):
        function = "x**2"
        symbol = "x"
        derivative, _ = self.computer.derivative(function, symbol)
        self.assertEqual(str(derivative), "2*x")

    def test_evaluate_integral(self):
        function = "x**2"
        symbol = "x"
        integral, _ = self.computer.integral(function, symbol)
        self.assertEqual(str(integral), "x**3/3 + C")

    def test_evaluate_limit(self):
        function = "sin(x)/x"
        symbol = "x"
        point = 0
        limit, _ = self.computer.limit(function, symbol, point)
        self.assertEqual(limit, 1)

    def test_matrix_operations(self):
        matrix_expr = "[[1, 2], [3, 4]]"
        result = self.computer.matrix_operations(matrix_expr)
        expected_matrix = Matrix([[1, 2], [3, 4]])
        expected_determinant = -2
        expected_inverse = Matrix([[-2, 1], [1.5, -0.5]])
        self.assertTrue(result['matrix'].equals(expected_matrix))
        self.assertEqual(result['determinant'], expected_determinant)
        self.assertTrue(result['inverse'].equals(expected_inverse))

    def test_solve_linear_equation(self):
        equation = "2*x + 3 = 7"
        solution, _ = self.computer.solve_linear_equation(equation)
        self.assertEqual(solution, [2])

    def test_solve_ode(self):
        equation = "diff(y(x), x) - y(x) = 0"
        func = "y(x)"
        solution, _ = self.computer.ode_solver(equation, func)
        expected_solution = "Eq(y(x), C1*exp(x))"
        self.assertEqual(str(solution), expected_solution)

    def test_tangent_line(self):
        function = "x**2"
        symbol = "x"
        point = 1.0
        tangent, _ = self.computer.tangent_line(function, symbol, point)
        self.assertEqual(str(tangent), "2.0*x - 1.0")
