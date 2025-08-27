from osmxml import *
import socket, ssl

from .feature import XMPPFeature

from typing import Callable, List

class XMPPClient:
    def __init__(self, server:str, port:int=5222):
        self.server = server
        self.port = port

        self.connected = False

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


    def _start_xmpp_stream(self):
        stream_start = XMLElement(
            "stream:stream", 
            attributes = [
                XMLAttribute("xmlns", "jabber:client"), 
                XMLAttribute("xmlns:stream", "http://etherx.jabber.org/streams"), 
                XMLAttribute("version", "1.0"), 
                XMLAttribute("to", host)
            ],
            is_closed=False
        )

        self.socket.sendall(stream_start.to_string().encode("utf-8"))

        data = self.socket.recv(4096)
        return XMLParser.parse_elements(data.decode("utf-8"))[0]
    
    def _close_xmpp_stream(self):
        self.socket.sendall(b"</stream:stream>")
    
    def _receive_stream_features(self):
        data = self.socket.recv(4096)
        return XMLParser.parse_elements(data.decode("utf-8"))[0]
    

    def connect(self, features:List[XMPPFeature]=None) -> None:
        if features is None:
            features = []
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            self.socket.connect((host, port))

            self.connected = True
            for handler in self.handlers["connected"]:
                handler()
            
            self._start_xmp_stream()

            features_xml = self._receive_stream_features()
            while True:
                new_features_xml = None
                for i, children in enumerate(features_xml.children):
                    for feature in features:
                        new_features_xml = feature.handle_client(children)
                        if new_features_xml:
                           break 
                    
                    if new_features_xml:
                        break
                
                if not new_features_xml:
                    break
                features_xml = new_features_xml