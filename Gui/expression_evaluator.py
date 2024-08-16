import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class ExpressionInputFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style='ExpressionInput.TFrame', padding=(20, 20))
        self.controller = controller
        
        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the expression input frame."""
        header_frame = ttk.Frame(self, padding=(10, 10))
        header_frame.grid(row=0, column=0, columnspan=3, pady=(10, 20), sticky="ew")
        
        ttk.Label(header_frame, text="Enter a problem", font=("Helvetica", 14), foreground="#2c3e50").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.expression_entry = ttk.Entry(header_frame, font=("Helvetica", 14), width=50)
        self.expression_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        eval_button = ttk.Button(header_frame, text="Go", command=self.evaluate_expression, style='Sidebar.TButton')
        eval_button.grid(row=0, column=2, padx=10, pady=10)

        # Removed the camera and keyboard icon buttons as they were causing issues

        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky="nsew")
        
        canvas = tk.Canvas(content_frame)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        examples_frame = ttk.Frame(scrollable_frame, padding=(10, 10))
        examples_frame.grid(row=0, column=0, pady=(10, 20), sticky="ew")

        ttk.Label(examples_frame, text="Equation Examples", font=("Helvetica", 14), foreground="#2c3e50").grid(row=0, column=0, padx=10, pady=5, sticky="w")

        example_1 = ttk.Label(examples_frame, text="5x - 6 = 3x - 8", font=("Helvetica", 12))
        example_1.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        example_2 = ttk.Label(examples_frame, text="x² - x - 6 = 0", font=("Helvetica", 12))
        example_2.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        example_3 = ttk.Label(examples_frame, text="x⁴ - 5x² + 4 = 0", font=("Helvetica", 12))
        example_3.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        description_frame = ttk.Frame(scrollable_frame, padding=(10, 10))
        description_frame.grid(row=1, column=0, pady=(10, 20), sticky="ew")

        description_label = ttk.Label(description_frame, text="Solve linear, quadratic, biquadratic, absolute, and radical equations, step-by-step.", font=("Helvetica", 12))
        description_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        save_frame = ttk.Frame(self, padding=(10, 10))
        save_frame.grid(row=2, column=0, pady=(20, 10), sticky="ew")

        save_button = ttk.Button(save_frame, text="Save Output", command=self.save_output, style='Sidebar.TButton')
        save_button.grid(row=0, column=0, padx=10, pady=10)

        export_pdf_button = ttk.Button(save_frame, text="Export as PDF", command=self.export_as_pdf, style='Sidebar.TButton')
        export_pdf_button.grid(row=0, column=1, padx=10, pady=10)

        export_image_button = ttk.Button(save_frame, text="Export as Image", command=self.export_as_image, style='Sidebar.TButton')
        export_image_button.grid(row=0, column=2, padx=10, pady=10)

    def evaluate_expression(self):
        """Evaluate the mathematical expression provided by the user."""
        expression = self.expression_entry.get()
        try:
            result, steps = self.controller.evaluator.evaluate(expression)
            result_text = f"Result: {result}\n\nSteps:\n{steps}"
            self.controller.display_result(result_text, self.controller.success_color)
        except Exception as e:
            self.controller.display_error_popup(f"Error evaluating expression: {e}")

    def save_output(self):
        """Save the current output to a file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write("Your output goes here...")
                messagebox.showinfo("Save Output", "Output saved successfully!")
            except Exception as e:
                messagebox.showerror("Save Output", f"Failed to save output: {e}")

    def export_as_pdf(self):
        """Export the current output as a PDF."""
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")])
        if file_path:
            try:
                pdf_canvas = canvas.Canvas(file_path, pagesize=letter)
                width, height = letter
                text = "Your output goes here..."
                pdf_canvas.setFont("Helvetica", 12)
                pdf_canvas.drawString(100, height - 100, text)
                pdf_canvas.save()
                messagebox.showinfo("Export as PDF", "Output exported as PDF successfully!")
            except Exception as e:
                messagebox.showerror("Export as PDF", f"Failed to export as PDF: {e}")

    def export_as_image(self):
        """Export the current output as an image."""
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg"), ("All Files", "*.*")])
        if file_path:
            try:
                # Just a placeholder, you can replace this with actual widget area capture if needed.
                messagebox.showinfo("Export as Image", "This function has been disabled due to errors with image handling.")
            except Exception as e:
                messagebox.showerror("Export as Image", f"Failed to export as image: {e}")

