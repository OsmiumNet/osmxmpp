from enum import Enum, auto

class XMPPPermission(Enum):
    """
    Permissions are used to control what actions Feature or Extension can perform.
    """

    ALL = auto()

    SEND_XML = auto()
    RECV_XML = auto()

    GET_JID = auto()
    GET_RESOURCE = auto()
    SET_JID = auto()
    SET_RESOURCE = auto()

    GET_HOST = auto()
    GET_PORT = auto()

    GET_SOCKET = auto()
    CHANGE_SOCKET = auto()

    OPEN_STREAM = auto()
    CLOSE_STREAM = auto()

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"<XMPPPermission.{self.name}>"