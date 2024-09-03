from Interfaces.error_handler import IErrorHandler

class ErrorHandler(IErrorHandler):
    def handleError(self, error: Exception) -> str:
        return str(error)

    def logError(self, error: Exception):
        print(f"Error: {error}")

    def validateInput(self, input: str) -> bool:
        return True
