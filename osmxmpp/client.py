from osmxml import *
import socket, ssl

from .feature import XMPPFeature

from typing import Callable, List

class XMPPClient:
    def __init__(self, host:str, port:int=5222):
        self.host = host
        self.port = port

        self.connected = False

        self.handlers = {
            "connected": [],
            "disconnected": [],
            "ready": [],
            "message": [],
            "presence": [],
            "iq": [],
        }


    def on_connect(self, handler:Callable) -> Callable:
        self.handlers["connected"].append(handler)
        return handler
    
    def on_disconnect(self, handler:Callable) -> Callable:
        self.handlers["disconnected"].append(handler)
        return handler
    
    def on_ready(self, handler:Callable) -> Callable:
        self.handlers["ready"].append(handler)
        return handler

    def on_message(self, handler:Callable) -> Callable:
        self.handlers["message"].append(handler)
        return handler
    
    def on_presence(self, handler:Callable) -> Callable:
        self.handlers["presence"].append(handler)
        return handler
    
    def on_iq(self, handler:Callable) -> Callable:
        self.handlers["iq"].append(handler)
        return handler

    def _start_xmpp_stream(self):
        stream_start = XMLElement(
            "stream:stream", 
            attributes = [
                XMLAttribute("xmlns", "jabber:client"), 
                XMLAttribute("xmlns:stream", "http://etherx.jabber.org/streams"), 
                XMLAttribute("version", "1.0"), 
                XMLAttribute("to", self.host)
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
    
    def _send_presence(self):
        presence = XMLElement(
            "presence",
        )

        self.socket.sendall(presence.to_string().encode("utf-8"))
    

    def _listen(self):
        buffer = ""

        while True:
            data = self.socket.recv(4096)
            if not data:
                for handler in self.handlers["disconnected"]:
                    handler()
                break

            buffer += data.decode("utf-8")

            try:
                elements = XMLParser.parse_elements(buffer)
                buffer = ""
            except Exception:
                # Incomplete stanza
                continue

            for element in elements:
                if element.name == "message":
                    for handler in self.handlers["message"]:
                        handler(element)

                elif element.name == "presence":
                    for handler in self.handlers["presence"]:
                        handler(element)
                
                elif element.name == "iq":
                    for handler in self.handlers["iq"]:
                        handler(element)


    def connect(self, features:List[XMPPFeature]=None) -> None:
        if features is None:
            features = []
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            self.socket.connect((self.host, self.port))

            self.connected = True
            for handler in self.handlers["connected"]:
                handler()
            
            self._start_xmpp_stream()

            features_xml = self._receive_stream_features()
            while True:
                new_features_xml = None
                for i, children in enumerate(features_xml.children):
                    for feature in features:
                        new_features_xml = feature.handle_client(self, children)
                        if new_features_xml:
                           break 
                    
                    if new_features_xml:
                        break
                
                if not new_features_xml:
                    break
                features_xml = new_features_xml
            
            self._send_presence()

            for handler in self.handlers["ready"]:
                handler()

            self._listen()