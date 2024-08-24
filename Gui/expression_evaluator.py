import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk

class ExpressionInputFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Configure the grid layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=2)  # Give more weight to the text output column
        self.grid_columnconfigure(1, weight=1)  # Ensure the image gets resized appropriately

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the expression input frame."""
        header_frame = ttk.Frame(self, padding=(10, 10))
        header_frame.grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(header_frame, text="Enter a problem", font=("Helvetica", 14), foreground="#2c3e50").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.expression_entry = ttk.Entry(header_frame, font=("Helvetica", 14))
        self.expression_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        eval_button = ttk.Button(header_frame, text="Go", command=self.evaluate_expression, style='Sidebar.TButton')
        eval_button.grid(row=0, column=2, padx=10, pady=10)

        # Scrolled output frame to display the result and steps
        self.output_text = ScrolledText(self, wrap='word', height=10, font=("Helvetica", 12))
        self.output_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.output_text.config(state='disabled')  # Initially disable the output area

        # Frame to display AST image
        self.tree_image_label = ttk.Label(self)
        self.tree_image_label.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        save_frame = ttk.Frame(self, padding=(10, 10))
        save_frame.grid(row=2, column=0, columnspan=2, pady=(20, 10), sticky="ew")
        save_frame.grid_columnconfigure((0, 1, 2), weight=1)

        save_button = ttk.Button(save_frame, text="Save Output", command=self.save_output, style='Sidebar.TButton')
        save_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        export_pdf_button = ttk.Button(save_frame, text="Export as PDF", command=self.export_as_pdf, style='Sidebar.TButton')
        export_pdf_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        export_image_button = ttk.Button(save_frame, text="Export as Image", command=self.export_as_image, style='Sidebar.TButton')
        export_image_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        # Bind resizing event to update the image size
        self.tree_image_label.bind('<Configure>', self.resize_image)

    def evaluate_expression(self):
        """Evaluate the mathematical expression provided by the user and display the result."""
        self.clear_output()  # Clear previous output first

        expression = self.expression_entry.get()
        if not expression:
            self.display_error_popup("Please enter an expression to evaluate.")
            return

        try:
            # Assuming controller has an evaluator instance
            result, steps, ast_image = self.controller.evaluator.evaluate(expression)

            # Now update the text and image with the new evaluation result
            result_text = f"Result: {result}\n\nSteps:\n{steps}"
            self.display_result(result_text)

            # Display the AST image
            self.ast_image = ast_image  # Save the original image for resizing
            self.display_ast_image()

            # Save the result to the computation history
            self.save_to_history(expression, result, steps)

        except Exception as e:
            self.display_error_popup(f"Error evaluating expression: {e}")

    def clear_output(self):
        """Clear the output area."""
        # Enable the text widget to allow clearing
        self.output_text.config(state='normal')
        
        # Clear the text widget
        self.output_text.delete('1.0', tk.END)
        
        # Disable the text widget after clearing
        self.output_text.config(state='disabled')

        # Clear the image
        self.tree_image_label.config(image='')
        self.ast_image = None

    def display_result(self, result_text):
        """Display the result in the output_text widget."""
        # Enable the text widget
        self.output_text.config(state='normal')
        
        # Insert the new result text
        self.output_text.insert(tk.END, result_text)
        
        # Disable the text widget to prevent editing
        self.output_text.config(state='disabled')

    def display_ast_image(self):
        """Display the AST image."""
        if self.ast_image:
            # Resize the image to fit the label size
            label_width = self.tree_image_label.winfo_width()
            label_height = self.tree_image_label.winfo_height()

            if label_width > 1 and label_height > 1:  # Check if the label size is valid
                # Ensure image maintains aspect ratio
                img_ratio = self.ast_image.width / self.ast_image.height
                label_ratio = label_width / label_height

                if label_ratio > img_ratio:
                    # Height is the constraining dimension
                    new_height = label_height
                    new_width = int(new_height * img_ratio)
                else:
                    # Width is the constraining dimension
                    new_width = label_width
                    new_height = int(new_width / img_ratio)

                resized_image = self.ast_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(resized_image)
                
                self.tree_image_label.config(image=photo)
                self.tree_image_label.image = photo  # Keep a reference to avoid garbage collection

    def resize_image(self, event):
        """Handle resizing of the image when the label size changes."""
        self.display_ast_image()

    def save_to_history(self, expression, result, steps):
        """Save the evaluation result and steps to the computation history."""
        self.controller.evaluator.save_to_history(expression, result, steps)

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

    def clear_all(self):
        """Clear both the input field and the output area."""
        self.expression_entry.delete(0, tk.END)  # Clear the input entry field
        self.clear_output()  # Clear the output area

    def on_frame_show(self):
        """Method to be called when the frame is shown to ensure fields are cleared."""
        self.clear_all()
