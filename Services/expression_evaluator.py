import math
import re
from collections import deque

class ExpressionEvaluator:
    def __init__(self):
        self.variables = {}
        self.functions = {
            'abs': abs,
            'sqrt': math.sqrt,
            'log': math.log,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan
        }
        self.constants = {
            'pi': math.pi,
            'e': math.e
        }
        self.object_classes = {
            'Polynomial': Polynomial,
            'ComplexNumber': ComplexNumber,
            'Matrix': Matrix,
        }
        self.solver = StepByStepSolver()

    def evaluate(self, expression: str):
        parser = self.Parser(expression)
        ast = parser.parse()
        result = self._evaluate_ast(ast)
        steps = self.solver.get_steps()
        return result, steps

    def _evaluate_ast(self, node):
        if node is None:
            return None

        if node.left is None and node.right is None:
            if node.value.replace('.', '', 1).isdigit():
                return float(node.value)
            elif node.value in self.variables:
                return self.variables[node.value]
            elif node.value in self.constants:
                return self.constants[node.value]
            elif node.value in self.functions:
                return self.functions[node.value]
            elif '.' in node.value:
                return self._handle_method_call(node.value)
            else:
                return self._instantiate_object(node.value)

        left_val = self._evaluate_ast(node.left)
        right_val = self._evaluate_ast(node.right)

        if node.value == '=':
            self.variables[node.left.value] = right_val
            return right_val

        return self._apply_operator(node.value, left_val, right_val)

    def _handle_method_call(self, method_call):
        try:
            obj_name, method_call = method_call.split('.', 1)
            method_name, args = method_call.split('(', 1)
            args = args.rstrip(')')
            obj = self.variables.get(obj_name)
            if obj is None:
                raise ValueError(f"Object {obj_name} not found.")
            method = getattr(obj, method_name, None)
            if method is None:
                raise ValueError(f"Method {method_name} not found in object {obj_name}.")
            args_values = [self._evaluate_ast(self.Parser(arg.strip()).parse()) if arg else None for arg in args.split(',')] if args else []
            result = method(*args_values)
            self.solver.log_step(f"Calling method {method_name} of {obj_name} with args {args_values}", result)
            return result
        except Exception as e:
            raise ValueError(f"Failed to handle method call: {str(e)}")

    def _instantiate_object(self, expression):
        try:
            class_name, params = expression.split('(', 1)
            params = params.rstrip(')')
            if class_name in self.object_classes:
                params_list = self._parse_parameters(params)
                obj = self.object_classes[class_name](*params_list)
                self.solver.log_step(f"Instantiated {class_name} with params {params_list}", obj)
                return obj
            else:
                raise ValueError(f"Unknown class {class_name}")
        except Exception as e:
            raise ValueError(f"Failed to instantiate object: {str(e)}")

    def _parse_parameters(self, params):
        if not params:
            return []
        param_list = []
        depth = 0
        current_param = ''
        for char in params:
            if char == '(':
                depth += 1
                current_param += char
            elif char == ')':
                depth -= 1
                current_param += char
            elif char == ',' and depth == 0:
                param_list.append(current_param.strip())
                current_param = ''
            else:
                current_param += char
        if current_param:
            param_list.append(current_param.strip())
        return [self._evaluate_ast(self.Parser(param).parse()) for param in param_list]

    def _apply_operator(self, operator, left_val, right_val):
        try:
            if isinstance(left_val, Polynomial) or isinstance(right_val, Polynomial):
                if operator == '+':
                    result = left_val + right_val
                elif operator == '-':
                    result = left_val - right_val
                elif operator == '*':
                    result = left_val * right_val
                elif operator == '/':
                    result = left_val.long_division(right_val)
                self.solver.log_step(f"Applied operator {operator} on {left_val} and {right_val}", result)
                return result
            if operator == '+':
                result = left_val + right_val
            elif operator == '-':
                result = left_val - right_val
            elif operator == '*':
                result = left_val * right_val
            elif operator == '/':
                if right_val == 0:
                    raise ZeroDivisionError("Division by zero")
                result = left_val / right_val
            elif operator == '^':
                result = left_val ** right_val
            elif operator == 'and':
                result = left_val and right_val
            elif operator == 'or':
                result = left_val or right_val
            elif operator == 'not':
                result = not right_val
            elif operator == 'sqrt':
                result = math.sqrt(right_val)
            elif operator == 'log':
                result = math.log(left_val, right_val)
            elif operator == 'abs':
                result = abs(right_val)
            else:
                raise ValueError(f"Unknown operator: {operator}")
            self.solver.log_step(f"Applied operator {operator} on {left_val} and {right_val}", result)
            return result
        except Exception as e:
            raise ValueError(f"Failed to apply operator: {str(e)}")

    class Parser:
        def __init__(self, expression):
            self.expression = expression
            self.tokens = self.tokenize(expression)
            self.pos = 0

        def tokenize(self, expression):
            token_pattern = re.compile(r'\d+\.?\d*|[a-zA-Z_]\w*|[()+\-*/^=<>!&|]')
            return token_pattern.findall(expression)

        def parse(self):
            return self.expression_to_ast()

        def expression_to_ast(self):
            output = deque()
            operators = deque()

            precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3, '=': 0, 'and': 0, 'or': 0, 'not': 0}
            associativity = {'+': 'L', '-': 'L', '*': 'L', '/': 'L', '^': 'R'}

            def apply_operator():
                operator = operators.pop()
                right = output.pop()
                if operator in ['and', 'or', 'not']:
                    output.append(ExpressionEvaluator.ASTNode(operator, right))
                else:
                    left = output.pop()
                    output.append(ExpressionEvaluator.ASTNode(operator, left, right))

            while self.pos < len(self.tokens):
                token = self.tokens[self.pos]

                if token.isnumeric() or token.replace('.', '', 1).isdigit():
                    output.append(ExpressionEvaluator.ASTNode(token))
                elif token.isalpha() or token in ['pi', 'e']:
                    output.append(ExpressionEvaluator.ASTNode(token))
                elif token in precedence:
                    while (operators and operators[-1] != '(' and
                           (precedence[operators[-1]] > precedence[token] or
                            (precedence[operators[-1]] == precedence[token] and associativity[token] == 'L'))):
                        apply_operator()
                    operators.append(token)
                elif token == '(':
                    operators.append(token)
                elif token == ')':
                    while operators[-1] != '(':
                        apply_operator()
                    operators.pop()
                self.pos += 1

            while operators:
                apply_operator()

            return output.pop()

    class ASTNode:
        def __init__(self, value, left=None, right=None):
            self.value = value
            self.left = left
            self.right = right


# Step-by-Step Solver to track each step of the evaluation process
class StepByStepSolver:
    def __init__(self):
        self.steps = []

    def log_step(self, description, result):
        self.steps.append(f"{description}: {result}")

    def get_steps(self):
        return "\n".join(self.steps)


# Polynomial class with operations and root finding
class Polynomial:
    def __init__(self, coefficients):
        self.coefficients = coefficients

    def __str__(self):
        return f"Polynomial({self.coefficients})"

    def __add__(self, other):
        diff = len(self.coefficients) - len(other.coefficients)
        if diff > 0:
            other.coefficients = [0] * diff + other.coefficients
        elif diff < 0:
            self.coefficients = [0] * (-diff) + self.coefficients
        result = [a + b for a, b in zip(self.coefficients, other.coefficients)]
        return Polynomial(result)

    def __sub__(self, other):
        diff = len(self.coefficients) - len(other.coefficients)
        if diff > 0:
            other.coefficients = [0] * diff + self.coefficients
        elif diff < 0:
            self.coefficients = [0] * (-diff) + self.coefficients
        result = [a - b for a, b in zip(self.coefficients, other.coefficients)]
        return Polynomial(result)

    def __mul__(self, other):
        result = [0] * (len(self.coefficients) + len(other.coefficients) - 1)
        for i, a in enumerate(self.coefficients):
            for j, b in enumerate(other.coefficients):
                result[i + j] += a * b
        return Polynomial(result)

    def long_division(self, divisor):
        quotient = []
        remainder = self.coefficients[:]

        while len(remainder) >= len(divisor.coefficients):
            leading_term_coeff = remainder[0] / divisor.coefficients[0]
            leading_term_degree = len(remainder) - len(divisor.coefficients)
            quotient_term = [leading_term_coeff] + [0] * leading_term_degree

            quotient_poly = Polynomial(quotient_term)
            remainder_poly = Polynomial(remainder) - quotient_poly * divisor
            remainder = remainder_poly.coefficients

            while remainder and remainder[0] == 0:
                remainder.pop(0)

            quotient.append(leading_term_coeff)

        return Polynomial(quotient), Polynomial(remainder)

    def find_roots(self):
        if len(self.coefficients) == 3:
            a, b, c = self.coefficients
            discriminant = b ** 2 - 4 * a * c
            if discriminant > 0:
                root1 = (-b + math.sqrt(discriminant)) / (2 * a)
                root2 = (-b - math.sqrt(discriminant)) / (2 * a)
                return root1, root2
            elif discriminant == 0:
                return -b / (2 * a),
            else:
                return complex(-b / (2 * a), math.sqrt(-discriminant) / (2 * a)),
        return "Higher degree roots can be found using numerical methods or by factoring."


# ComplexNumber class with basic arithmetic and root finding
class ComplexNumber:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

    def __add__(self, other):
        return ComplexNumber(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other):
        return ComplexNumber(self.real - other.real, self.imag - other.imag)

    def __mul__(self, other):
        real_part = self.real * other.real - self.imag * other.imag
        imag_part = self.real * other.imag + self.imag * other.real
        return ComplexNumber(real_part, imag_part)

    def __truediv__(self, other):
        denominator = other.real ** 2 + other.imag ** 2
        real_part = (self.real * other.real + self.imag * other.imag) / denominator
        imag_part = (self.imag * other.real - self.real * other.imag) / denominator
        return ComplexNumber(real_part, imag_part)

    def __str__(self):
        return f"{self.real} + {self.imag}i"

    def nth_root(self, n):
        magnitude = math.sqrt(self.real ** 2 + self.imag ** 2)
        angle = math.atan2(self.imag, self.real)
        root_magnitude = magnitude ** (1 / n)
        roots = []
        for k in range(n):
            real_part = root_magnitude * math.cos((angle + 2 * math.pi * k) / n)
            imag_part = root_magnitude * math.sin((angle + 2 * math.pi * k) / n)
            roots.append(ComplexNumber(real_part, imag_part))
        return roots


# Matrix class with arithmetic and determinant operations
class Matrix:
    def __init__(self, matrix):
        self.matrix = matrix
        self.rows = len(matrix)
        self.cols = len(matrix[0])

    def __add__(self, other):
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Matrices must have the same dimensions to be added")
        return Matrix([[self.matrix[i][j] + other.matrix[i][j] for j in range(self.cols)] for i in range(self.rows)])

    def __sub__(self, other):
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Matrices must have the same dimensions to be subtracted")
        return Matrix([[self.matrix[i][j] - other.matrix[i][j] for j in range(self.cols)] for i in range(self.rows)])

    def __mul__(self, other):
        if self.cols != other.rows:
            raise ValueError("Number of columns in the first matrix must equal the number of rows in the second matrix")
        return Matrix([[sum(self.matrix[i][k] * other.matrix[k][j] for k in range(self.cols)) for j in range(other.cols)]
                       for i in range(self.rows)])

    def determinant(self):
        if self.rows != self.cols:
            raise ValueError("Matrix must be square to compute the determinant")
        if self.rows == 2:
            return self.matrix[0][0] * self.matrix[1][1] - self.matrix[0][1] * self.matrix[1][0]
        det = 0
        for c in range(self.cols):
            minor = [[self.matrix[i][j] for j in range(self.cols) if j != c] for i in range(1, self.rows)]
            det += ((-1) ** c) * self.matrix[0][c] * Matrix(minor).determinant()
        return det

    def inverse(self):
        det = self.determinant()
        if det == 0:
            raise ValueError("Matrix is singular and cannot be inverted")
        return Matrix(
            [[((-1) ** (i + j)) * Matrix(
                [[self.matrix[x][y] for y in range(self.cols) if y != j] for x in range(self.rows) if x != i]
            ).determinant() / det for j in range(self.cols)] for i in range(self.rows)]
        )


# Vector class with arithmetic operations and dot/cross products
class Vector:
    def __init__(self, components):
        self.components = components

    def __add__(self, other):
        return Vector([a + b for a, b in zip(self.components, other.components)])

    def __sub__(self, other):
        return Vector([a - b for a, b in zip(self.components, other.components)])

    def dot(self, other):
        return sum(a * b for a, b in zip(self.components, other.components))

    def cross(self, other):
        if len(self.components) != 3 or len(other.components) != 3:
            raise ValueError("Cross product is only defined for 3-dimensional vectors")
        return Vector(
            [
                self.components[1] * other.components[2] - self.components[2] * other.components[1],
                self.components[2] * other.components[0] - self.components[0] * other.components[2],
                self.components[0] * other.components[1] - self.components[1] * other.components[0]
            ]
        )


# Step-by-Step Solver to track each step of the evaluation process
class StepByStepSolver:
    def __init__(self):
        self.steps = []

    def log_step(self, description, result):
        self.steps.append(f"{description}: {result}")

    def get_steps(self):
        return "\n".join(self.steps)

# Rational Expression handling
class RationalExpression:
    def __init__(self, numerator, denominator):
        self.numerator = Polynomial(numerator)
        self.denominator = Polynomial(denominator)

    def simplify(self):
        def gcd(a, b):
            while b:
                a, b = b, a % b
            return a
        
        gcd_value = gcd(self.numerator.coefficients[-1], self.denominator.coefficients[-1])
        simplified_numerator = [c // gcd_value for c in self.numerator.coefficients]
        simplified_denominator = [c // gcd_value for c in self.denominator.coefficients]

        return RationalExpression(simplified_numerator, simplified_denominator)

    def add(self, other):
        common_denominator = self.denominator * other.denominator
        new_numerator = self.numerator * other.denominator + other.numerator * self.denominator
        return RationalExpression(
            new_numerator.coefficients, common_denominator.coefficients
        ).simplify()

    def subtract(self, other):
        common_denominator = self.denominator * other.denominator
        new_numerator = self.numerator * other.denominator - other.numerator * self.denominator
        return RationalExpression(
            new_numerator.coefficients, common_denominator.coefficients
        ).simplify()

    def multiply(self, other):
        new_numerator = self.numerator * other.numerator
        new_denominator = self.denominator * other.denominator
        return RationalExpression(
            new_numerator.coefficients, new_denominator.coefficients
        ).simplify()

    def divide(self, other):
        new_numerator = self.numerator * other.denominator
        new_denominator = self.denominator * other.numerator
        return RationalExpression(
            new_numerator.coefficients, new_denominator.coefficients
        ).simplify()


# Inequality Expression handling
class InequalityExpression:
    def __init__(self, left_expr, operator, right_expr):
        self.left_expr = left_expr
        self.operator = operator
        self.right_expr = right_expr

    def solve(self):
        left_val = eval(self.left_expr)
        right_val = eval(self.right_expr)
        if self.operator == '>':
            return left_val > right_val
        elif self.operator == '<':
            return left_val < right_val
        elif self.operator == '>=':
            return left_val >= right_val
        elif self.operator == '<=':
            return left_val <= right_val

    def to_interval(self):
        solution = self.solve()
        if '>' in self.operator:
            return f"({self.right_expr}, ∞)"
        elif '<' in self.operator:
            return f"(-∞, {self.right_expr})"


# Piecewise Function Evaluation
class PiecewiseExpression:
    def __init__(self, conditions, expressions):
        self.conditions = conditions
        self.expressions = expressions

    def evaluate(self, x):
        for condition, expr in zip(self.conditions, self.expressions):
            if eval(condition.replace("x", str(x))):
                return eval(expr.replace("x", str(x)))
        return None


# Example Usage in Code:
evaluator = ExpressionEvaluator()

expression = "Polynomial([1, -4, 4]).find_roots()"
result, steps = evaluator.evaluate(expression)
print("Result:", result)
print("Steps:\n", steps)
