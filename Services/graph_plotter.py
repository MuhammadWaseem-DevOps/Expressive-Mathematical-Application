import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import datetime
import json
from Interfaces.graph_plotter import IGraphPlotter
import io

class GraphPlotter(IGraphPlotter):
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

    def plot_function(self, function: str, x_min: float, x_max: float):
        x = np.linspace(x_min, x_max, 400)
        try:
            y = eval(function, {"np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan, "exp": np.exp, "sqrt": np.sqrt, "log": np.log}, {"x": x})
        except Exception as e:
            print(f"Error in evaluating the function: {e}")
            return
        self.ax.clear()
        self.ax.plot(x, y)
        self.ax.set_title(f"Plot of {function}")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        self.ax.grid(True, which='both')
        self.ax.spines['left'].set_position('zero')
        self.ax.spines['left'].set_color('black')
        self.ax.spines['left'].set_linewidth(0.5)
        self.ax.spines['bottom'].set_position('zero')
        self.ax.spines['bottom'].set_color('black')
        self.ax.spines['bottom'].set_linewidth(0.5)
        self.ax.spines['right'].set_color('none')
        self.ax.spines['top'].set_color('none')
        self.ax.plot(1, 0, ">k", transform=self.ax.get_yaxis_transform(), clip_on=False)
        self.ax.plot(0, 1, "^k", transform=self.ax.get_xaxis_transform(), clip_on=False)
        self.ax.xaxis.set_ticks_position('bottom')
        self.ax.yaxis.set_ticks_position('left')
        self.plot_canvas.draw()

        # Save the graph data
        self.save_graph_data(function, x_min, x_max)

    def save_graph_data(self, function: str, x_min: float, x_max: float):
        """Save the graph data to the database."""
        plot_settings = {
            'x_min': x_min,
            'x_max': x_max,
        }

        # Save the plot image as a PNG file in memory
        buffer = io.BytesIO()
        self.figure.savefig(buffer, format='png')
        image_data = buffer.getvalue()
        buffer.close()

        # Save graph data in GRAPHICAL_FUNCTION table
        graph_entry = {
            'user_id': self.user_id,
            'function': function,
            'x_min': x_min,
            'x_max': x_max,
            'timestamp': datetime.datetime.now().isoformat(),
            'image': image_data
        }
        graph_data_id = self.dao.insert('GRAPHICAL_FUNCTION', graph_entry)

        # Link to computation history
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

    def plot_parametric(self, x_func: str, y_func: str, t_min: float, t_max: float):
        t = np.linspace(t_min, t_max, 400)
        x = eval(x_func)
        y = eval(y_func)
        self.ax.clear()
        self.ax.plot(x, y)
        self.ax.set_title("Parametric Plot")
        self.plot_canvas.draw()

    def plot_polar(self, r_func: str, theta_min: float, theta_max: float):
        theta = np.linspace(theta_min, theta_max, 400)
        r = eval(r_func)
        self.ax.clear()
        self.ax = self.figure.add_subplot(111, polar=True)
        self.ax.plot(theta, r)
        self.ax.set_title("Polar Plot")
        self.plot_canvas.draw()

    def plot_3d(self, z_func: str, x_min: float, x_max: float, y_min: float, y_max: float):
        from mpl_toolkits.mplot3d import Axes3D
        x = np.linspace(x_min, x_max, 100)
        y = np.linspace(y_min, y_max, 100)
        x, y = np.meshgrid(x, y)
        z = eval(z_func)
        self.ax.clear()
        self.ax = self.figure.add_subplot(111, projection='3d')
        self.ax.plot_surface(x, y, z, cmap='viridis')
        self.ax.set_title("3D Plot")
        self.plot_canvas.draw()

    def plot_bar(self, categories: list, values: list):
        self.ax.clear()
        self.ax.bar(categories, values)
        self.ax.set_title("Bar Chart")
        self.plot_canvas.draw()

    def plot_scatter(self, x_values: list, y_values: list):
        self.ax.clear()
        self.ax.scatter(x_values, y_values)
        self.ax.set_title("Scatter Plot")
        self.plot_canvas.draw()

    def plot_histogram(self, data: list, bins: int):
        self.ax.clear()
        self.ax.hist(data, bins=bins)
        self.ax.set_title("Histogram")
        self.plot_canvas.draw()

    def plot_pie(self, labels: list, sizes: list):
        self.ax.clear()
        self.ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        self.ax.set_title("Pie Chart")
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
