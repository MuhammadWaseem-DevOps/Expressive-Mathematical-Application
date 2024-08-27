import math
import re
from collections import deque
import datetime
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
import json


class ExpressionEvaluator:
    def __init__(self, dao, user_id):
        self.variables = {}
        self.functions = {
            'abs': abs,
            'sqrt': math.sqrt,
            'log': math.log,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'and': lambda x, y: x and y,
            'or': lambda x, y: x or y,
            'not': lambda x: not x
        }
        self.constants = {
            'pi': math.pi,
            'e': math.e
        }
        self.object_classes = {
            'Polynomial': Polynomial,
            'ComplexNumber': ComplexNumber,
            'Matrix': Matrix,
            'RationalExpression': RationalExpression,
            'InequalityExpression': InequalityExpression,
            'PiecewiseExpression': PiecewiseExpression
        }
        self.solver = StepByStepSolver()
        self.dao = dao  # Data Access Object for database operations
        self.user_id = user_id  # Current user ID for saving history
        self._history_saved = False  # Flag to track if history is saved

    def evaluate(self, expression: str):
        # Reset the history saved flag before each evaluation
        self._history_saved = False

        self.solver.log_expression(expression)
        
        # Parse and evaluate
        parser = self.Parser(expression, self)  # Passing self as the evaluator
        ast = parser.parse()
        self.solver.log_ast_generation(ast)
        
        result = self._evaluate_ast(ast)
        steps = self.solver.get_detailed_steps()

        # Save the result and steps to the computation history
        self.save_to_history(expression, result, steps)

        # Generate and display the AST
        ast_image = parser.draw_ast(ast)
        self.solver.log_final_result(result)
        return result, steps, ast_image

    def _evaluate_ast(self, node):
        if node is None:
            raise ValueError("Attempted to evaluate a None node. Check the AST construction for issues.")

        # If the node is a leaf node
        if node.left is None and node.right is None:
            value = None
            if isinstance(node.value, str) and node.value.replace('.', '', 1).isdigit():
                # Handle numeric values
                value = float(node.value)
                self.solver.log_leaf_node(node.value, value)
            elif node.value in self.variables:
                # Handle variables
                value = self.variables[node.value]
                self.solver.log_variable(node.value, value)
            elif node.value in self.constants:
                # Handle constants
                value = self.constants[node.value]
                self.solver.log_constant(node.value, value)
            elif node.value in self.functions:
                # Handle functions (returning function reference)
                return self.functions[node.value]
            elif isinstance(node.value, Polynomial):
                # Handle Polynomial objects
                value = node.value
            elif isinstance(node.value, (int, float)):
                # Handle integer or float values directly
                value = node.value
            else:
                # Handle object instantiation (like Polynomial)
                value = self._instantiate_object(node.value)
            return value

        # If the node represents a function call
        if node.value in self.functions:
            func = self.functions[node.value]
            arg = self._evaluate_ast(node.right)
            result = func(arg) if node.value == 'not' else func(self._evaluate_ast(node.left), arg)
            self.solver.log_operation(node.value, None, arg, result, node)
            return result

        # If the node represents an operator
        left_val = self._evaluate_ast(node.left) if node.left else None
        right_val = self._evaluate_ast(node.right) if node.right else None

        if left_val is None or right_val is None:
            raise ValueError(f"Failed to evaluate operator '{node.value}' because one of the operands is None.")

        if node.value == '=':
            self.variables[node.left.value] = right_val
            self.solver.log_assignment(node.left.value, right_val)
            return right_val

        # Evaluate the operation (including for Polynomial objects)
        result = self._apply_operator(node.value, left_val, right_val, node)
        return result


    def _instantiate_object(self, expression):
        try:
            class_name, params = expression.split('(', 1)
            params = params.rstrip(')')
            if class_name in self.object_classes:
                params_list = self._parse_parameters(params)
                obj = self.object_classes[class_name](*params_list)
                self.solver.log_instantiation(class_name, params_list, obj)
                return obj
            elif class_name in self.constants:
                return self.constants[class_name]
            else:
                raise ValueError(f"Unknown class or constant: {class_name}")
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
        parsed_params = [self._evaluate_ast(self.Parser(param, self).parse()) for param in param_list]
        self.solver.log_parsed_parameters(params, parsed_params)
        return parsed_params

    def _apply_operator(self, operator, left_val, right_val, node):
        try:
            result = None

            # Handle Polynomial operations
            if isinstance(left_val, Polynomial) or isinstance(right_val, Polynomial):
                if operator == '+':
                    result = left_val + right_val
                elif operator == '-':
                    result = left_val - right_val
                elif operator == '*':
                    result = left_val * right_val
                elif operator == '/':
                    result = left_val.long_division(right_val)
                else:
                    raise ValueError(f"Unsupported polynomial operator: {operator}")

                # Log the polynomial operation
                self.solver.log_operation(operator, left_val, right_val, result, node)

                # Prepare details for logging step-by-step explanation
                details = {
                    'left_coefficients': left_val.coefficients,
                    'right_coefficients': right_val.coefficients,
                    'result_coefficients': result.coefficients if isinstance(result, Polynomial) else result[0].coefficients
                }
                self.solver.log_steps_for_expression("Polynomial", details)

                return result

            # Handle standard operators
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
            elif operator in ['^', '**']:
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
            elif operator in ('>', '<', '>=', '<='):
                result = eval(f'{left_val} {operator} {right_val}')
            else:
                raise ValueError(f"Unknown operator: {operator}")

            # Log the standard operation
            self.solver.log_operation(operator, left_val, right_val, result, node)

            return result
        except Exception as e:
            raise ValueError(f"Failed to apply operator: {str(e)}")

    def save_to_history(self, expression, result, steps):
        """Save the evaluation result and steps to the computation history."""
        if not self._history_saved:
            entry = {
                'user_id': self.user_id,
                'expression': expression,
                'result': str(result),
                'computation_type': 'Expression Evaluation',
                'timestamp': datetime.datetime.now().isoformat(),  # Add the timestamp here
                'symbolic_steps': json.dumps(steps)  # Convert steps to JSON format
            }
            self.dao.insert('COMPUTATION_HISTORY', entry)
            self._history_saved = True  # Mark as saved to prevent duplicates

    class Parser:
        def __init__(self, expression, evaluator):
            self.expression = expression
            self.evaluator = evaluator
            self.tokens = self.tokenize(expression)
            self.pos = 0
            self.graph = nx.DiGraph()

        def tokenize(self, expression):
            # Updated regex pattern to include polynomial recognition
            token_pattern = re.compile(r'Polynomial\(\[.*?\]\)|\d+\.?\d*|[a-zA-Z_]\w*|[()+\-*/^=<>!&|]')
            return token_pattern.findall(expression)

        def parse(self):
            ast = self.expression_to_ast()
            return ast

        def expression_to_ast(self):
            output = deque()
            operators = deque()

            precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3, '**': 3, '=': 0, 'and': 0, 'or': 0, 'not': 0, '>': 0, '<': 0, '>=': 0, '<=': 0}
            associativity = {'+': 'L', '-': 'L', '*': 'L', '/': 'L', '^': 'R', '**': 'R'}

            def apply_operator():
                operator = operators.pop()
                right = output.pop() if output else None
                left = output.pop() if output else None

                if right is None or left is None:
                    print(f"Warning: Operator '{operator}' has a None operand. Left: {left}, Right: {right}")

                if operator in self.evaluator.functions:
                    node = ExpressionEvaluator.ASTNode(operator, None, right)
                    output.append(node)
                    self.graph.add_node(id(node), label=operator)
                    if right:
                        self.graph.add_edge(id(node), id(right))
                else:
                    node = ExpressionEvaluator.ASTNode(operator, left, right)
                    output.append(node)
                    self.graph.add_node(id(node), label=operator)
                    if left:
                        self.graph.add_edge(id(node), id(left))
                    if right:
                        self.graph.add_edge(id(node), id(right))

            while self.pos < len(self.tokens):
                token = self.tokens[self.pos]

                if token.startswith('Polynomial'):
                    # Handle polynomial tokens separately
                    node = self._parse_polynomial(token)
                    output.append(node)
                    self.evaluator.solver.log_polynomial_token(token, node)
                elif token.isnumeric() or token.replace('.', '', 1).isdigit() or token in self.evaluator.constants:
                    node = ExpressionEvaluator.ASTNode(token)
                    output.append(node)
                    self.graph.add_node(id(node), label=token)
                    self.evaluator.solver.log_numeric_token(token, node)
                elif token in self.evaluator.functions:
                    operators.append(token)
                    self.evaluator.solver.log_operator_token(token, list(operators))
                elif token == '(':
                    operators.append(token)
                    self.evaluator.solver.log_left_parenthesis(list(operators))
                elif token == ')':
                    while operators and operators[-1] != '(':
                        apply_operator()
                    operators.pop()  # Remove the '('
                    if operators and operators[-1] in self.evaluator.functions:
                        apply_operator()
                    self.evaluator.solver.log_right_parenthesis(list(operators))
                elif token in precedence:
                    while (operators and operators[-1] != '(' and
                        (precedence[operators[-1]] > precedence[token] or
                            (precedence[operators[-1]] == precedence[token] and associativity[token] == 'L'))):
                        apply_operator()
                    operators.append(token)
                    self.evaluator.solver.log_operator_token(token, list(operators))

                self.pos += 1

            while operators:
                apply_operator()

            if not output:
                raise ValueError("AST construction failed; no output generated.")

            self.evaluator.solver.log_ast_structure(output[-1])
            return output.pop()

        def _parse_polynomial(self, token):
            # Extract the coefficients from the polynomial string
            coefficients_str = token[token.find('[') + 1:token.rfind(']')]
            coefficients = [float(c.strip()) for c in coefficients_str.split(',')]
            polynomial_obj = Polynomial(coefficients)
            node = ExpressionEvaluator.ASTNode(polynomial_obj)
            node.coefficients = coefficients
            self.graph.add_node(id(node), label=f"Polynomial({coefficients})")
            return node

        def draw_ast(self, ast_node):
            """Draw the AST using matplotlib and return the image."""
            pos = nx.shell_layout(self.graph)  # Use shell_layout for better circular layout
            labels = nx.get_node_attributes(self.graph, 'label')

            plt.figure(figsize=(10, 10))
            nx.draw(self.graph, pos, labels=labels, with_labels=True, arrows=False, node_size=3000, node_color="lightblue", font_size=10, font_weight="bold")
            plt.title("Abstract Syntax Tree")

            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            image = Image.open(buf)
            return image

    class ASTNode:
        def __init__(self, value, left=None, right=None):
            self.value = value
            self.left = left
            self.right = right

        def __repr__(self):
            return f"ASTNode(value={self.value}, left={self.left}, right={self.right})"

# Step-by-Step Solver to track each step of the evaluation process
class StepByStepSolver:
    def __init__(self):
        self.steps = []

    def log_expression(self, expression):
        self.steps.append(f"Input Expression:\nThe expression given is: {expression}\n")

    def log_tokenization(self, tokens):
        numbers = [token for token in tokens if token.isdigit()]
        operators = [token for token in tokens if not token.isdigit() and token not in '()']
        parentheses = [token for token in tokens if token in '()']
        self.steps.append(f"Tokenization:\nThe expression is broken down into the following components:\n"
                          f"Numbers: {', '.join(numbers)}\n"
                          f"Operators: {', '.join(operators)}\n"
                          f"Parentheses: {', '.join(parentheses)}\n")

    def log_ast_generation(self, ast):
        self.steps.append("Building the Expression Tree:\n")

    def log_numeric_token(self, token, node):
        self.steps.append(f"Inserting numeric token '{token}' as a leaf node.\n")

    def log_polynomial_token(self, token, node):
        self.steps.append(f"Inserting polynomial '{token}' as a node with coefficients {node.coefficients}.\n")

    def log_identifier_token(self, token, node):
        self.steps.append(f"Inserting identifier token '{token}' as a leaf node.\n")

    def log_operator_token(self, token, operators):
        self.steps.append(f"Inserting operator token '{token}' into the operator stack. Stack now: {operators}\n")

    def log_left_parenthesis(self, operators):
        self.steps.append(f"Left parenthesis found. Stack now: {operators}\n")

    def log_right_parenthesis(self, operators):
        self.steps.append(f"Right parenthesis found. Resolving operations in the stack. Stack now: {operators}\n")

    def log_operator_application(self, operator, node):
        self.steps.append(f"Creating a new subtree with operator '{operator}' as the root node.\n"
                          f"  - Left child: {node.left.value}\n"
                          f"  - Right child: {node.right.value}\n")

    def log_ast_structure(self, node):
        structure = self._format_ast(node)
        self.steps.append(f"Constructed AST:\n{structure}\n")

    def _format_ast(self, node, level=0):
        """Recursively format the AST structure."""
        if node is None:
            return ""
        result = f"{'  ' * level}Node '{node.value}'\n"
        if node.left:
            result += f"{'  ' * (level + 1)}Left child of '{node.value}':\n{self._format_ast(node.left, level + 2)}"
        if node.right:
            result += f"{'  ' * (level + 1)}Right child of '{node.value}':\n{self._format_ast(node.right, level + 2)}"
        return result

    def log_leaf_node(self, value, evaluated_value):
        self.steps.append(f"Evaluating Leaf Node '{value}': Value is {evaluated_value}\n")

    def log_variable(self, variable, value):
        self.steps.append(f"Using variable '{variable}' with value {value}\n")

    def log_constant(self, constant, value):
        self.steps.append(f"Using constant '{constant}' with value {value}\n")

    def log_function(self, function, value):
        self.steps.append(f"Using function '{function}'\n")

    def log_method_call(self, obj_name, method_name, args_values, result):
        self.steps.append(f"Calling method '{method_name}' of object '{obj_name}' with arguments {args_values}. Result: {result}\n")

    def log_instantiation(self, class_name, params_list, obj):
        self.steps.append(f"Instantiating object of class '{class_name}' with parameters {params_list}. Resulting object: {obj}\n")

    def log_parsed_parameters(self, params, parsed_params):
        self.steps.append(f"Parsed parameters from '{params}' as {parsed_params}\n")

    def log_assignment(self, variable, value):
        self.steps.append(f"Assigning value {value} to variable '{variable}'\n")

    def log_operation(self, operator, left_val, right_val, result, node):
        self.steps.append(f"Evaluating operation '{operator}' on left operand {left_val} and right operand {right_val} "
                          f"results in {result}. Node '{node.value}' updated with result.\n")

    def log_final_result(self, result):
        self.steps.append(f"Final Calculation:\nThe final result of the expression evaluation is: {result}\n")

    def log_steps_for_expression(self, expression_type, details):
        """Log the detailed steps for any type of expression."""
        self.steps.append("\n" + "-" * 80 + "\n")
        
        if expression_type == "Polynomial":
            self.log_polynomial_steps(details)
        # You can add more conditions for other expression types like Relational, Piecewise, Matrix, etc.
        else:
            self.steps.append(f"Unknown expression type '{expression_type}'. Cannot generate detailed steps.")

    def log_polynomial_steps(self, details):
        left_expr = self._format_polynomial(details['left_coefficients'])
        right_expr = self._format_polynomial(details['right_coefficients'])
        result_expr = self._format_polynomial(details['result_coefficients'])
        
        self.steps.append("Step 1: Understand the Polynomial Representation\n-----------------------------------------------")
        self.steps.append(f"- Polynomial({details['left_coefficients']}) represents:\n  {left_expr}")
        self.steps.append(f"- Polynomial({details['right_coefficients']}) represents:\n  {right_expr}")

        self.steps.append("\nStep 2: Write Down the Equation\n--------------------------------")
        self.steps.append(f"({left_expr}) + ({right_expr})")

        self.steps.append("\nStep 3: Combine Like Terms\n---------------------------")
        self.steps.append(f"Combine the like terms:\n{left_expr} + {right_expr}")

        self.steps.append("\nStep 4: Perform the Addition\n-----------------------------")
        self.steps.append(f"- Combine the terms:\n  {result_expr}")

        self.steps.append("\nStep 5: State the Final Answer\n-------------------------------")
        self.steps.append(f"The result of the polynomial addition is:\n{result_expr}")

    def _format_polynomial(self, coefficients):
        terms = []
        degree = len(coefficients) - 1
        for i, coef in enumerate(coefficients):
            if coef == 0:
                continue
            term = ""
            if coef < 0:
                term += "-"
            elif i != 0:
                term += "+"
            if abs(coef) != 1 or degree == 0:
                term += f"{abs(coef)}"
            if degree - i > 0:
                term += f"x^{degree - i}"
            terms.append(term)
        return " ".join(terms)

    def get_detailed_steps(self):
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
        if '>' in this.operator:
            return f"({self.right_expr}, ∞)"
        elif '<' in this.operator:
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
