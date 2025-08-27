from osmxml import *
import socket, ssl

from .feature import XMPPFeature

from typing import Callable, List

class XMPPClient:
    def __init__(self, server:str, port:int=5222):
        self.server = server
        self.port = port

        self.handlers = {
            "connected": [],
            "ready": [],
        }

    def connected(self, handler:Callable) -> Callable:
        self.handlers["connected"].append(handler)
        return handler
    
    def ready(self, handler:Callable) -> Callable:
        self.handlers["ready"].append(handler)
        return handler


    def connect(self, features:List[XMPPFeature]=None) -> None:
        if features is None:
            features = []
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            self.socket.connect((host, port))

            for handler in self.handlers["connected"]:
                handler()