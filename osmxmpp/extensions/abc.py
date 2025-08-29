from abc import ABC, abstractmethod

class XMPPExtension(ABC):
    """
    Extensions are used to implement specific XMPP extensions & etc.

    Attributes:
        id (str): The ID of the extension implementation.
    """

    id = None
    
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