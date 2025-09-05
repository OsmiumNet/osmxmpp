from abc import ABC, abstractmethod

class XMPPExtension(ABC):
    """
    Extensions are used to implement specific XMPP extensions & etc.
    They have more wider usecase than features.

    Attributes:
        ID (str): The ID of the extension implementation.
    """

    ID = None
    
    @abstractmethod
    def connect_ci(self, ci) -> None:
        """
        Connects the extension to the client interface.

        Args:
            ci (XMPPClientInterface): The client interface.
        """
        ...
    
    @abstractmethod
    def process(self, element) -> None:
        """
        Processes the extension.

        Args:
            element (XMLElement): The XML element to process.
        """
        ...