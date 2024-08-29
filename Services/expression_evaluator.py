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
            'Vector': Vector,
            'InequalityExpression': InequalityExpression,
            'PiecewiseExpression': PiecewiseExpression
        }
        self.solver = StepByStepSolver()
        self.dao = dao  # Data Access Object for database operations
        self.user_id = user_id  # Current user ID for saving history
        self._history_saved = False  # Flag to track if history is saved

    def evaluate(self, expression: str):
        # Reset the solver state for a new evaluation
        self._history_saved = False
        self.solver.clear_steps()  # Reset the steps in the solver
        self.solver.log_expression(expression)
        
        parser = self.Parser(expression, self)
        ast = parser.parse()
        self.solver.log_ast_generation(ast)
        result = self._evaluate_ast(ast)
        steps = self.solver.get_detailed_steps()
        
        # Save the result and steps to the history for this specific evaluation
        self.save_to_history(expression, result, steps)
        
        ast_image = parser.draw_ast(ast)
        self.solver.log_final_result(result)
        return result, steps, ast_image

    def _evaluate_ast(self, node):
        if node is None:
            raise ValueError("Attempted to evaluate a None node. Check the AST construction for issues.")

        if node.left is None and node.right is None:
            # Handling constants, variables, and functions
            if isinstance(node.value, str):
                if node.value in self.constants:
                    value = self.constants[node.value]
                    self.solver.log_constant(node.value, value)
                    return value
                elif node.value in self.variables:
                    value = self.variables[node.value]
                    self.solver.log_variable(node.value, value)
                    return value
                elif node.value in self.functions:
                    # Here, we expect node.value to be a function name, so let's handle this case.
                    func = self.functions[node.value]
                    if callable(func):
                        self.solver.log_function(node.value, func)
                        return func
                    else:
                        raise ValueError(f"Expected a callable function for {node.value}, but got {type(func)}.")
                elif node.value.replace('.', '', 1).isdigit():
                    value = float(node.value)
                    self.solver.log_leaf_node(node.value, value)
                    return value
                else:
                    raise ValueError(f"Unrecognized token: {node.value}")
            else:
                return node.value

        if node.value in self.functions:
            func = self.functions[node.value]
            if callable(func):
                # For unary functions (like 'sqrt', 'sin', 'cos', etc.)
                if node.right is not None:
                    arg = self._evaluate_ast(node.right)
                    result = func(arg)
                    self.solver.log_operation(node.value, None, arg, result, node)
                    return result
                elif node.left is not None:
                    arg = self._evaluate_ast(node.left)
                    result = func(arg)
                    self.solver.log_operation(node.value, arg, None, result, node)
                    return result
                else:
                    raise ValueError(f"Function '{node.value}' requires an argument but none was provided.")
            else:
                raise ValueError(f"Expected a callable function for {node.value}, but got {type(func)}.")

        left_val = self._evaluate_ast(node.left) if node.left else None
        right_val = self._evaluate_ast(node.right) if node.right else None

        if left_val is None or right_val is None:
            raise ValueError(f"Failed to evaluate operator '{node.value}' because one of the operands is None.")

        if node.value == '=':
            self.variables[node.left.value] = right_val
            self.solver.log_assignment(node.left.value, right_val)
            return right_val

        result = self._apply_operator(node.value, left_val, right_val, node)
        return result

    def _instantiate_object(self, expression):
        try:
            class_name, params = expression.split('(', 1)
            params = params.rstrip(')')

            if class_name in self.object_classes:
                if class_name == 'Polynomial':
                    coefficients = eval(params)
                    obj = Polynomial(coefficients)
                elif class_name == 'Matrix':
                    params_list = [self._parse_matrix_parameters(params)]
                    obj = self.object_classes[class_name](*params_list)
                elif class_name == 'Vector':
                    params_list = [self._parse_vector_parameters(params)]
                    obj = self.object_classes[class_name](*params_list)
                elif class_name == 'InequalityExpression':
                    params_list = self._parse_inequality_expression_parameters(params)
                    obj = self.object_classes[class_name](*params_list)
                elif class_name == 'PiecewiseExpression':
                    params_list = self._parse_piecewise_expression_parameters(params)
                    obj = self.object_classes[class_name](*params_list)
                elif class_name == 'ComplexNumber':
                    # Properly parsing ComplexNumber parameters
                    real_part, imag_part = self._parse_complex_parameters(params)
                    obj = self.object_classes[class_name](real_part, imag_part)
                else:
                    params_list = self._parse_parameters(params)
                    obj = self.object_classes[class_name](*params_list)

                self.solver.log_instantiation(class_name, params, obj)
                return obj
            elif class_name in self.constants:
                return self.constants[class_name]
            else:
                raise ValueError(f"Unknown class or constant: {class_name}")
        except Exception as e:
            raise ValueError(f"Failed to instantiate object: {str(e)}")

    def _parse_complex_parameters(self, params):
        try:
            # Remove any surrounding whitespace and split the string by comma
            param_list = params.split(',')
            if len(param_list) != 2:
                raise ValueError(f"ComplexNumber requires exactly 2 parameters, got {len(param_list)}")

            # Convert the split strings into floats
            real_part = float(param_list[0].strip())
            imag_part = float(param_list[1].strip())
            return real_part, imag_part
        except ValueError as ve:
            raise ValueError(f"Error parsing ComplexNumber parameters: {ve}")

    def _parse_vector_parameters(self, params):
        vector_str = params.strip()
        vector = eval(vector_str)
        if not isinstance(vector, list):
            raise ValueError(f"Invalid vector format: {params}")
        return vector

    def _parse_matrix_parameters(self, params):
        matrix_str = params.strip()
        matrix = eval(matrix_str)
        if not isinstance(matrix, list) or not all(isinstance(row, list) for row in matrix):
            raise ValueError(f"Invalid matrix format: {params}")
        return matrix

    def _parse_inequality_expression_parameters(self, params):
        parts = params.split(',')
        left_expr = parts[0].strip()
        operator = parts[1].strip().strip('"')
        right_expr = parts[2].strip().strip('"')
        return [left_expr, operator, right_expr]

    def _parse_piecewise_expression_parameters(self, params):
        parts = params.split('],[')
        conditions = [x.strip().strip('"') for x in parts[0].lstrip('[').split(',')]
        expressions = [x.strip().strip('"') for x in parts[1].rstrip(']').split(',')]
        return [conditions, expressions]

    def _parse_piecewise_params(self, params):
        conditions_part, expressions_part = params.split('],[')
        conditions = json.loads(conditions_part + ']')
        expressions = json.loads('[' + expressions_part)
        return conditions, expressions

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
            if left_val is None or right_val is None:
                raise ValueError(f"Failed to evaluate operator '{operator}' because one of the operands is None. Left: {left_val}, Right: {right_val}")

            result = None
            if isinstance(left_val, Polynomial) or isinstance(right_val, Polynomial):
                # Polynomial operations
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
                self.solver.log_operation(operator, left_val, right_val, result, node)
                details = {
                    'left_coefficients': left_val.coefficients,
                    'right_coefficients': right_val.coefficients,
                    'result_coefficients': result.coefficients if isinstance(result, Polynomial) else result[0].coefficients
                }
                self.solver.log_steps_for_expression("Polynomial", details)
                return result
            elif isinstance(left_val, ComplexNumber) or isinstance(right_val, ComplexNumber):
                # Complex number operations
                if operator == '+':
                    result = left_val + right_val
                elif operator == '-':
                    result = left_val - right_val
                elif operator == '*':
                    result = left_val * right_val
                elif operator == '/':
                    result = left_val / right_val
                else:
                    raise ValueError(f"Unsupported complex number operator: {operator}")
                self.solver.log_operation(operator, left_val, right_val, result, node)
                details = {
                    'left_complex': left_val,
                    'right_complex': right_val,
                    'operation': operator,
                    'result': result
                }
                self.solver.log_steps_for_expression("ComplexNumber", details)
                return result
            elif isinstance(left_val, Matrix) or isinstance(right_val, Matrix):
                # Matrix operations
                if operator == '+':
                    result = left_val + right_val
                elif operator == '-':
                    result = left_val - right_val
                elif operator == '*':
                    result = left_val * right_val
                else:
                    raise ValueError(f"Unsupported matrix operator: {operator}")
                self.solver.log_operation(operator, left_val, right_val, result, node)
                return result
            elif isinstance(left_val, Vector) or isinstance(right_val, Vector):
                # Vector operations
                if operator == '+':
                    result = left_val + right_val
                elif operator == '-':
                    result = left_val - right_val
                elif operator == '.':
                    result = left_val.dot(right_val)  # Dot product
                elif operator == 'x':
                    result = left_val.cross(right_val)  # Cross product
                else:
                    raise ValueError(f"Unsupported vector operator: {operator}")
                self.solver.log_operation(operator, left_val, right_val, result, node)
                details = {
                    'left_vector': left_val.components,
                    'right_vector': right_val.components,
                    'operation': operator,
                    'result': result
                }
                self.solver.log_steps_for_expression("Vector", details)
                return result
            elif isinstance(left_val, InequalityExpression) or isinstance(right_val, InequalityExpression):
                result = left_val.solve()
                self.solver.log_operation(operator, left_val, right_val, result, node)
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
            self.solver.log_operation(operator, left_val, right_val, result, node)
            return result
        except Exception as e:
            raise ValueError(f"Failed to apply operator: {str(e)}")

    def save_to_history(self, expression, result, steps):
        if not self._history_saved:
            entry = {
                'user_id': self.user_id,
                'expression': expression,
                'result': str(result),
                'computation_type': 'Expression Evaluation',
                'timestamp': datetime.datetime.now().isoformat(),
                'symbolic_steps': json.dumps(steps)
            }
            self.dao.insert('COMPUTATION_HISTORY', entry)
            self._history_saved = True

    class Parser:
        def __init__(self, expression, evaluator):
            self.expression = expression
            self.evaluator = evaluator
            self.tokens = self.tokenize(expression)
            self.pos = 0
            self.graph = nx.DiGraph()

        def tokenize(self, expression):
            token_pattern = re.compile(
                r'Polynomial\(\[.*?\]\)|Matrix\(\[\[.*?\]\]\)|Vector\(\[.*?\]\)|InequalityExpression\(".*?","\w+",".*?"\)|'
                r'PiecewiseExpression\(\[.*?\],\[.*?\]\)|ComplexNumber\([ \d.,-]+\)|\d+\.?\d*|[a-zA-Z_]\w*|[()+\-*/^=<>!&|]')
            tokens = token_pattern.findall(expression)
            self.evaluator.solver.log_tokenization(tokens)
            return tokens

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

                if operator in ('+', '-', '*', '/', '^', '**') and (left is None or right is None):
                    raise ValueError(f"Operator '{operator}' requires two operands, but got: Left: {left}, Right: {right}")

                node = ExpressionEvaluator.ASTNode(operator, left, right)
                output.append(node)
                self.graph.add_node(id(node), label=operator)
                if left:
                    self.graph.add_edge(id(node), id(left))
                if right:
                    self.graph.add_edge(id(node), id(right))
                self.evaluator.solver.log_ast_construction(node)

            while self.pos < len(self.tokens):
                token = self.tokens[self.pos]

                if token.startswith('Polynomial') or token.startswith('Matrix') or token.startswith('Vector') or token.startswith('InequalityExpression') or token.startswith('PiecewiseExpression') or token.startswith('ComplexNumber'):
                    node = self.evaluator._instantiate_object(token)
                    ast_node = ExpressionEvaluator.ASTNode(node)
                    output.append(ast_node)
                    self.graph.add_node(id(ast_node), label=str(node))
                elif token in self.evaluator.constants:
                    value = self.evaluator.constants[token]
                    node = ExpressionEvaluator.ASTNode(value)
                    output.append(node)
                    self.graph.add_node(id(node), label=token)
                elif token in self.evaluator.functions:
                    operators.append(token)  # Push the function onto the operators stack
                elif token == '(':
                    operators.append(token)
                elif token == ')':
                    while operators and operators[-1] != '(':
                        apply_operator()
                    operators.pop()  # Pop the '('
                    if operators and operators[-1] in self.evaluator.functions:
                        # If the top of the stack is a function, treat it as such
                        func = operators.pop()
                        arg = output.pop()
                        func_node = ExpressionEvaluator.ASTNode(func, None, arg)
                        output.append(func_node)
                        self.graph.add_node(id(func_node), label=func)
                        self.graph.add_edge(id(func_node), id(arg))
                        self.evaluator.solver.log_ast_construction(func_node)
                elif token.isdigit() or token.replace('.', '', 1).isdigit():
                    node = ExpressionEvaluator.ASTNode(token)
                    output.append(node)
                    self.graph.add_node(id(node), label=token)
                elif token in precedence:
                    while (operators and operators[-1] != '(' and
                        (precedence[operators[-1]] > precedence[token] or
                            (precedence[operators[-1]] == precedence[token] and associativity[token] == 'L'))):
                        apply_operator()
                    operators.append(token)

                self.evaluator.solver.log_stack_operation("Processed", token, list(output), list(operators))
                self.pos += 1

            while operators:
                apply_operator()

            if not output:
                raise ValueError("AST construction failed; no output generated.")

            final_ast = output.pop()
            self.evaluator.solver.log_ast_construction(final_ast)
            return final_ast


        def draw_ast(self, ast_node):
            def set_positions(node, x=0, y=0, positions=None, level=0, width_scale=10):
                if positions is None:
                    positions = {}

                if node is not None:
                    # Assign the position for the current node
                    positions[id(node)] = (x, y)

                    # Increase the vertical distance between nodes to avoid overlap
                    vertical_offset = 1.5  # Adjust this value to reduce overlap

                    # Calculate positions for the left and right children
                    if node.left:
                        set_positions(node.left, x - width_scale / (2 ** (level + 1)), y - vertical_offset, positions, level + 1, width_scale)
                    if node.right:
                        set_positions(node.right, x + width_scale / (2 ** (level + 1)), y - vertical_offset, positions, level + 1, width_scale)

                return positions

            # Generate positions for each node in the AST
            positions = set_positions(ast_node, width_scale=10)

            # Ensure every node in the graph has a position
            for node_id in self.graph.nodes:
                if node_id not in positions:
                    positions[node_id] = (0, 0)  # Assign a default position

            # Adjust node labels for readability
            labels = nx.get_node_attributes(self.graph, 'label')

            # Initialize the plot with a larger figure size for clarity
            plt.figure(figsize=(14, 10))

            # Estimate the appropriate node size based on label length
            node_sizes = []
            for node_id, label in labels.items():
                estimated_length = len(label) * 1000  # Adjust multiplier as needed for better fitting
                node_sizes.append(estimated_length)

            # Draw the graph with manually set positions and calculated node sizes
            nx.draw(self.graph, pos=positions, labels=labels, with_labels=True,
                    arrows=False, node_size=node_sizes, node_color="lightblue", font_size=10, font_weight="bold")

            plt.title("Abstract Syntax Tree")
            plt.axis('off')  # Turn off the axis for a cleaner look
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
        self.ast_construction_logs = []

    def clear_steps(self):
        """Clear the steps and logs for a fresh evaluation."""
        self.steps = []
        self.ast_construction_logs = []

    def log_expression(self, expression):
        self.steps.append(f"Input Expression:\nThe expression given is: {expression}\n")

    def log_tokenization(self, tokens):
        numbers = [token for token in tokens if token.replace('.', '', 1).isdigit()]
        operators = [token for token in tokens if token in '+-*/^=<>!&|']
        parentheses = [token for token in tokens if token in '()']
        self.steps.append(f"Tokenization:\nThe expression is broken down into the following components:\n"
                          f"Numbers: {', '.join(numbers)}\n"
                          f"Operators: {', '.join(operators)}\n"
                          f"Parentheses: {', '.join(parentheses)}\n")

    def log_ast_generation(self, ast):
        self.steps.append("Building the Expression Tree:\n")

    def log_ast_construction(self, node):
        structure = self._format_ast(node)
        self.ast_construction_logs.append(f"AST Node '{node.value}' with structure:\n{structure}\n")

    def _format_ast(self, node, level=0):
        if node is None:
            return ""
        result = f"{'  ' * level}Node '{node.value}'\n"
        if node.left:
            result += f"{'  ' * (level + 1)}Left child of '{node.value}':\n{self._format_ast(node.left, level + 2)}"
        if node.right:
            result += f"{'  ' * (level + 1)}Right child of '{node.value}':\n{self._format_ast(node.right, level + 2)}"
        return result

    def log_stack_operation(self, operation, token, output_stack, operator_stack):
        self.steps.append(f"{operation} Token '{token}':\n"
                          f"  Output Stack: {[str(node.value) for node in output_stack]}\n"
                          f"  Operator Stack: {operator_stack}\n")

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
        self.steps.append("\n" + "-" * 80 + "\n")
        if expression_type == "Polynomial":
            self.log_polynomial_steps(details)
        elif expression_type == "Vector":
            self.log_vector_steps(details)
        elif expression_type == "ComplexNumber":
            self.log_complex_steps(details)
        else:
            self.steps.append(f"Unknown expression type '{expression_type}'. Cannot generate detailed steps.")

    def log_vector_steps(self, details):
        self.steps.append("Step 1: Understand the Vector Representation\n-----------------------------------------------")
        self.steps.append(f"Left Vector: {details['left_vector']}")
        self.steps.append(f"Right Vector: {details['right_vector']}")

        self.steps.append("\nStep 2: Perform the Operation\n-----------------------------")
        self.steps.append(f"- {details['operation']} of vectors results in: {details['result']}")

    def log_complex_steps(self, details):
        self.steps.append("Step 1: Understand the Complex Number Representation\n-----------------------------------------------")
        self.steps.append(f"Left Complex Number: {details['left_complex']}")
        self.steps.append(f"Right Complex Number: {details['right_complex']}")

        self.steps.append("\nStep 2: Perform the Operation\n-----------------------------")
        self.steps.append(f"- {details['operation']} of complex numbers results in: {details['result']}")


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

            if coef < 0:
                sign = '-' if len(terms) == 0 else ' - '
            else:
                sign = '' if len(terms) == 0 else ' + '

            if abs(coef) != 1 or degree - i == 0:
                term = f"{abs(coef)}"
            else:
                term = ""

            if degree - i > 0:
                term += f"x"
                if degree - i > 1:
                    term += f"^{degree - i}"

            terms.append(sign + term)

        return "".join(terms)

    def get_detailed_steps(self):
        return "\n".join(self.steps) + "\n" + "\n".join(self.ast_construction_logs)


# Polynomial class with operations and root finding
class Polynomial:
    def __init__(self, coefficients):
        self.coefficients = coefficients

    def __str__(self):
        return f"Polynomial({self.coefficients})"

    def __add__(self, other):
        self_coeffs = self.coefficients[:]
        other_coeffs = other.coefficients[:]

        diff = len(self_coeffs) - len(other_coeffs)
        if diff > 0:
            other_coeffs = [0] * diff + other_coeffs
        elif diff < 0:
            self_coeffs = [0] * (-diff) + self.coefficients

        result = [a + b for a, b in zip(self_coeffs, other_coeffs)]
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

    def __str__(self):
        return f"Matrix({self.matrix})"


# Vector class with basic operations
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

    def __str__(self):
        return f"Vector({self.components})"

# InequalityExpression class with evaluation and interval representation
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

    def __str__(self):
        return f"InequalityExpression({self.left_expr} {self.operator} {self.right_expr})"


# PiecewiseExpression class for handling piecewise functions
class PiecewiseExpression:
    def __init__(self, conditions, expressions):
        self.conditions = conditions
        self.expressions = expressions

    def evaluate(self, x):
        for condition, expr in zip(self.conditions, self.expressions):
            if eval(condition.replace("x", str(x))):
                return eval(expr.replace("x", str(x)))
        return None

    def __str__(self):
        return f"PiecewiseExpression({self.conditions}, {self.expressions})"
