import sys
import os

# Ensure the current directory is included in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Controllers.main_controller import MainController
from Services.authentication import AuthenticationService
from Services.expression_evaluator import ExpressionEvaluator
from Services.graph_plotter import GraphPlotter
from Services.symbolic_computer import SymbolicComputer
from Services.profile_manager import ProfileManager
from Services.dao import SQLiteDataAccessObject
from Services.error_handler import ErrorHandler
from Services.computation_history import ComputationHistory
from Services.data_exporter import DataExporter
from Gui.userview import TkinterGUI




if __name__ == "__main__":
    db = None  # Replace with actual database connection
    auth_service = AuthenticationService(db)
    expression_evaluator = ExpressionEvaluator()
    graph_plotter = GraphPlotter()
    symbolic_computer = SymbolicComputer()
    profile_manager = ProfileManager(db)
    data_access_object = SQLiteDataAccessObject(db)
    error_handler = ErrorHandler()
    computation_history = ComputationHistory()
    data_exporter = DataExporter()

    controller = MainController(
        auth_service, expression_evaluator, graph_plotter, symbolic_computer,
        profile_manager, data_access_object, error_handler, computation_history, data_exporter
    )

    app = TkinterGUI(controller)
    app.mainloop()
