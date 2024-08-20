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

    def get_history(self, offset=0, limit=15) -> list:
        """Fetch computation history with pagination."""
        query = f"SELECT * FROM COMPUTATION_HISTORY WHERE user_id = {self.user_id} ORDER BY timestamp DESC LIMIT {limit} OFFSET {offset}"
        return self.dao.execute_query(query)

    def search_history(self, query_str) -> list:
        """Search computation history for a specific query."""
        query = f"SELECT * FROM COMPUTATION_HISTORY WHERE user_id = {self.user_id} AND expression LIKE '%{query_str}%' ORDER BY timestamp DESC"
        return self.dao.execute_query(query)

    def get_computation_details(self, computation_id) -> dict:
        """Get details of a specific computation."""
        query = f"SELECT * FROM COMPUTATION_HISTORY WHERE history_id = {computation_id}"
        computation = self.dao.execute_query(query)
        if computation:
            return computation[0]
        return None
