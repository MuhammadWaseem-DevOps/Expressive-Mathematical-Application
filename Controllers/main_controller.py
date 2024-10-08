from Interfaces.controller import IController
from Services.authentication import AuthenticationService
from Services.expression_evaluator import ExpressionEvaluator
from Services.graph_plotter import GraphPlotter
from Services.symbolic_computer import SymbolicComputer
from Services.profile_manager import ProfileManager
from DbSetup.dao import IDataAccessObject
from Services.error_handler import IErrorHandler
from Services.computation_history import ComputationHistory


class MainController(IController):
    def __init__(self, authService: AuthenticationService, expressionEvaluator: ExpressionEvaluator,
                 graphPlotter: GraphPlotter, symbolicComputer: SymbolicComputer,
                 profileManager: ProfileManager, dataAccessObject: IDataAccessObject,
                 errorHandler: IErrorHandler, computationHistory: ComputationHistory):
        self.authService = authService
        self.expressionEvaluator = expressionEvaluator
        self.graphPlotter = graphPlotter
        self.symbolicComputer = symbolicComputer
        self.profileManager = profileManager
        self.dataAccessObject = dataAccessObject
        self.errorHandler = errorHandler
        self.computationHistory = computationHistory

    def authenticateUser(self, username: str, password: str) -> bool:
        return self.authService.authenticateUser(username, password)

    def evaluateExpression(self, expression: str) -> float:
        return self.expressionEvaluator.evaluate(expression)

    def plotGraph(self, function: str) -> any:
        return self.graphPlotter.plotFunction(function)

    def performSymbolicComputation(self, expression: str) -> str:
        return self.symbolicComputer.simplify(expression)

    def manageProfile(self, userId: int) -> any:
        return self.profileManager.getProfile(userId)

    def getComputationHistory(self) -> list:
        return self.computationHistory.get_history()
