from .client import XMPPClient

class XMPPFeature:
    def __init__(self):
        pass

    def handle_client(self, client:XMPPClient, feature:XMLElement) -> XMLElement:
        pass