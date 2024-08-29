import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from Services.graph_plotter import GraphPlotter

class GraphPlotterFrame(ttk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

        # Configure styles
        self.style = ttk.Style()
        self.style.configure('GraphPlotter.TFrame', background='#f0f0f0')
        self.style.configure('Sidebar.TButton', padding=6, font=("Helvetica", 10))
        self.style.configure('Sidebar.TFrame', background='#2c3e50')
        self.style.configure('Zoom.TButton', padding=6, font=("Helvetica", 10))

        # Create sidebar frame
        self.sidebar_frame = ttk.Frame(self, width=250, style='Sidebar.TFrame')
        self.sidebar_frame.grid(row=0, column=0, sticky="ns")

        # Add entries and buttons to the sidebar
        ttk.Label(self.sidebar_frame, text="Function:", font=("Helvetica", 12), foreground="#ecf0f1", background='#2c3e50').grid(row=0, column=0, padx=10, pady=(10, 5), sticky=tk.W)
        self.function_entry = ttk.Entry(self.sidebar_frame, font=("Helvetica", 12))
        self.function_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(self.sidebar_frame, text="Variable (x/y):", font=("Helvetica", 12), foreground="#ecf0f1", background='#2c3e50').grid(row=2, column=0, padx=10, pady=(10, 5), sticky=tk.W)
        self.variable_entry = ttk.Entry(self.sidebar_frame, font=("Helvetica", 12))
        self.variable_entry.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        self.variable_entry.insert(0, "x")

        ttk.Label(self.sidebar_frame, text="Range Start:", font=("Helvetica", 12), foreground="#ecf0f1", background='#2c3e50').grid(row=4, column=0, padx=10, pady=(10, 5), sticky=tk.W)
        self.range_start_entry = ttk.Entry(self.sidebar_frame, font=("Helvetica", 12))
        self.range_start_entry.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(self.sidebar_frame, text="Range End:", font=("Helvetica", 12), foreground="#ecf0f1", background='#2c3e50').grid(row=6, column=0, padx=10, pady=(10, 5), sticky=tk.W)
        self.range_end_entry = ttk.Entry(self.sidebar_frame, font=("Helvetica", 12))
        self.range_end_entry.grid(row=7, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(self.sidebar_frame, text="Function Type:", font=("Helvetica", 12), foreground="#ecf0f1", background='#2c3e50').grid(row=8, column=0, padx=10, pady=(10, 5), sticky=tk.W)
        self.function_type_combobox = ttk.Combobox(self.sidebar_frame, font=("Helvetica", 12), state="readonly", values=[
            "Linear", "Quadratic", "Cubic", "Polynomial", "Exponential", 
            "Logarithmic", "Trigonometric"
        ])
        self.function_type_combobox.current(0)
        self.function_type_combobox.grid(row=9, column=0, padx=10, pady=5, sticky="ew")

        # Units for trigonometric functions
        self.units_label = ttk.Label(self.sidebar_frame, text="Units (for trig):", font=("Helvetica", 12), foreground="#ecf0f1", background='#2c3e50')
        self.units_label.grid(row=10, column=0, padx=10, pady=(10, 5), sticky=tk.W)
        self.units_combobox = ttk.Combobox(self.sidebar_frame, font=("Helvetica", 12), state="readonly", values=["Radians", "Degrees"])
        self.units_combobox.current(0)
        self.units_combobox.grid(row=11, column=0, padx=10, pady=5, sticky="ew")

        plot_button = ttk.Button(self.sidebar_frame, text="Plot", command=self.plot_graph, style='Sidebar.TButton')
        plot_button.grid(row=12, column=0, padx=10, pady=(20, 10), sticky="ew")

        export_button = ttk.Button(self.sidebar_frame, text="Export", command=self.export_graph, style='Sidebar.TButton')
        export_button.grid(row=13, column=0, padx=10, pady=(10, 10), sticky="ew")

        # Create the main plot canvas
        self.plot_canvas = tk.Canvas(self, bg='#ffffff')
        self.plot_canvas.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Fetch the user ID
        user_id = self.controller.auth_service.get_current_user_id()
        if user_id is None:
            raise ValueError("User ID is None. Please ensure the user is logged in.")

        # Create an instance of GraphPlotter, passing the Canvas, DAO, and user ID
        self.graph_plotter = GraphPlotter(self.plot_canvas, dao=self.controller.dao, user_id=user_id)

        # Bind the resize event to redraw the grid
        self.plot_canvas.bind("<Configure>", self.on_resize)

        # Create zoom control frame
        self.zoom_frame = ttk.Frame(self, style='Sidebar.TFrame')
        self.zoom_frame.grid(row=0, column=2, sticky="ns")
        
        zoom_in_button = ttk.Button(self.zoom_frame, text="+", command=self.zoom_in, style='Zoom.TButton')
        zoom_in_button.grid(row=0, column=0, padx=10, pady=5)
        zoom_out_button = ttk.Button(self.zoom_frame, text="-", command=self.zoom_out, style='Zoom.TButton')
        zoom_out_button.grid(row=1, column=0, padx=10, pady=5)
        settings_button = ttk.Button(self.zoom_frame, text="⚙", style='Zoom.TButton')
        settings_button.grid(row=2, column=0, padx=10, pady=5)

        # Make the plot area expandable
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Status display at the bottom of the plot
        self.status_display = ttk.Label(self, text="", font=("Helvetica", 12), foreground="#2c3e50")
        self.status_display.grid(row=1, column=1, columnspan=5, pady=(10, 20))

        # Draw initial grid
        self.draw_grid()

    def draw_grid(self):
        """Draw a grid on the canvas."""
        self.plot_canvas.delete("grid_line")  # Remove existing grid lines, if any
        width = self.plot_canvas.winfo_width()
        height = self.plot_canvas.winfo_height()
        grid_size = 20

        for i in range(0, width, grid_size):
            self.plot_canvas.create_line([(i, 0), (i, height)], tag='grid_line', fill='#d0d0d0')
        for i in range(0, height, grid_size):
            self.plot_canvas.create_line([(0, i), (width, i)], tag='grid_line', fill='#d0d0d0')

    def plot_graph(self):
        try:
            function = self.function_entry.get()
            variable = self.variable_entry.get().strip()
            range_start = float(self.range_start_entry.get())
            range_end = float(self.range_end_entry.get())
            function_type = self.function_type_combobox.get()
            units = self.units_combobox.get()

            if function_type == "Implicit":
                y_min, y_max = range_start, range_end  # For implicit functions, we need y-range too
                self.graph_plotter.plot_implicit(function, range_start, range_end, y_min, y_max)
            else:
                self.graph_plotter.plot_function(function, variable, range_start, range_end, function_type, units)

            self.status_display.config(text="Graph plotted successfully.")
        except Exception as e:
            self.status_display.config(text=f"Error: {str(e)}", foreground="red")

    def export_graph(self):
        """Export the graph as an image or PDF."""
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[
            ("PNG Image", "*.png"),
            ("PDF Document", "*.pdf"),
            ("All Files", "*.*")
        ])
        if file_path:
            try:
                file_format = file_path.split('.')[-1]
                self.graph_plotter.export_plot(file_path, file_format)
                messagebox.showinfo("Export Successful", f"Graph has been exported as {file_format.upper()}.")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export graph: {str(e)}")

    def on_resize(self, event):
        self.draw_grid()
        self.graph_plotter.figure.set_size_inches(self.plot_canvas.winfo_width()/100, self.plot_canvas.winfo_height()/100)
        self.graph_plotter.plot_canvas.draw()

    def zoom_in(self):
        self.graph_plotter.zoom_in()

    def zoom_out(self):
        self.graph_plotter.zoom_out()
