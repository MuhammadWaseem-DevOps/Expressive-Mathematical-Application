import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
import datetime
import numpy as np
import matplotlib.pyplot as plt
from tkinter.scrolledtext import ScrolledText
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from Services.symbolic_computer import SymbolicComputer
import sympy as sp
import json


class SymbolicComputation(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller

        self.computer = SymbolicComputer()
        self.history = []
        self.future = []

        self.create_main_layout()
        self.create_statusbar()

    def create_main_layout(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        input_frame = ttk.Frame(top_frame)
        input_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        ttk.Label(input_frame, text="Enter a problem", font=("Helvetica", 14)).pack(anchor=tk.W)

        self.input_text = tk.Entry(input_frame, font=("Helvetica", 14), width=50)
        self.input_text.pack(fill=tk.X, pady=(5, 5))

        go_button = ttk.Button(input_frame, text="Go", command=self.solve, width=5)
        go_button.pack(side=tk.RIGHT, pady=(5, 5), padx=(5, 0))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

        simplify_button = ttk.Button(button_frame, text="Simplify", command=self.simplify)
        simplify_button.pack(side=tk.LEFT, padx=5)

        solve_button = ttk.Button(button_frame, text="Solve", command=self.solve)
        solve_button.pack(side=tk.LEFT, padx=5)

        inverse_button = ttk.Button(button_frame, text="Inverse", command=self.solve)
        inverse_button.pack(side=tk.LEFT, padx=5)

        tangent_button = ttk.Button(button_frame, text="Tangent", command=self.solve_tangent)
        tangent_button.pack(side=tk.LEFT, padx=5)

        line_button = ttk.Button(button_frame, text="Line", command=self.solve_line)
        line_button.pack(side=tk.LEFT, padx=5)

        dropdown = ttk.Combobox(button_frame, values=["See All", "Derivative", "Integral", "Limit", "ODE Solver"])
        dropdown.current(0)
        dropdown.bind("<<ComboboxSelected>>", self.handle_dropdown_selection)
        dropdown.pack(side=tk.LEFT, padx=5)

        result_frame = ttk.LabelFrame(main_frame, text="Result")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tab_control = ttk.Notebook(result_frame)
        tab_control.pack(fill=tk.BOTH, expand=True)

        self.result_tab = ScrolledText(tab_control, wrap=tk.WORD, state=tk.DISABLED)
        tab_control.add(self.result_tab, text="Result")

        self.step_tab = ScrolledText(tab_control, wrap=tk.WORD, state=tk.DISABLED)
        tab_control.add(self.step_tab, text="Steps")

        bottom_button_frame = ttk.Frame(main_frame)
        bottom_button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        undo_button = ttk.Button(bottom_button_frame, text="Undo", command=self.undo)
        undo_button.pack(side=tk.LEFT, padx=5)

        redo_button = ttk.Button(bottom_button_frame, text="Redo", command=self.redo)
        redo_button.pack(side=tk.LEFT, padx=5)

        save_button = ttk.Button(bottom_button_frame, text="Save", command=self.save_solution)
        save_button.pack(side=tk.LEFT, padx=5)

    def create_statusbar(self):
        self.statusbar = ttk.Label(self, text="Ready", relief=tk.SUNKEN, anchor=tk.W, padding="5")
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def handle_dropdown_selection(self, event):
        selected = event.widget.get()
        if selected == "Derivative":
            self.solve_derivative()
        elif selected == "Integral":
            self.solve_integral()
        elif selected == "Limit":
            self.solve_limit()
        elif selected == "ODE Solver":
            self.solve_ode()

    def solve(self):
        expression = self.input_text.get().strip()
        if expression:
            try:
                if expression.startswith("[[") and expression.endswith("]]"):
                    result = self.computer.matrix_operations(expression)
                    self.display_result(f"Matrix Result: {result['matrix']}\n"
                                        f"Determinant: {result['determinant']}\n"
                                        f"Inverse: {result['inverse']}\n"
                                        f"Eigenvalues: {result['eigenvalues']}")
                    steps = result['steps']
                else:
                    result, steps = self.computer.evaluate_expression(expression)
                    self.display_result(f"Result: {result}")
                    
                self.last_steps = steps 
                self.display_steps()
                self.statusbar.config(text="Calculation completed successfully.")
                self.save_computation_to_db(expression, result, steps, "evaluation")  
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.statusbar.config(text="Error in calculation.")
        self.update_history()

    def solve_derivative(self):
        expression = self.input_text.get().strip()
        if expression:
            try:
                function, symbol = expression.split(',')
                result, steps = self.computer.derivative(function.strip(), symbol.strip())
                self.last_steps = steps
                self.display_result(f"Derivative: {result}")
                self.display_steps()
                self.statusbar.config(text="Derivative calculation completed successfully.")
                self.save_computation_to_db(expression, result, steps, "derivative") 
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.statusbar.config(text="Error in derivative calculation.")
        self.update_history()

    def solve_integral(self):
        expression = self.input_text.get().strip()
        if expression:
            try:
                function, symbol = expression.split(',')
                result, steps = self.computer.integral(function.strip(), symbol.strip())
                self.last_steps = steps
                self.display_result(f"Integral: {result}")
                self.display_steps()
                self.statusbar.config(text="Integral calculation completed successfully.")
                self.save_computation_to_db(expression, result, steps, "integral") 
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.statusbar.config(text="Error in integral calculation.")
        self.update_history()

    def solve_limit(self):
        expression = self.input_text.get().strip()
        if expression:
            try:
                function, symbol, point = expression.split(',')
                result, steps = self.computer.limit(function.strip(), symbol.strip(), float(point.strip()))
                self.last_steps = steps
                self.display_result(f"Limit: {result}")
                self.display_steps()
                self.statusbar.config(text="Limit calculation completed successfully.")
                self.save_computation_to_db(expression, result, steps, "limit") 
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.statusbar.config(text="Error in limit calculation.")
        self.update_history()

    def solve_ode(self):
        expression = self.input_text.get().strip()
        if expression:
            try:
                parts = expression.rsplit(',', 1)
                if len(parts) != 2:
                    raise ValueError("Please enter the equation followed by the dependent function, separated by a comma.")

                equation = parts[0].strip()
                func = parts[1].strip()

                print(f"Input equation: {equation}")
                print(f"Function: {func}")

                if not equation or not func:
                    raise ValueError("Both the equation and function name must be provided and non-empty.")

                result, steps = self.computer.ode_solver(equation, func)
                self.last_steps = steps
                self.display_result(f"ODE Solution: {result}")
                self.display_steps()
                self.statusbar.config(text="ODE solution completed successfully.")
                self.save_computation_to_db(expression, result, steps, "ode_solver")  
            except ValueError as ve:
                messagebox.showerror("Input Error", f"Input format error: {ve}")
                self.statusbar.config(text="Input error.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.statusbar.config(text="Error in ODE solution.")
        self.update_history()
  
    def solve_tangent(self):
        expression = self.input_text.get().strip()
        if expression:
            try:
                function, symbol, point = expression.split(',')
                result, steps = self.computer.tangent_line(function.strip(), symbol.strip(), float(point.strip()))
                self.last_steps = steps
                self.display_result(f"Tangent Line: {result}")
                self.display_steps()
                self.plot_tangent(function.strip(), symbol.strip(), float(point.strip()), result)
                self.statusbar.config(text="Tangent line calculation and graph completed successfully.")
                self.save_computation_to_db(expression, result, steps, "tangent_line") 
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.statusbar.config(text="Error in tangent line calculation.")
        self.update_history()

    def plot_tangent(self, function, symbol, point, tangent):
        try:
            plt.close('all')

            sym = sp.Symbol(symbol)
            func_expr = sp.sympify(function)
            tangent_expr = sp.sympify(tangent)

            func_lambda = sp.lambdify(sym, func_expr, "numpy")
            tangent_lambda = sp.lambdify(sym, tangent_expr, "numpy")

            x_vals = np.linspace(point - 10, point + 10, 400)
            func_vals = func_lambda(x_vals)
            tangent_vals = tangent_lambda(x_vals)

            plt.figure(figsize=(10, 6))
            plt.plot(x_vals, func_vals, label=f'Function: {function}')
            plt.plot(x_vals, tangent_vals, label=f'Tangent at {symbol} = {point}', linestyle='--')
            plt.scatter([point], [func_lambda(point)], color='red', label=f'Point of Tangency ({point}, {func_lambda(point)})')

            plt.title("Function and Tangent Line")
            plt.xlabel(symbol)
            plt.ylabel('y')
            plt.legend()
            plt.grid(True)
            
            plt.show()

        except Exception as e:
            messagebox.showerror("Plotting Error", f"Failed to plot the graph: {e}")

    def solve_line(self):
        expression = self.input_text.get().strip()
        if expression:
            try:
                self.computer.clear_steps()
                
                if '=' not in expression:
                    raise ValueError("The equation must contain an '=' sign.")
                
                lhs, rhs = expression.split('=')
                lhs_expr = sp.sympify(lhs.strip())
                rhs_expr = sp.sympify(rhs.strip())

                self.computer.add_step(f"**Step 1:** Start with the equation: {lhs} = {rhs}")

                lhs_expanded = sp.expand(lhs_expr)
                rhs_expanded = sp.expand(rhs_expr)
                self.computer.add_step(f"**Step 2:** Expand both sides:\n   LHS: {lhs_expanded}\n   RHS: {rhs_expanded}")

                equation = lhs_expanded - rhs_expanded
                self.computer.add_step(f"**Step 3:** Move all terms to one side to set the equation to 0:\n   {equation} = 0")

                simplified_eq = sp.simplify(equation)
                self.computer.add_step(f"**Step 4:** Simplify the equation:\n   {simplified_eq} = 0")

                if simplified_eq == 0:
                    raise ValueError("The equation simplifies to 0 = 0, which indicates that it is either an identity or has no solution.")
                if isinstance(simplified_eq, (sp.Integer, sp.Float)) and simplified_eq != 0:
                    raise ValueError("The equation simplifies to a contradiction, meaning there is no solution.")

                solution = sp.solve(simplified_eq, dict=True)
                self.computer.add_step(f"**Step 5:** Solve the equation for the variable(s):\n   Solution: {solution}")

                self.last_steps = self.computer.get_steps()
                self.display_result(f"Line Solution: {solution}")
                self.display_steps()
                self.statusbar.config(text="Line equation solved successfully.")
                self.save_computation_to_db(expression, solution, self.last_steps, "line_solver")

            except ValueError as ve:
                messagebox.showerror("Input Error", f"Input format error: {ve}")
                self.statusbar.config(text="Input error.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.statusbar.config(text="Error in line solution.")
        self.update_history()

    def simplify(self):
        expression = self.input_text.get().strip()
        if expression:
            try:
                result, steps = self.computer.evaluate_expression(expression)
                simplified_result = sp.simplify(result)
                self.last_steps = steps
                self.display_result(f"Simplified Result: {simplified_result}")
                self.display_steps()
                self.statusbar.config(text="Simplification completed successfully.")
                self.save_computation_to_db(expression, simplified_result, steps, "simplification")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.statusbar.config(text="Error in simplification.")
        self.update_history()

    def save_computation_to_db(self, expression, result, steps, computation_type):
        user_id = self.controller.auth_service.current_user_id
        if user_id:
            logging.debug(f"Saving computation with: expression={expression}, result={result}, steps={steps}, computation_type={computation_type}")
            entry = {
                'user_id': user_id,
                'expression': expression,
                'result': str(result), 
                'computation_type': computation_type,
                'symbolic_steps': json.dumps(steps),
                'timestamp': datetime.datetime.now().isoformat()
            }
            logging.debug(f"Formatted entry: {entry}")
            self.controller.computation_history.add_entry(entry)
            messagebox.showinfo("Success", "Computation saved successfully!")
        else:
            messagebox.showerror("Error", "User not logged in. Cannot save computation.")

    def display_result(self, text):
        self.result_tab.config(state=tk.NORMAL)
        self.result_tab.delete("1.0", tk.END)
        self.result_tab.insert(tk.END, text)
        self.result_tab.config(state=tk.DISABLED)

    def display_steps(self):
        if hasattr(self, 'last_steps') and self.last_steps:
            steps = self.last_steps
            self.step_tab.config(state=tk.NORMAL)
            self.step_tab.delete("1.0", tk.END)
            self.step_tab.insert(tk.END, steps)
            self.step_tab.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("Info", "No steps available. Please perform a calculation first.")

    def undo(self):
        current_input = self.input_text.get().strip()

        if self.history:
            if not self.future or self.future[-1] != current_input:
                self.future.append(current_input)

            last_input = self.history.pop()
            self.input_text.delete(0, tk.END)
            self.input_text.insert(0, last_input)
            self.statusbar.config(text="Undo performed.")
        else:
            self.statusbar.config(text="Nothing to undo.")

    def redo(self):
        current_input = self.input_text.get().strip()

        if self.future:
            if not self.history or self.history[-1] != current_input:
                self.history.append(current_input)

            next_input = self.future.pop()
            self.input_text.delete(0, tk.END)
            self.input_text.insert(0, next_input)
            self.statusbar.config(text="Redo performed.")
        else:
            self.statusbar.config(text="Nothing to redo.")

    def save_solution(self):
        file_types = [("PDF files", "*.pdf"), ("PNG files", "*.png"), ("Text files", "*.txt")]
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=file_types)
        if file_path:
            try:
                if file_path.endswith('.pdf'):
                    self.save_as_pdf(file_path)
                elif file_path.endswith('.png'):
                    self.save_as_image(file_path)
                elif file_path.endswith('.txt'):
                    self.save_as_text(file_path)
            except Exception as e:
                messagebox.showerror("Save Solution", f"Error saving solution: {e}")

    def save_as_pdf(self, file_path):
        try:
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter

            c.setFont("Helvetica", 12)
            textobject = c.beginText(40, height - 40)

            content = self.result_tab.get("1.0", tk.END)

            for line in content.splitlines():
                textobject.textLine(line)

            c.drawText(textobject)
            c.showPage()
            c.save()

            self.statusbar.config(text=f"Solution saved as PDF: {file_path}")
        except Exception as e:
            messagebox.showerror("Save Solution", f"Error saving as PDF: {e}")

    def save_as_image(self, file_path):
        try:
            self.result_tab.update()
            x = self.result_tab.winfo_rootx()
            y = self.result_tab.winfo_rooty()
            width = self.result_tab.winfo_width()
            height = self.result_tab.winfo_height()
            ImageGrab.grab().crop((x, y, x + width, y + height)).save(file_path)
            self.statusbar.config(text=f"Solution saved as image: {file_path}")
        except Exception as e:
            messagebox.showerror("Save Solution", f"Error saving as image: {e}")

    def save_as_text(self, file_path):
        try:
            with open(file_path, 'w') as file:
                file.write("Symbolic Computation Result\n\n")
                file.write(self.result_tab.get("1.0", tk.END))
                file.write("\nStep-by-Step Solution:\n")
                file.write(self.step_tab.get("1.0", tk.END))
            self.statusbar.config(text=f"Solution saved as text: {file_path}")
        except Exception as e:
            messagebox.showerror("Save Solution", f"Error saving as text: {e}")

    def load(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, "r") as file:
                    content = file.read()
                    self.input_text.delete(0, tk.END)
                    self.input_text.insert(0, content)
                self.statusbar.config(text=f"Loaded content from: {file_path}")
            except Exception as e:
                messagebox.showerror("Load", f"Error loading file: {e}")

    def update_history(self):
        current_input = self.input_text.get().strip()
        if not self.history or self.history[-1] != current_input:
            self.history.append(current_input)
        self.future.clear()
