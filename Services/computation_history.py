class ComputationHistory:
    def __init__(self, dao, user_id):
        self.dao = dao
        self.user_id = user_id

    def add_entry(self, entry: dict):
        self.dao.insert('COMPUTATION_HISTORY', entry)

    def get_history(self) -> list:
        return self.dao.get_computation_history(self.user_id)
