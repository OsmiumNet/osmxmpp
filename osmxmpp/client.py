from osmxml import *
import socket, ssl

from .feature import XMPPFeature
from .permission import XMPPPermission

from typing import Callable, List


class XMPPCI:
    def __init__(self, client, permissions:List[XMPPPermission]=None):
        self.__client = client
        self.__permissions = permissions
    
    def __handle_permission(self, permission:XMPPPermission):
        if self.has_permission(XMPPPermission.ALL):
            return

        if self.has_permission(permission):
            return
        
        raise Exception(f"No {permission} permission")
    
    # Exposed functions
    def has_permission(self, permission:XMPPPermission) -> bool:
        return permission in self.__permissions

    def send_xml(self, xml:XMLElement):
        self.__handle_permission(XMPPPermission.SEND_XML)
        self.__client.socket.sendall(xml.to_string().encode("utf-8"))
    
    def recv_xml(self) -> XMLElement:
        self.__handle_permission(XMPPPermission.RECV_XML)
        data = self.__client.socket.recv(4096)
        return XMLParser.parse_elements(data.decode("utf-8"))[0]
    
    def get_jid(self) -> str:
        self.__handle_permission(XMPPPermission.GET_JID)
        return self.__client.jid

    def get_resource(self) -> str:
        self.__handle_permission(XMPPPermission.GET_RESOURCE)
        return self.__client.resource

    def set_jid(self, jid:str):
        self.__handle_permission(XMPPPermission.SET_JID)
        self.__client.jid = jid
        return

    def set_resource(self, resource:str):
        self.__handle_permission(XMPPPermission.SET_RESOURCE)
        self.__client.resource = resource
        return

    def get_host(self) -> str:
        self.__handle_permission(XMPPPermission.GET_HOST)
        return self.__client.host

    def get_port(self) -> int:
        self.__handle_permission(XMPPPermission.GET_PORT)
        return self.__client.port

    def open_stream(self):
        self.__handle_permission(XMPPPermission.OPEN_STREAM)
        self.__client._start_xmpp_stream()
    
    def close_stream(self):
        self.__handle_permission(XMPPPermission.CLOSE_STREAM)
        self.__client._close_xmpp_stream()
    
    def change_socket(self, socket):
        self.__handle_permission(XMPPPermission.CHANGE_SOCKET)
        self.__client.socket = socket
    
    def get_socket(self) -> socket:
        self.__handle_permission(XMPPPermission.GET_SOCKET)
        return self.__client.socket
        

    

class XMPPClient:
    def __init__(self, host:str, port:int=5222):
        self.host = host
        self.port = port

        self.__connected = False

        self.__handlers = {
            "connected": [],
            "disconnected": [],
            "ready": [],
            "message": [],
            "presence": [],
            "iq": [],
        }

        self.__features = {}

    @property
    def connected(self):
        return self.__connected
    

    def on_connect(self, handler:Callable) -> Callable:
        self.__handlers["connected"].append(handler)
        return handler
    
    def on_disconnect(self, handler:Callable) -> Callable:
        self.__handlers["disconnected"].append(handler)
        return handler
    
    def on_ready(self, handler:Callable) -> Callable:
        self.__handlers["ready"].append(handler)
        return handler

    def on_message(self, handler:Callable) -> Callable:
        self.__handlers["message"].append(handler)
        return handler
    
    def on_presence(self, handler:Callable) -> Callable:
        self.__handlers["presence"].append(handler)
        return handler
    
    def on_iq(self, handler:Callable) -> Callable:
        self.__handlers["iq"].append(handler)
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
                for handler in self.__handlers["disconnected"]:
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
                    for handler in self.__handlers["message"]:
                        handler(element)

                elif element.name == "presence":
                    for handler in self.__handlers["presence"]:
                        handler(element)
                
                elif element.name == "iq":
                    for handler in self.__handlers["iq"]:
                        handler(element)

    def connect_feature(self, feature:XMPPFeature, permissions:List[XMPPPermission]=None) -> None:
        if permissions is None:
            permissions = []
        
        feature.connect_ci(XMPPCI(self, permissions))
        self.__features[feature.id] = feature


    def connect(self) -> None:        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            self.socket.connect((self.host, self.port))

            self.__connected = True
            for handler in self.__handlers["connected"]:
                handler()
            
            self._start_xmpp_stream()

            features_xml = self._receive_stream_features()
            while True:
                processed_feature = None
                for feature in self.__features.values():
                    feature_xml = features_xml.get_child_by_name(feature.tag)
                    if feature_xml:
                        feature.process(feature_xml)
                        processed_feature = feature
                        break
                
                if not processed_feature.receive_new_features:
                    break

                features_xml = self._receive_stream_features()
            
            self._send_presence()

            for handler in self.__handlers["ready"]:
                handler()

            self._listen()