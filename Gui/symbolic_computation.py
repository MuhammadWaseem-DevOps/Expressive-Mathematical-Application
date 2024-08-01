import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk
import customtkinter as ctk
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw, ImageFont

class SymbolicComputation(ctk.CTkFrame):
    def __init__(self, parent, root):
        super().__init__(parent, corner_radius=10, fg_color="#ecf0f1")
        self.parent = parent
        self.root = root

        # Create history stacks for undo and redo
        self.history = []
        self.future = []

        # Main frame configuration
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#ffffff")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Entry widget for input
        self.entry = ctk.CTkTextbox(self.main_frame, height=5, font=("Helvetica", 16), fg_color="#ffffff")
        self.entry.pack(fill=tk.BOTH, padx=10, pady=10)
        self.entry.insert(tk.END, "Enter your symbolic equations here...")

        # Output Area
        self.output_area = ctk.CTkLabel(self.main_frame, text="Results will be shown here...", font=("Helvetica", 14), text_color="#000000", fg_color="#ffffff", anchor="w", wraplength=600)
        self.output_area.pack(fill=tk.BOTH, padx=10, pady=10)

        # Step-by-Step Output Area
        self.step_output_area = ctk.CTkLabel(self.main_frame, text="Step-by-step solution will be shown here...", font=("Helvetica", 14), text_color="#000000", fg_color="#ffffff", anchor="w", wraplength=600)
        self.step_output_area.pack(fill=tk.BOTH, padx=10, pady=10)

        # Create tabbed interface
        self.create_tabs()

        # Control Buttons
        self.create_control_buttons()

        # Plot Area
        self.plot_frame = ctk.CTkFrame(self.main_frame)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.plot_canvas = None

    def create_tabs(self):
        # Create a tab control
        self.tab_control = ttk.Notebook(self.main_frame)
        
        # Define tabs with updated names
        tabs = {
            "Simplification": self.show_simplification,
            "Expansion": self.show_expansion,
            "Factorization": self.show_factorization,
            "Substitution": self.show_substitution,
            "Differentiation": self.show_differentiation,
            "Integration": self.show_integration,
            "Solving Equations": self.show_solving_equations
        }

        # Apply ttkthemes style to tabs
        style = ttk.Style()
        style.theme_use('arc')  # Applying the 'arc' theme from ttkthemes
        style.configure('TNotebook', background='#ecf0f1')
        style.configure('TNotebook.Tab', background='#bdc3c7', padding=[10, 5], font=('Helvetica', 12))
        style.map('TNotebook.Tab', background=[('selected', '#3498db')])

        # Create tabs
        for tab_name in tabs:
            tab_frame = ttk.Frame(self.tab_control)
            self.tab_control.add(tab_frame, text=tab_name)
            tabs[tab_name](tab_frame)

        self.tab_control.pack(expand=1, fill="both")

    def create_control_buttons(self):
        # Create control buttons
        self.control_buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="#ffffff")
        self.control_buttons_frame.pack(fill=tk.X)

        buttons = {
            "Execute": self.execute,
            "Undo": self.undo,
            "Redo": self.redo,
            "Clear": self.clear_all,
            "Save Solution": self.save_solution,
            "Load": self.load
        }

        for text, command in buttons.items():
            button = ctk.CTkButton(
                self.control_buttons_frame,
                text=text,
                command=command,
                height=40,
                corner_radius=10,
                fg_color="#3498db",
                hover_color="#2980b9",
                text_color="#ffffff"
            )
            button.pack(side=tk.LEFT, padx=5, pady=5)

    def show_simplification(self, frame):
        self.setup_interface(frame, "Simplify the expression:")

    def show_expansion(self, frame):
        self.setup_interface(frame, "Expand the expression:")

    def show_factorization(self, frame):
        self.setup_interface(frame, "Factorize the expression:")

    def show_substitution(self, frame):
        self.setup_interface(frame, "Substitute in the expression:")

    def show_differentiation(self, frame):
        self.setup_interface(frame, "Differentiate the expression:")

    def show_integration(self, frame):
        self.setup_interface(frame, "Integrate the expression:")

    def show_solving_equations(self, frame):
        self.setup_interface(frame, "Solve the equations:")

    def setup_interface(self, frame, label_text):
        for widget in frame.winfo_children():
            widget.destroy()
        
        label = ctk.CTkLabel(frame, text=label_text, font=("Helvetica", 14))
        label.pack(pady=10)

        step_button = ctk.CTkButton(
            frame,
            text="Show Step-by-Step",
            command=self.show_step_by_step,
            height=40,
            corner_radius=10,
            fg_color="#3498db",
            hover_color="#2980b9",
            text_color="#ffffff"
        )
        step_button.pack(pady=10)
        # Add widgets like input field, output area, etc. here

    def execute(self):
        # Placeholder for execution logic
        entered_text = self.entry.get("1.0", tk.END).strip()
        self.output_area.configure(text=f"Executed: {entered_text}")

    def show_step_by_step(self):
        # Placeholder for step-by-step solution logic
        entered_text = self.entry.get("1.0", tk.END).strip()
        step_by_step_solution = f"Step-by-step for: {entered_text}\nStep 1: ...\nStep 2: ..."
        self.step_output_area.configure(text=step_by_step_solution)

    def undo(self):
        if self.history:
            self.future.append(self.entry.get("1.0", tk.END).strip())
            self.entry.delete("1.0", tk.END)
            self.entry.insert(tk.END, self.history.pop())
        else:
            tk.messagebox.showinfo("Undo", "Nothing to undo")

    def redo(self):
        if self.future:
            self.history.append(self.entry.get("1.0", tk.END).strip())
            self.entry.delete("1.0", tk.END)
            self.entry.insert(tk.END, self.future.pop())
        else:
            tk.messagebox.showinfo("Redo", "Nothing to redo")

    def clear_all(self):
        self.history.append(self.entry.get("1.0", tk.END).strip())
        self.entry.delete("1.0", tk.END)
        self.future.clear()
        self.output_area.configure(text="Results will be shown here...")
        self.step_output_area.configure(text="Step-by-step solution will be shown here...")

    def save_solution(self):
        step_by_step_solution = self.step_output_area.cget("text")
        if not step_by_step_solution.strip():
            messagebox.showwarning("Save Solution", "No step-by-step solution to save.")
            return

        file_types = [("PDF files", "*.pdf"), ("PNG files", "*.png"), ("All files", "*.*")]
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=file_types)

        if file_path:
            if file_path.endswith('.pdf'):
                self.save_as_pdf(file_path, step_by_step_solution)
            elif file_path.endswith('.png'):
                self.save_as_image(file_path, step_by_step_solution)

    def save_as_pdf(self, file_path, content):
        try:
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            c.drawString(100, height - 100, "Step-by-Step Solution")
            c.drawString(100, height - 120, content)
            c.save()
            messagebox.showinfo("Save Solution", f"Solution saved as PDF: {file_path}")
        except Exception as e:
            messagebox.showerror("Save Solution", f"Error saving as PDF: {e}")

    def save_as_image(self, file_path, content):
        try:
            img = Image.new('RGB', (800, 600), color = (255, 255, 255))
            d = ImageDraw.Draw(img)
            font = ImageFont.load_default()
            d.text((10,10), content, fill=(0,0,0), font=font)
            img.save(file_path)
            messagebox.showinfo("Save Solution", f"Solution saved as image: {file_path}")
        except Exception as e:
            messagebox.showerror("Save Solution", f"Error saving as image: {e}")

    def load(self):
        # Placeholder for load logic
        tk.messagebox.showinfo("Load", "Loaded successfully!")

