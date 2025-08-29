from abc import ABC, abstractmethod

class XMPPFeature(ABC):
    id = None
    tag = None

    receive_new_features = None
    
    @abstractmethod
    def connect_ci(self, ci) -> None:
        ...
    
    @abstractmethod
    def process(self, element) -> None:
        ...