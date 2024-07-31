class ComputationHistory:
    def __init__(self):
        self.history = []

    def add_entry(self, entry: dict):
        self.history.append(entry)

    def get_history(self) -> list:
        return self.history
