import re
import sympy as sp
from typing import List, Any

class Token:
    def __init__(self, value):
        self.value = value

class Number(Token):
    def __init__(self, value):
        value_str = str(value)
        if '.' in value_str:
            super().__init__(float(value_str))
        else:
            super().__init__(int(value_str))

class Constant(Token):
    pass

class Operator(Token):
    pass

class Function(Token):
    pass

class Variable(Token):
    pass

class Parenthesis(Token):
    pass

class Bracket(Token):
    pass

class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self):
        if self.left and self.right:
            return f"({self.left} {self.value} {self.right})"
        return str(self.value)

class SymbolicComputer:
    def __init__(self):
        self.operators = {
            '+': sp.Add, 
            '-': lambda a, b: sp.Add(a, -b, evaluate=False), 
            '*': sp.Mul, 
            '/': lambda a, b: sp.Mul(a, sp.Pow(b, -1)),
            '^': sp.Pow, 
            '**': sp.Pow, 
            'mod': sp.Mod
        }

        self.priority = {'+': 1, '-': 1, '*': 2, '/': 2, 'mod': 2, '^': 3, '**': 3}
        self.right_associative = {'^', '**'}
        self.functions = {
            'sqrt': sp.sqrt, 'cbrt': lambda x: x**(1/3), 'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
            'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan, 'log': sp.log, 'exp': sp.exp, 
            'lim': sp.limit, 'Σ': sp.summation, 'Π': sp.product, 'integrate': sp.integrate
        }
        self.constants = {'π': sp.pi, 'e': sp.E, 'I': sp.I}
        self.steps = []

    def add_step(self, step: str):
        self.steps.append(step)

    def get_steps(self) -> str:
        return "\n".join(self.steps)

    def clear_steps(self):
        self.steps = []

    def tokenize(self, expression: str) -> List[Token]:
        token_specification = [
            ('NUMBER', r'\b\d+(\.\d*)?\b'),
            ('CONSTANT', r'\bπ|e|I\b'),
            ('FUNCTION', r'\b(sin|cos|tan|log|exp|sqrt|integrate|diff|Derivative)\b'),
            ('OPERATOR', r'(\*\*|[\+\-\*/\^])'),
            ('COMMA', r','),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('LBRACKET', r'\['),
            ('RBRACKET', r'\]'),
            ('VARIABLE', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
            ('EQUALS', r'='),
            ('SKIP', r'[ \t]+'),
            ('MISMATCH', r'.'),
        ]
        tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
        tokens = []
        for mo in re.finditer(tok_regex, expression):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'NUMBER':
                tokens.append(Number(value))
            elif kind == 'CONSTANT':
                tokens.append(Constant(self.constants[value]))
            elif kind == 'FUNCTION':
                tokens.append(Function(value))
            elif kind == 'OPERATOR':
                tokens.append(Operator(value))
            elif kind == 'COMMA':
                tokens.append(Token(','))
            elif kind == 'LPAREN' or kind == 'RPAREN':
                tokens.append(Parenthesis(value))
            elif kind == 'LBRACKET' or kind == 'RBRACKET':
                tokens.append(Bracket(value))
            elif kind == 'VARIABLE':
                tokens.append(Variable(value))
            elif kind == 'EQUALS':
                tokens.append(Token(value))
            elif kind == 'SKIP':
                continue
            else:
                raise ValueError(f'Unexpected character: {value}')

        self.add_step(f"Tokens: {[token.value for token in tokens]}")
        return tokens

    def to_postfix(self, tokens: List[Token]) -> List[Token]:
        output = []
        operators = []
        
        for token in tokens:
            if isinstance(token, (Number, Variable, Constant)):
                output.append(token)
            elif isinstance(token, Operator):
                while (operators and isinstance(operators[-1], Operator) and
                    (self.priority.get(token.value, 0) < self.priority.get(operators[-1].value, 0) or
                        (self.priority.get(token.value, 0) == self.priority.get(operators[-1].value, 0) and
                        token.value not in self.right_associative))):
                    output.append(operators.pop())
                operators.append(token)
            elif isinstance(token, Function):
                operators.append(token)
            elif isinstance(token, Parenthesis):
                if token.value == '(':
                    operators.append(token)
                elif token.value == ')':
                    while operators and not isinstance(operators[-1], Parenthesis):
                        output.append(operators.pop())
                    operators.pop()  # Pop the '('
            elif isinstance(token, Bracket):
                if token.value == '[':
                    operators.append(token)
                elif token.value == ']':
                    while operators and not isinstance(operators[-1], Bracket):
                        output.append(operators.pop())
                    operators.pop()  # Pop the '['

        while operators:
            output.append(operators.pop())

        self.add_step(f"Postfix notation: {[token.value for token in output]}")
        return output

    def build_tree_from_postfix(self, postfix_tokens: List[Token]) -> Node:
        stack = []

        for token in postfix_tokens:
            if isinstance(token, (Number, Variable, Constant)):
                stack.append(Node(token))
            elif isinstance(token, Operator):
                if len(stack) < 2:
                    raise ValueError(f"Not enough operands in stack for operator {token.value}")
                right = stack.pop()
                left = stack.pop()
                stack.append(Node(token, left=left, right=right))
            elif isinstance(token, Function):
                if len(stack) < 1:
                    raise ValueError(f"Not enough operands in stack for function {token.value}")
                arg = stack.pop()
                stack.append(Node(token, right=arg))
            else:
                raise ValueError(f"Unexpected token: {token.value}")

        if len(stack) != 1:
            raise ValueError(f"Invalid postfix expression, stack should have exactly one element, but has {len(stack)}")

        self.add_step(f"Expression tree: {stack[0]}")
        return stack[0]

    def evaluate_expression(self, expression: str):
        self.clear_steps()

        # Split the expression into LHS and RHS based on the equals sign
        if '=' in expression:
            lhs_expression, rhs_expression = expression.split('=')
        else:
            lhs_expression, rhs_expression = expression, '0'  # Assume the equation is equal to zero if no equals sign

        # Tokenize and process LHS
        lhs_tokens = self.tokenize(lhs_expression.strip())
        lhs_postfix_tokens = self.to_postfix(lhs_tokens)
        lhs_tree = self.build_tree_from_postfix(lhs_postfix_tokens)

        # Tokenize and process RHS
        rhs_tokens = self.tokenize(rhs_expression.strip())
        rhs_postfix_tokens = self.to_postfix(rhs_tokens)
        rhs_tree = self.build_tree_from_postfix(rhs_postfix_tokens)

        if not lhs_tree or not rhs_tree:
            raise ValueError("The tree was not correctly built.")

        # Evaluate both sides
        lhs_result = self.evaluate_node(lhs_tree)
        rhs_result = self.evaluate_node(rhs_tree)

        # Create a SymPy equation and solve it
        equation = sp.Eq(lhs_result, rhs_result)
        self.add_step(f"Solving the equation: {equation}")
        result = sp.solve(equation)

        self.add_step(f"Final result: {result}")
        return result, self.get_steps()

    def evaluate_node(self, node: Node):
        if node is None:
            raise ValueError("Node is None during evaluation.")
        
        if isinstance(node, sp.Basic):
            return node
        
        if isinstance(node.value, Number):
            return sp.sympify(node.value.value)
        
        if isinstance(node.value, Constant):
            return node.value.value
        
        if isinstance(node.value, Variable):
            return sp.Symbol(node.value.value)
        
        if isinstance(node.value, Operator):
            left_value = self.evaluate_node(node.left)
            right_value = self.evaluate_node(node.right)
            if left_value is None or right_value is None:
                raise ValueError(f"Evaluation resulted in None for operator {node.value.value}")
            result = self.operators[node.value.value](left_value, right_value)
            self.add_step(f"Evaluating {node.value.value}: {left_value} {node.value.value} {right_value} = {result}")
            return result
        
        if isinstance(node.value, Function):
            arg_value = self.evaluate_node(node.right)
            if arg_value is None:
                raise ValueError(f"Function {node.value.value} received None as argument")
            return self.handle_function(node.value.value, arg_value)
        
        return None
    
    def handle_function(self, func_name: str, arg: Any) -> Any:
        try:
            if func_name in self.functions:
                result = self.functions[func_name](arg)
                self.add_step(f"Result of {func_name}({arg}) = {result}")
                return result
            else:
                raise ValueError(f"Unknown function: {func_name}")
        except Exception as e:
            raise ValueError(f"Error handling function {func_name}: {e}")

    def solve_equation(self, equation: str, symbol: str):
        self.clear_steps()
        sym = sp.Symbol(symbol)
        lhs, rhs = equation.split('=')
        eq = sp.Eq(sp.sympify(lhs), sp.sympify(rhs))
        self.add_step(f"Setting up the equation: {lhs} = {rhs}")
        result = sp.solve(eq, sym)
        self.add_step(f"Solving the equation for {symbol}: {result}")
        return result, self.get_steps()

    def derivative(self, function: str, symbol: str):
        self.clear_steps()
        sym = sp.Symbol(symbol)
        expr = sp.sympify(function)

        self.add_step("Steps to Differentiate:\n")
        self.add_step(r"1. **Initial Expression**:\n")
        self.add_step(rf"   \( f({symbol}) = {sp.pretty(expr)} \)\n")

        derivatives = []
        for term in expr.as_ordered_terms():
            term_derivative = sp.diff(term, sym)
            derivatives.append(term_derivative)
            self.add_step(rf"   - The derivative of \( {sp.pretty(term)} \) with respect to \( {symbol} \) is \( {sp.pretty(term_derivative)} \).\n")

        derivative_expr = sum(derivatives)
        self.add_step(r"\n3. **Combine the Results**:\n")
        self.add_step(rf"   \( f'({symbol}) = {sp.pretty(derivative_expr)} \)\n")

        self.add_step(r"\n4. **Final Result**:\n")
        self.add_step(rf"   The derivative of the expression \( {sp.pretty(expr)} \) with respect to \( {symbol} \) is **{sp.pretty(derivative_expr)}**.\n")

        return derivative_expr, self.get_steps()

    def integral(self, function: str, symbol: str):
        self.clear_steps()
        sym = sp.Symbol(symbol)
        expr = sp.sympify(function)
        integral = sp.integrate(expr, sym)
        self.add_step(f'Taking integral of {function} with respect to {symbol}: {integral} + C')
        return integral, self.get_steps()

    def limit(self, function: str, symbol: str, point):
        self.clear_steps()
        sym = sp.Symbol(symbol)
        expr = sp.sympify(function)
        limit = sp.limit(expr, sym, point)
        self.add_step(f'Taking limit of {function} as {symbol} approaches {point}: {limit}')
        return limit, self.get_steps()

    def matrix_operations(self, matrix_expr: str):
        self.clear_steps()
        matrix = sp.Matrix(sp.sympify(matrix_expr))
        determinant = matrix.det()
        inverse = matrix.inv() if matrix.det() != 0 else None
        eigenvalues = matrix.eigenvals()
        self.add_step(f"Matrix: {matrix}")
        self.add_step(f"Determinant: {determinant}")
        self.add_step(f"Inverse: {inverse}")
        self.add_step(f"Eigenvalues: {eigenvalues}")
        return {
            'matrix': matrix,
            'determinant': determinant,
            'inverse': inverse,
            'eigenvalues': eigenvalues,
            'steps': self.get_steps()
        }

    def series_expansion(self, function: str, symbol: str, point=0, order=6):
        self.clear_steps()
        sym = sp.Symbol(symbol)
        expr = sp.sympify(function)
        self.add_step(f"Computing series expansion of {function} around {point} up to order {order}.")
        series = expr.series(sym, point, order)
        self.add_step(f"Series expansion result: {series}")
        return series, self.get_steps()

    def laplace_transform(self, function: str, symbol: str):
        self.clear_steps()
        sym = sp.Symbol(symbol)
        expr = sp.sympify(function)
        self.add_step(f"Computing Laplace transform of {function} with respect to {symbol}.")
        laplace = sp.laplace_transform(expr, sym, sp.Symbol('s'))
        self.add_step(f"Laplace transform result: {laplace}")
        return laplace, self.get_steps()

    def ode_solver(self, equation: str, func: str):
        self.clear_steps()
        x = sp.Symbol('x')
        y = sp.Function(func)(x)
        eq = sp.sympify(equation)
        if not isinstance(eq, sp.Equality):
            eq = sp.Eq(eq, 0)
        self.add_step(f"Solving ordinary differential equation: {equation}")
        solution = sp.dsolve(eq, y)
        self.add_step(f"Solution of ODE: {solution}")
        return solution, self.get_steps()

    def pde_solver(self, equation, func):
        self.clear_steps()
        eq = equation
        x, t = sp.symbols('x t')
        y = sp.Function(func)(x, t)
        self.add_step(f"Solving partial differential equation: {eq}")
        try:
            solution = sp.pdsolve(eq, y)
            self.add_step(f"Solution of PDE: {solution}")
        except NotImplementedError as e:
            solution = str(e)
            self.add_step(f"Error: {solution}")
        return solution, self.get_steps()

    def tangent_line(self, function: str, symbol: str, point: float):
            self.clear_steps()
            sym = sp.Symbol(symbol)
            expr = sp.sympify(function)
            slope = sp.diff(expr, sym).subs(sym, point)
            self.add_step(f"Step 1: Differentiate the function to find the slope.\n"
                        f"   - The derivative of {sp.pretty(expr)} with respect to {symbol} is {sp.pretty(sp.diff(expr, sym))}.\n"
                        f"   - Evaluating this derivative at {symbol} = {point} gives the slope {sp.pretty(slope)}.\n")
            y_intercept = expr.subs(sym, point) - slope * point
            self.add_step(f"Step 2: Compute the y-intercept.\n"
                        f"   - Substituting {symbol} = {point} into the original function gives {sp.pretty(expr.subs(sym, point))}.\n"
                        f"   - The equation of the tangent line is y = {slope}*{symbol} + b.\n"
                        f"   - Solving for the y-intercept b gives b = {sp.pretty(y_intercept)}.\n")
            tangent = slope * sym + y_intercept
            self.add_step(f"Step 3: Form the equation of the tangent line.\n"
                        f"   - Therefore, the equation of the tangent line is y = {sp.pretty(tangent)}.\n")
            self.add_step(f"Final Result: The tangent line to the curve at {symbol} = {point} is y = {sp.pretty(tangent)}.\n")
            return tangent, self.get_steps()
    
    def solve_exact_diff_eq(self, P, Q, x, y):
        self.clear_steps()
        dP_dy = sp.diff(P, y)
        dQ_dx = sp.diff(Q, x)
        self.add_step(f"Computing partial derivatives: ∂P/∂y = {dP_dy}, ∂Q/∂x = {dQ_dx}.")
        is_exact = sp.simplify(dP_dy - dQ_dx) == 0
        if is_exact:
            self.add_step("This is an exact differential equation.")
            f_xy = sp.integrate(P, x) + sp.Function('h')(y)
            self.add_step(f"Integrating P with respect to x: ∫P dx = {sp.integrate(P, x)} + h(y).")
            f_xy_y = sp.diff(f_xy, y)
            eq = sp.Eq(f_xy_y, Q)
            self.add_step(f"Taking derivative with respect to y and setting equal to Q: {f_xy_y} = {Q}.")
            h_y = sp.dsolve(eq, sp.Function('h')(y)).rhs
            self.add_step(f"Solving for h(y): h(y) = {h_y}.")
            f_xy = f_xy.subs(sp.Function('h')(y), h_y)
            self.add_step(f"Final solution: f(x, y) = {f_xy}.")
            return f_xy, self.get_steps()
        else:
            self.add_step("This is not an exact differential equation.")
            return None, self.get_steps()

    def practice_problems(self, topic: str):
        problems = {
            'algebra': ["x^2 - 4 = 0", "2*x + 3 = 7"],
            'calculus': ["diff(x^2 + 2*x + 1, x)", "integrate(x^2 + 2*x + 1, x)"],
            'trigonometry': ["sin(x) = 0.5", "cos(x) = 0.5"],
            'linear_algebra': ["[[1, 2], [3, 4]]"],
            'series': ["exp(x)", "sin(x)"]
        }
        return problems.get(topic, [])

    def solve_practice_problem(self, problem: str):
        if '=' in problem:
            symbol = re.findall(r'\b[a-zA-Z]\b', problem)[0]
            result, steps = self.solve_equation(problem, symbol)
        elif 'diff' in problem:
            function = problem.split('(')[1].split(',')[0]
            symbol = problem.split(',')[1].strip(')')
            result, steps = self.derivative(function, symbol)
        elif 'integrate' in problem:
            function = problem.split('(')[1].split(',')[0]
            symbol = problem.split(',')[1].strip(')')
            result, steps = self.integral(function, symbol)
        elif '[' in problem:
            result = self.matrix_operations(problem)
            steps = result['steps']
        else:
            result, steps = self.evaluate_expression(problem)

        return result, steps
