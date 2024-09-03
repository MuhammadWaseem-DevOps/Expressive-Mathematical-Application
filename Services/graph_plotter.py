import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import datetime
import json
import io
import re

class GraphPlotter:
    def __init__(self, canvas, dao, user_id):
        self.canvas = canvas
        self.figure = plt.Figure()
        self.ax = self.figure.add_subplot(111)
        self.plot_canvas = FigureCanvasTkAgg(self.figure, self.canvas)
        self.plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.dao = dao
        self.user_id = user_id
        
        if self.user_id is None:
            raise ValueError("User ID is None. Please ensure it is passed correctly.")

    def _prepare_function(self, function: str) -> str:
        """Convert user-friendly mathematical functions to NumPy equivalents."""
        replacements = {
            r'\bsin\b': 'np.sin',
            r'\bcos\b': 'np.cos',
            r'\btan\b': 'np.tan',
            r'\blog\b': 'np.log',
            r'\bexp\b': 'np.exp',
            r'\bsqrt\b': 'np.sqrt',
            r'\^': '**', 
            r'(\d)([a-zA-Z\(])': r'\1*\2' 
        }

        for pattern, replacement in replacements.items():
            function = re.sub(pattern, replacement, function)

        return function

    def plot_function(self, function: str, variable: str, x_min: float, x_max: float, function_type: str, units: str = None):
        function = self._prepare_function(function)
        x = np.linspace(x_min, x_max, 400)
        
        if function_type == "Trigonometric" and units == "Degrees":
            x = np.deg2rad(x)
        
        try:
            y = eval(function, {"np": np, variable: x})
        except Exception as e:
            raise ValueError(f"Error in evaluating the function: {e}")
        
        self.ax.clear()
        self.ax.plot(x, y)
        self.ax.set_title(f"{function_type} Function: {function}")
        self.ax.set_xlabel(variable)
        self.ax.set_ylabel("y")
        self.ax.grid(True)
        self.plot_canvas.draw()
        self.save_graph_data(function, x_min, x_max)

    def plot_implicit(self, function: str, x_min: float, x_max: float, y_min: float, y_max: float):
        function = self._prepare_function(function)
        x = np.linspace(x_min, x_max, 400)
        y = np.linspace(y_min, y_max, 400)
        X, Y = np.meshgrid(x, y)

        try:
            Z = eval(function, {"np": np, "X": X, "Y": Y, "x": X, "y": Y})
        except Exception as e:
            raise ValueError(f"Error in evaluating the implicit function: {e}")
        
        self.ax.clear()
        self.ax.contour(X, Y, Z, levels=[0], colors='black')
        self.ax.set_title(f"Implicit Plot: {function}")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        self.ax.grid(True)
        self.plot_canvas.draw()
        self.save_graph_data(function, x_min, x_max)

    def save_graph_data(self, function: str, x_min: float, x_max: float):
        """Save the graph data to the database."""
        plot_settings = {
            'x_min': x_min,
            'x_max': x_max,
        }
        
        buffer = io.BytesIO()
        self.figure.savefig(buffer, format='png')
        image_data = buffer.getvalue()
        buffer.close()

        graph_entry = {
            'user_id': self.user_id,
            'function': function,
            'x_min': x_min,
            'x_max': x_max,
            'timestamp': datetime.datetime.now().isoformat(),
            'image': image_data
        }
        graph_data_id = self.dao.insert('GRAPHICAL_FUNCTION', graph_entry)

        history_entry = {
            'user_id': self.user_id,
            'expression': function,
            'result': 'Graph plotted',
            'computation_type': 'Graphical Function',
            'timestamp': datetime.datetime.now().isoformat(),
            'symbolic_steps': json.dumps(plot_settings),
            'graph_data_id': graph_data_id
        }
        self.dao.insert('COMPUTATION_HISTORY', history_entry)

    def zoom_in(self):
        self.ax.set_xlim(self.ax.get_xlim()[0] / 1.5, self.ax.get_xlim()[1] / 1.5)
        self.ax.set_ylim(self.ax.get_ylim()[0] / 1.5, self.ax.get_ylim()[1] / 1.5)
        self.plot_canvas.draw()

    def zoom_out(self):
        self.ax.set_xlim(self.ax.get_xlim()[0] * 1.5, self.ax.get_xlim()[1] * 1.5)
        self.ax.set_ylim(self.ax.get_ylim()[0] * 1.5, self.ax.get_ylim()[1] * 1.5)
        self.plot_canvas.draw()

    def plot_3d(self, z_func: str, x_min: float, x_max: float, y_min: float, y_max: float):
        from mpl_toolkits.mplot3d import Axes3D
        x = np.linspace(x_min, x_max, 100)
        y = np.linspace(y_min, y_max, 100)
        x, y = np.meshgrid(x, y)
        z_func = self._prepare_function(z_func)
        try:
            z = eval(z_func, {"np": np, "x": x, "y": y})
        except Exception as e:
            print(f"Error in evaluating the 3D function: {e}")
            return
        self.ax.clear()
        self.ax = self.figure.add_subplot(111, projection='3d')
        self.ax.plot_surface(x, y, z, cmap='viridis')
        self.ax.set_title("3D Plot")
        self.plot_canvas.draw()

    def customize_plot(self, options: dict):
        if 'title' in options:
            self.ax.set_title(options['title'])
        if 'xlabel' in options:
            self.ax.set_xlabel(options['xlabel'])
        if 'ylabel' in options:
            self.ax.set_ylabel(options['ylabel'])
        if 'xlim' in options:
            self.ax.set_xlim(options['xlim'])
        if 'ylim' in options:
            self.ax.set_ylim(options['ylim'])
        self.plot_canvas.draw()

    def export_plot(self, file_path: str, file_format: str = 'png'):
        self.figure.savefig(file_path, format=file_format)
