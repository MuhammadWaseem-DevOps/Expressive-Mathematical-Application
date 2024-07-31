from abc import ABC, abstractmethod

class IUserInterface(ABC):
    @abstractmethod
    def showLoginScreen(self):
        pass

    @abstractmethod
    def showMainDashboard(self):
        pass

    @abstractmethod
    def showExpressionInput(self):
        pass

    @abstractmethod
    def showGraphPlotter(self):
        pass

    @abstractmethod
    def showSymbolicComputation(self):
        pass

    @abstractmethod
    def showProfileManagement(self):
        pass

    @abstractmethod
    def displayResult(self, result):
        pass

    @abstractmethod
    def displayError(self, message):
        pass
