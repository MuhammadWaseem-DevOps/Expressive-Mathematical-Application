import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import ImageGrab
import pdfkit
from Services.symbolic_computer import SymbolicComputer
import sympy as sp

class SymbolicComputation(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller

        # Initialize the symbolic computation components
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
        input_frame.pack(side=tk.LEFT, padx=10)

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

        dropdown = ttk.Combobox(button_frame, values=["See All", "Derivative", "Integral", "Limit", "ODE Solver", "PDE Solver"])
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
        elif selected == "PDE Solver":
            self.solve_pde()

    def solve(self):
        expression = self.input_text.get().strip()
        if expression:
            try:
                result, steps = self.computer.evaluate_expression(expression)
                self.last_steps = steps  # Store steps for later display
                self.display_result(f"Result: {result}")
                self.display_steps()
                self.statusbar.config(text="Calculation completed successfully.")
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
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.statusbar.config(text="Error in limit calculation.")
        self.update_history()

    def solve_ode(self):
        expression = self.input_text.get().strip()
        if expression:
            try:
                equation, func = expression.split(',')
                result, steps = self.computer.ode_solver(equation.strip(), func.strip())
                self.last_steps = steps
                self.display_result(f"ODE Solution: {result}")
                self.display_steps()
                self.statusbar.config(text="ODE solution completed successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.statusbar.config(text="Error in ODE solution.")
        self.update_history()

    def solve_pde(self):
        expression = self.input_text.get().strip()
        if expression:
            try:
                equation, func = expression.split(',')
                eq = sp.sympify(equation)
                result, steps = self.computer.pde_solver(eq, func.strip())
                self.last_steps = steps
                self.display_result(f"PDE Solution: {result}")
                self.display_steps()
                self.statusbar.config(text="PDE solution completed successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.statusbar.config(text="Error in PDE solution.")
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
                self.statusbar.config(text="Tangent line calculation completed successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.statusbar.config(text="Error in tangent line calculation.")
        self.update_history()

    def solve_line(self):
        expression = self.input_text.get().strip()
        if expression:
            try:
                self.display_result("Line feature not implemented yet.")
                self.statusbar.config(text="Line feature not implemented yet.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.statusbar.config(text="Error in line calculation.")
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
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.statusbar.config(text="Error in simplification.")
        self.update_history()

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
        if self.history:
            self.future.append(self.input_text.get().strip())
            last_input = self.history.pop()
            self.input_text.delete(0, tk.END)
            self.input_text.insert(0, last_input)
            self.statusbar.config(text="Undo performed.")
        else:
            self.statusbar.config(text="Nothing to undo.")

    def redo(self):
        if self.future:
            self.history.append(self.input_text.get().strip())
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
            html = self.result_tab.get("1.0", tk.END)
            pdfkit.from_string(html, file_path)
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
