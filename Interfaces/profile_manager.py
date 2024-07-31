from abc import ABC, abstractmethod

class IProfileManager(ABC):
    @abstractmethod
    def createProfile(self, userData: dict) -> any: pass

    @abstractmethod
    def updateProfile(self, userId: int, newData: dict) -> any: pass

    @abstractmethod
    def getProfile(self, userId: int) -> any: pass
