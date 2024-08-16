import tkinter as tk
from tkinter import ttk
from Services.graph_plotter import GraphPlotter

class GraphPlotterFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('GraphPlotter.TFrame', background='#f0f0f0')
        self.style.configure('Sidebar.TButton', padding=6, font=("Helvetica", 10))
        self.style.configure('Sidebar.TFrame', background='#2c3e50')
        self.style.configure('Zoom.TButton', padding=6, font=("Helvetica", 10))

        # Create sidebar frame
        self.sidebar_frame = ttk.Frame(self, width=200, style='Sidebar.TFrame')
        self.sidebar_frame.grid(row=0, column=0, sticky="ns")

        # Add entries and buttons to the sidebar
        ttk.Label(self.sidebar_frame, text="Function:", font=("Helvetica", 12), foreground="#ecf0f1", background='#2c3e50').grid(row=0, column=0, padx=10, pady=(10, 5), sticky=tk.W)
        self.function_entry = ttk.Entry(self.sidebar_frame, font=("Helvetica", 12))
        self.function_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(self.sidebar_frame, text="X Min:", font=("Helvetica", 12), foreground="#ecf0f1", background='#2c3e50').grid(row=2, column=0, padx=10, pady=(10, 5), sticky=tk.W)
        self.x_min_entry = ttk.Entry(self.sidebar_frame, font=("Helvetica", 12))
        self.x_min_entry.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(self.sidebar_frame, text="X Max:", font=("Helvetica", 12), foreground="#ecf0f1", background='#2c3e50').grid(row=4, column=0, padx=10, pady=(10, 5), sticky=tk.W)
        self.x_max_entry = ttk.Entry(self.sidebar_frame, font=("Helvetica", 12))
        self.x_max_entry.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

        plot_button = ttk.Button(self.sidebar_frame, text="Plot", command=self.plot_graph, style='Sidebar.TButton')
        plot_button.grid(row=6, column=0, padx=10, pady=(20, 10), sticky="ew")

        # Create the main plot canvas
        self.plot_canvas = tk.Canvas(self, bg='#ffffff')
        self.plot_canvas.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Create an instance of GraphPlotter, passing the Canvas
        self.graph_plotter = GraphPlotter(self.plot_canvas)

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
            x_min = float(self.x_min_entry.get())
            x_max = float(self.x_max_entry.get())
            self.graph_plotter.plot_function(function, x_min, x_max)
            self.status_display.config(text="Graph plotted successfully.")
        except Exception as e:
            self.status_display.config(text=f"Error: {str(e)}", foreground="red")

    def on_resize(self, event):
        """Redraw the grid when the canvas is resized."""
        self.draw_grid()
        self.graph_plotter.figure.set_size_inches(self.plot_canvas.winfo_width()/100, self.plot_canvas.winfo_height()/100)
        self.graph_plotter.plot_canvas.draw()

    def zoom_in(self):
        """Handle zooming in."""
        self.graph_plotter.zoom_in()

    def zoom_out(self):
        """Handle zooming out."""
        self.graph_plotter.zoom_out()
