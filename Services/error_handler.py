from Interfaces.error_handler import IErrorHandler

class ErrorHandler(IErrorHandler):
    def handleError(self, error: Exception) -> str:
        # Implement error handling logic
        return str(error)

    def logError(self, error: Exception):
        # Implement error logging logic
        print(f"Error: {error}")

    def validateInput(self, input: str) -> bool:
        # Implement input validation logic
        return True
