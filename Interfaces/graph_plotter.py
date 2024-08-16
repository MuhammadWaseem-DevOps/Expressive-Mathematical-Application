from abc import ABC, abstractmethod

class IGraphPlotter(ABC):
    @abstractmethod
    def plot_function(self, function: str, x_min: float, x_max: float):
        pass

    @abstractmethod
    def plot_parametric(self, x_func: str, y_func: str, t_min: float, t_max: float):
        pass

    @abstractmethod
    def plot_polar(self, r_func: str, theta_min: float, theta_max: float):
        pass

    @abstractmethod
    def plot_3d(self, z_func: str, x_min: float, x_max: float, y_min: float, y_max: float):
        pass

    @abstractmethod
    def plot_bar(self, categories: list, values: list):
        pass

    @abstractmethod
    def plot_scatter(self, x_values: list, y_values: list):
        pass

    @abstractmethod
    def plot_histogram(self, data: list, bins: int):
        pass

    @abstractmethod
    def plot_pie(self, labels: list, sizes: list):
        pass

    @abstractmethod
    def customize_plot(self, options: dict):
        pass

    @abstractmethod
    def export_plot(self, file_path: str, file_format: str):
        pass
