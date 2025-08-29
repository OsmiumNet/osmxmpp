from abc import ABC, abstractmethod

class XMPPFeature(ABC):
    """
    Features are used to implement specific XMPP stream features.

    Attributes:
        id (str): The ID of the feature implementation.
        tag (str): The tag of the feature. This is used to identify the feature in the XML stream.
        receive_new_features (bool): If client should receive new features after processing the current one.
    """

    id = None
    tag = None

    receive_new_features = None
    
    @abstractmethod
    def connect_ci(self, ci) -> None:
        """
        Connects the feature to the client interface.

        Args:
            ci (XMPPCI): The client interface.
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