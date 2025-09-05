from abc import ABC, abstractmethod

class XMPPFeature(ABC):
    """
    Features are used to implement specific XMPP stream features.

    Attributes:
        ID (str): The ID of the feature implementation.
        TAG (str): The tag of the feature. This is used to identify the feature in the XML stream.
        RECEIVE_NEW_FEATURES (bool): Whether the feature should receive new features.
    """

    ID = None
    TAG = None

    RECEIVE_NEW_FEATURES = None
    
    @abstractmethod
    def connect_ci(self, ci) -> None:
        """
        Connects the feature to the client interface.

        Args:
            ci (XMPPClientInterface): The client interface.
        """
        ...
    
    @abstractmethod
    def process(self, element) -> None:
        """
        Processes the feature.

        Args:
            element (XMLElement): The XML element to process.
        """
        ...
