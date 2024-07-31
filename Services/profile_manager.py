from Interfaces.profile_manager import IProfileManager

class ProfileManager(IProfileManager):
    def __init__(self, db):
        self.db = db

    def createProfile(self, userData: dict) -> any:
        # Implement profile creation logic
        pass

    def updateProfile(self, userId: int, newData: dict) -> any:
        # Implement profile update logic
        pass

    def getProfile(self, userId: int) -> any:
        # Implement get profile logic
        pass
