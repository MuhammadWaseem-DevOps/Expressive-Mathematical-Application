import unittest
from unittest.mock import Mock
import numpy as np
import tkinter as tk
from Services.graph_plotter import GraphPlotter  

class TestGraphPlotter(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root)
        self.mock_dao = Mock()
        self.user_id = 1  
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

        self.plotter.save_graph_data = Mock()
        self.plotter.save_graph_data(function, -10, 10)

        self.plotter.save_graph_data.assert_called_once_with(function, -10, 10)

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

