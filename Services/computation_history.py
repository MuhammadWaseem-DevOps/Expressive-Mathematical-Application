class ComputationHistory:
    def __init__(self, dao, user_id):
        self.dao = dao
        self.user_id = user_id

    def add_entry(self, entry: dict):
        self.dao.insert('COMPUTATION_HISTORY', entry)

    def add_graph_entry(self, entry: dict):
        history_id = self.dao.insert('COMPUTATION_HISTORY', entry)
        graph_entry = {
            'history_id': history_id,
            'function': entry['expression'],
            'plot_settings': json.dumps({'x_min': entry['x_min'], 'x_max': entry['x_max']})
        }
        self.dao.insert('GRAPHICAL_FUNCTION', graph_entry)

    def get_history(self) -> list:
        return self.dao.get_computation_history(self.user_id)
