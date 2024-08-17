import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class ExpressionInputFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Configure the grid layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the expression input frame."""
        header_frame = ttk.Frame(self, padding=(10, 10))
        header_frame.grid(row=0, column=0, pady=(10, 20), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(header_frame, text="Enter a problem", font=("Helvetica", 14), foreground="#2c3e50").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.expression_entry = ttk.Entry(header_frame, font=("Helvetica", 14))
        self.expression_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        eval_button = ttk.Button(header_frame, text="Go", command=self.evaluate_expression, style='Sidebar.TButton')
        eval_button.grid(row=0, column=2, padx=10, pady=10)

        # Output frame to display the result and steps
        self.output_text = tk.Text(self, wrap='word', height=10, state='disabled', font=("Helvetica", 12))
        self.output_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        save_frame = ttk.Frame(self, padding=(10, 10))
        save_frame.grid(row=2, column=0, pady=(20, 10), sticky="ew")
        save_frame.grid_columnconfigure((0, 1, 2), weight=1)

        save_button = ttk.Button(save_frame, text="Save Output", command=self.save_output, style='Sidebar.TButton')
        save_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        export_pdf_button = ttk.Button(save_frame, text="Export as PDF", command=self.export_as_pdf, style='Sidebar.TButton')
        export_pdf_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        export_image_button = ttk.Button(save_frame, text="Export as Image", command=self.export_as_image, style='Sidebar.TButton')
        export_image_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

    def evaluate_expression(self):
        """Evaluate the mathematical expression provided by the user and display the result."""
        expression = self.expression_entry.get()
        try:
            # Assuming controller has an evaluator instance
            result, steps = self.controller.evaluator.evaluate(expression)
            result_text = f"Result: {result}\n\nSteps:\n{steps}"
            self.display_result(result_text)
        except Exception as e:
            self.display_error_popup(f"Error evaluating expression: {e}")

    def display_result(self, result_text):
        """Display the result in the output_text widget."""
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, result_text)
        self.output_text.config(state='disabled')

    def display_error_popup(self, message):
        """Display an error message in a popup dialog."""
        messagebox.showerror("Error", message)

    def save_output(self):
        """Save the current output to a file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(self.output_text.get(1.0, tk.END))  # Save the displayed result
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
                
                text = self.output_text.get(1.0, tk.END).strip()
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
                messagebox.showinfo("Export as Image", "This function has been disabled due to errors with image handling.")
            except Exception as e:
                messagebox.showerror("Export as Image", f"Failed to export as image: {e}")
