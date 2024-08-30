import unittest
from unittest.mock import Mock
import numpy as np
import tkinter as tk
from Services.graph_plotter import GraphPlotter  # Assuming the class is saved in a file called graph_plotter.py

class TestGraphPlotter(unittest.TestCase):

    def setUp(self):
        # Set up a mock Tkinter canvas and DAO for testing
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root)
        self.mock_dao = Mock()
        self.user_id = 1  # Example user ID
        self.plotter = GraphPlotter(self.canvas, self.mock_dao, self.user_id)

    def test_prepare_function(self):
        function = "sin(x) + log(x)"
        expected_function = "np.sin(x) + np.log(x)"
        prepared_function = self.plotter._prepare_function(function)
        self.assertEqual(prepared_function, expected_function)

    def test_plot_function(self):
        function = "x**2"
        self.plotter.plot_function(function, 'x', -10, 10, 'Polynomial')
        x_data = self.plotter.ax.lines[0].get_xdata()
        y_data = self.plotter.ax.lines[0].get_ydata()

        expected_x = np.linspace(-10, 10, 400)
        expected_y = expected_x ** 2

        np.testing.assert_array_almost_equal(x_data, expected_x)
        np.testing.assert_array_almost_equal(y_data, expected_y)

    def test_plot_function_with_trigonometric_degrees(self):
        function = "sin(x)"
        self.plotter.plot_function(function, 'x', 0, 360, 'Trigonometric', units='Degrees')
        x_data = self.plotter.ax.lines[0].get_xdata()
        y_data = self.plotter.ax.lines[0].get_ydata()

        expected_x = np.deg2rad(np.linspace(0, 360, 400))
        expected_y = np.sin(expected_x)

        np.testing.assert_array_almost_equal(x_data, expected_x)
        np.testing.assert_array_almost_equal(y_data, expected_y)

    def test_plot_implicit(self):
        function = "X**2 + Y**2 - 25"
        self.plotter.plot_implicit(function, -10, 10, -10, 10)
        contours = self.plotter.ax.collections
        self.assertGreater(len(contours), 0)

    def test_save_graph_data(self):
        function = "x**2"
        self.plotter.plot_function(function, 'x', -10, 10, 'Polynomial')

        # Check if the save_graph_data function is called with appropriate parameters
        self.plotter.save_graph_data = Mock()
        self.plotter.save_graph_data(function, -10, 10)

        self.plotter.save_graph_data.assert_called_once_with(function, -10, 10)

        # Verify that data was inserted into the database
        self.mock_dao.insert.assert_called()

    def test_zoom_in(self):
        initial_xlim = self.plotter.ax.get_xlim()
        initial_ylim = self.plotter.ax.get_ylim()

        self.plotter.zoom_in()

        zoomed_xlim = self.plotter.ax.get_xlim()
        zoomed_ylim = self.plotter.ax.get_ylim()

        self.assertLess(zoomed_xlim[1] - zoomed_xlim[0], initial_xlim[1] - initial_xlim[0])
        self.assertLess(zoomed_ylim[1] - zoomed_ylim[0], initial_ylim[1] - initial_ylim[0])

    def test_zoom_out(self):
        initial_xlim = self.plotter.ax.get_xlim()
        initial_ylim = self.plotter.ax.get_ylim()

        self.plotter.zoom_out()

        zoomed_xlim = self.plotter.ax.get_xlim()
        zoomed_ylim = self.plotter.ax.get_ylim()

        self.assertGreater(zoomed_xlim[1] - zoomed_xlim[0], initial_xlim[1] - initial_xlim[0])
        self.assertGreater(zoomed_ylim[1] - zoomed_ylim[0], initial_ylim[1] - initial_ylim[0])

    def test_plot_3d(self):
        z_func = "x**2 + y**2"
        self.plotter.plot_3d(z_func, -5, 5, -5, 5)
        self.assertEqual(len(self.plotter.ax.collections), 1)

    def test_plot_bar(self):
        categories = ['A', 'B', 'C']
        values = [5, 7, 3]
        self.plotter.plot_bar(categories, values)
        self.assertEqual(len(self.plotter.ax.patches), 3)

    def test_plot_scatter(self):
        x_values = [1, 2, 3, 4, 5]
        y_values = [5, 4, 3, 2, 1]
        self.plotter.plot_scatter(x_values, y_values)
        self.assertEqual(len(self.plotter.ax.collections), 1)

    def test_plot_histogram(self):
        data = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
        self.plotter.plot_histogram(data, bins=4)
        self.assertEqual(len(self.plotter.ax.patches), 4)

    def test_plot_pie(self):
        labels = ['A', 'B', 'C']
        sizes = [30, 40, 30]
        self.plotter.plot_pie(labels, sizes)
        self.assertEqual(len(self.plotter.ax.patches), 3)

    def test_customize_plot(self):
        options = {
            'title': 'Custom Title',
            'xlabel': 'Custom X',
            'ylabel': 'Custom Y',
            'xlim': [0, 10],
            'ylim': [0, 100]
        }
        self.plotter.customize_plot(options)

        self.assertEqual(self.plotter.ax.get_title(), 'Custom Title')
        self.assertEqual(self.plotter.ax.get_xlabel(), 'Custom X')
        self.assertEqual(self.plotter.ax.get_ylabel(), 'Custom Y')
        np.testing.assert_array_equal(self.plotter.ax.get_xlim(), options['xlim'])
        np.testing.assert_array_equal(self.plotter.ax.get_ylim(), options['ylim'])

    def test_export_plot(self):
        file_path = 'test_plot.png'
        self.plotter.export_plot(file_path)
        with open(file_path, 'rb') as f:
            self.assertTrue(len(f.read()) > 0)

    def tearDown(self):
        self.root.destroy()

if __name__ == '__main__':
    unittest.main()
