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
from Services.error_handler import ErrorHandler
from Services.computation_history import ComputationHistory
from Gui.userview import TkinterGUI
from DbSetup.dao import SQLiteDataAccessObject
import tkinter as tk
import unittest
if __name__ == "__main__":
    # Run the application
    db_path = 'my_project_database.db'
    dao = SQLiteDataAccessObject(db_name=db_path)

    auth_service = AuthenticationService(db_path)
    symbolic_computer = SymbolicComputer()
    profile_manager = ProfileManager(db=dao)
    error_handler = ErrorHandler()

    app = TkinterGUI(
        auth_service=auth_service,
        symbolic_computer=symbolic_computer,
        profile_manager=profile_manager,
        error_handler=error_handler,
        db_path=db_path,
        dao=dao
    )

    app.mainloop()
    
    dao.close()

    # Automatically run tests after closing the application
   # unittest.TextTestRunner().run(unittest.defaultTestLoader.discover('tests'))
