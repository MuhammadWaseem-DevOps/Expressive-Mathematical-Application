from Interfaces.profile_manager import IProfileManager
import datetime
import sqlite3

class ProfileManager(IProfileManager):
    def __init__(self, db):
        self.db = db

    def createProfile(self, userData: dict) -> int:
        """Create a new profile in the database."""
        profile_data = {
            'user_id': userData['user_id'],
            'full_name': userData.get('full_name', ''),
            'preferences': '{}',  # Default preferences as an empty JSON object
            'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return self.db.insert('PROFILE', profile_data)

    def updateProfile(self, userId: int, newData: dict) -> bool:
        """Update an existing profile in the USER table."""
        if 'profile_picture' in newData and newData['profile_picture'] is not None:
            newData['profile_picture'] = sqlite3.Binary(newData['profile_picture'])
        # Remove the following line if you do not need the last_updated column
        # newData['last_updated'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return self.db.update('USER', userId, newData)

    def getProfile(self, userId: int) -> dict:
        """Retrieve a user's profile from the database."""
        user_data = self.db.select('USER', f'user_id = {userId}')
        if user_data:
            user = user_data[0]
            return {
                'user_id': user[0],
                'username': user[1],
                'email': user[3],
                'first_name': user[4],
                'last_name': user[5],
                'profile_picture': user[6],
                'created_at': user[7],
                'last_login': user[8]
            }
        return None

    def delete_account(self, userId: int) -> bool:
        """Delete the user's account from the database."""
        return self.db.delete('USER', userId)
