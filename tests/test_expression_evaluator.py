import unittest
import math
from unittest.mock import Mock
from Services.expression_evaluator import ExpressionEvaluator, ComplexNumber, Vector, Polynomial, Matrix

class TestExpressionEvaluator(unittest.TestCase):

    def setUp(self):
        # Mock DAO for testing without database operations
        self.mock_dao = Mock()
        self.evaluator = ExpressionEvaluator(dao=self.mock_dao, user_id=1)

    def test_evaluate_simple_expression(self):
        expressions = [
            ("3 + 5", 8),
            ("10 - 2", 8),
            ("7 * 3", 21),
            ("8 / 2", 4)
        ]
        for expr, expected in expressions:
            with self.subTest(expr=expr):
                result, _, _ = self.evaluator.evaluate(expr)
                self.assertEqual(result, expected, f"Failed for expression: {expr}")
                print(f"Passed: {expr} = {result}")

    def test_evaluate_with_constants(self):
        expressions = [
            ("pi * 2", 2 * math.pi),
            ("e + 1", math.e + 1),
            ("sqrt(4) * pi", 2 * math.pi),
            ("log(1)", 0)
        ]
        for expr, expected in expressions:
            with self.subTest(expr=expr):
                result, _, _ = self.evaluator.evaluate(expr)
                self.assertAlmostEqual(result, expected, places=5, msg=f"Failed for expression: {expr}")
                print(f"Passed: {expr} = {result}")

    def test_evaluate_with_functions(self):
        expressions = [
            ("sqrt(16) + log(2.718281828459045)", 4 + 1),
            ("log10(100) + sin(pi/2)", 2 + 1),
            ("cos(0) * sin(pi/2)", 1),
            ("abs(-5) + log2(8)", 5 + 3)
        ]
        for expr, expected in expressions:
            with self.subTest(expr=expr):
                result, _, _ = self.evaluator.evaluate(expr)
                self.assertAlmostEqual(result, expected, places=5, msg=f"Failed for expression: {expr}")
                print(f"Passed: {expr} = {result}")

    def test_complex_number_operations(self):
        expressions = [
            ("ComplexNumber(1, 2) + ComplexNumber(3, 4)", ComplexNumber(4, 6)),
            ("ComplexNumber(5, 7) - ComplexNumber(2, 3)", ComplexNumber(3, 4)),
            ("ComplexNumber(6, 8) / ComplexNumber(3, 4)", ComplexNumber(2, 0))
        ]
        for expr, expected in expressions:
            with self.subTest(expr=expr):
                result, _, _ = self.evaluator.evaluate(expr)
                # Ensuring comparison without extra decimal points
                self.assertEqual(str(result).replace(".0", ""), str(expected), f"Failed for expression: {expr}")
                print(f"Passed: {expr} = {result}")

    def test_polynomial_operations(self):
        expressions = [
            ("Polynomial([2, 3, 4]) - Polynomial([1, 0, 2])", [1, 3, 2]),
            ("Polynomial([1, 0]) * Polynomial([0, 1])", [0, 1, 0])
        ]
        for expr, expected_coefficients in expressions:
            with self.subTest(expr=expr):
                result, _, _ = self.evaluator.evaluate(expr)
                self.assertEqual(result.coefficients, expected_coefficients, f"Failed for expression: {expr}")
                print(f"Passed: {expr} = {result.coefficients}")

    def test_vector_operations(self):
        expressions = [
            ("Vector([2, 3]) + Vector([4, 5])", Vector([6, 8])),
            ("Vector([7, 8, 9]) - Vector([3, 2, 1])", Vector([4, 6, 8]))
        ]
        for expr, expected in expressions:
            with self.subTest(expr=expr):
                result, _, _ = self.evaluator.evaluate(expr)
                self.assertEqual(str(result), str(expected), f"Failed for expression: {expr}")
                print(f"Passed: {expr} = {result}")

    def test_matrix_operations(self):
        expressions = [
            ("Matrix([[1, 2], [3, 4]]) + Matrix([[2, 0], [1, 2]])", [[3, 2], [4, 6]]),
            ("Matrix([[5, 6], [7, 8]]) - Matrix([[1, 1], [1, 1]])", [[4, 5], [6, 7]]),
            ("Matrix([[1, 0], [0, 1]]) * Matrix([[4, 1], [2, 2]])", [[4, 1], [2, 2]])
        ]
        for expr, expected_matrix in expressions:
            with self.subTest(expr=expr):
                result, _, _ = self.evaluator.evaluate(expr)
                self.assertEqual(result.matrix, expected_matrix, f"Failed for expression: {expr}")
                print(f"Passed: {expr} = {result.matrix}")
