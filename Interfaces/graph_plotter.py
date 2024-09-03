from abc import ABC, abstractmethod

class IGraphPlotter(ABC):
    @abstractmethod
    def plot_function(self, function: str, x_min: float, x_max: float):
        pass

    @abstractmethod
    def plot_parametric(self, x_func: str, y_func: str, t_min: float, t_max: float):
        pass

    @abstractmethod
    def customize_plot(self, options: dict):
        pass

    @abstractmethod
    def export_plot(self, file_path: str, file_format: str):
        pass
