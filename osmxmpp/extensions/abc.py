from abc import ABC, abstractmethod

class XmppExtension(ABC):
    """
    Extensions are used to implement specific XMPP extensions & etc.
    They have more wider usecase than features.

    Attributes:
        ID (str): The ID of the extension implementation.
    """

    ID = None
    
    @abstractmethod
    def _connect_ci(self, ci) -> None:
        """
        Connects the extension to the client interface.

        Args:
            ci (XmppClientInterface): The client interface.
        """
        ...
    
    @abstractmethod
    def process(self) -> None:
        """
        Processes the extension.
        """
        ...