from Interfaces.profile_manager import IProfileManager
import datetime
import sqlite3
import json

class ProfileManager(IProfileManager):
    def __init__(self, db):
        self.db = db

    def createProfile(self, userData: dict) -> int:
        profile_data = {
            'user_id': userData['user_id'],
            'full_name': f"{userData.get('first_name', '')} {userData.get('last_name', '')}",
            'preferences': '{}',
            'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return self.db.insert('PROFILE', profile_data)

    def updateProfile(self, userId: int, newData: dict) -> bool:
        user_update_data = {
            'first_name': newData.get('first_name'),
            'last_name': newData.get('last_name'),
            'profile_picture': sqlite3.Binary(newData['profile_picture']) if 'profile_picture' in newData and newData['profile_picture'] else None
        }
        user_updated = self.db.update('USER', userId, user_update_data)
        
        profile_update_data = {
            'full_name': f"{newData.get('first_name', '')} {newData.get('last_name', '')}",
            'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        profile_updated = self.db.update('PROFILE', userId, profile_update_data)

        return user_updated and profile_updated

    def getProfile(self, userId: int) -> dict:
        user_data = self.db.select('USER', f'user_id = {userId}')
        profile_data = self.db.select('PROFILE', f'user_id = {userId}')
        
        if user_data and profile_data:
            user = user_data[0]
            profile = profile_data[0]
            return {
                'user_id': user[0],
                'username': user[1],
                'email': user[3],
                'first_name': user[4],
                'last_name': user[5],
                'profile_picture': user[6],
                'created_at': user[7],
                'last_login': user[8],
                'full_name': profile[2],
                'preferences': profile[3],
                'profile_last_updated': profile[4]
            }
        return None

    def get_computation_history(self, userId: int, offset: int = 0, limit: int = 15) -> list:
        query = f"""
        SELECT ch.history_id, p.full_name, ch.expression, ch.result, ch.timestamp
        FROM COMPUTATION_HISTORY ch
        JOIN PROFILE p ON ch.user_id = p.user_id
        WHERE ch.user_id = ?
        ORDER BY ch.timestamp DESC
        LIMIT ? OFFSET ?
        """
        return self.db.execute_query(query, (userId, limit, offset))

    def search_computation_history(self, userId: int, query_str: str) -> list:
        query = f"""
        SELECT ch.history_id, p.full_name, ch.expression, ch.result, ch.timestamp
        FROM COMPUTATION_HISTORY ch
        JOIN PROFILE p ON ch.user_id = p.user_id
        WHERE ch.user_id = ? AND ch.expression LIKE ?
        ORDER BY ch.timestamp DESC
        """
        return self.db.execute_query(query, (userId, f"%{query_str}%"))

    def get_computation_details(self, computation_id: int) -> dict:
        query = """
        SELECT ch.expression, ch.result, ch.symbolic_steps, p.full_name
        FROM COMPUTATION_HISTORY ch
        JOIN PROFILE p ON ch.user_id = p.user_id
        WHERE ch.history_id = ?
        """
        result = self.db.execute_query(query, (computation_id,))
        if result:
            computation = result[0]
            try:
                steps = json.loads(computation[2]) if computation[2] else []
            except json.JSONDecodeError:
                steps = []
            return {
                'expression': computation[0],
                'result': computation[1],
                'steps': steps,
                'full_name': computation[3]
            }
        return None

    def delete_account(self, userId: int) -> bool:
        profile_deleted = self.db.delete('PROFILE', userId)
        user_deleted = self.db.delete('USER', userId)
        return profile_deleted and user_deleted
