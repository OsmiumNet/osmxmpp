from osmxml import *
import socket, ssl

from .permission import XMPPPermission
from .message import XMPPMessage
from .feature import XMPPFeature
from .ci import XMPPCI

from typing import Callable, List, Tuple

class XMPPClient:
    """
    XMPP client implementation.
    """

    def __init__(self, host:str, port:int=5222):
        """
        Initializes the XMPP client.

        Args:
            host (str): The host of the XMPP server.
            port (int): The port of the XMPP server.
        """
        self.host = host
        self.port = port

        self.__connected = False

        self.__hooks = {
            "message": [],
            "presence": [],
            "iq": [],
        }

        self.__handlers = {
            "connected": [],
            "disconnected": [],
            "ready": [],
            "message": [],
            "presence": [],
            "iq": [],
        }

        self.__features = {}
        self.__features_queue = []


    @property
    def connected(self):
        return self.__connected
    

    def _trigger_handlers(self, event:str, *args, **kwargs):
        for handler in self.__handlers[event]:
            handler(*args, **kwargs)
    
    def _trigger_hooks(self, event:str, value):
        for hook in self.__hooks[event]:
            value = hook(value)
            if not value:
                return None
        return value


    def on_connect(self, handler:Callable) -> Callable:
        """
        Registers a handler for the connected event.
        The handler will be called when the client is connected to the XMPP server, but not ready yet.

        Args:
            handler (Callable): The handler to register.

        Returns:
            Callable: The handler (not changed).
        """
        self.__handlers["connected"].append(handler)
        return handler
    
    def on_disconnect(self, handler:Callable) -> Callable:
        """
        Registers a handler for the disconnected event.
        The handler will be called when the client is disconnected from the XMPP server.

        Args:
            handler (Callable): The handler to register.

        Returns:
            Callable: The handler (not changed).
        """
        self.__handlers["disconnected"].append(handler)
        return handler
    
    def on_ready(self, handler:Callable) -> Callable:
        """
        Registers a handler for the ready event.
        The handler will be called when the client is ready to send and receive XMPP stanzas.

        Args:
            handler (Callable): The handler to register.

        Returns:
            Callable: The handler (not changed).
        
        Example:
            >>> @client.on_ready
            ... def on_ready():
            ...     print(f"Loggened in as {client.jid}")
        """
        self.__handlers["ready"].append(handler)
        return handler

    def on_message(self, handler:Callable) -> Callable:
        """
        Registers a handler for the message event.
        The handler will be called when the client receives a message stanza.

        Args:
            handler (Callable): The handler to register.

        Returns:
            Callable: The handler (not changed).
        """
        self.__handlers["message"].append(handler)
        return handler
    
    def on_presence(self, handler:Callable) -> Callable:
        """
        Registers a handler for the presence event.
        The handler will be called when the client receives a presence stanza.

        Args:
            handler (Callable): The handler to register.

        Returns:
            Callable: The handler (not changed).
        """
        self.__handlers["presence"].append(handler)
        return handler
    
    def on_iq(self, handler:Callable) -> Callable:
        """
        Registers a handler for the iq event.
        The handler will be called when the client receives an iq stanza.

        Args:
            handler (Callable): The handler to register.

        Returns:
            Callable: The handler (not changed).
        """
        self.__handlers["iq"].append(handler)
        return handler


    def hook_message(self, hook:Callable) -> Callable:
        """
        Registers a hook for the message event.
        The hook will be called when the client receives a message stanza.

        Args:
            hook (Callable): The hook to register.

        Returns:
            Callable: The hook (not changed).
        """
        self.__hooks["message"].append(hook)
        return hook
    
    def hook_presence(self, hook:Callable) -> Callable:
        """
        Registers a hook for the presence event.
        The hook will be called when the client receives a presence stanza.

        Args:
            hook (Callable): The hook to register.

        Returns:
            Callable: The hook (not changed).
        """
        self.__hooks["presence"].append(hook)
        return hook
    
    def hook_iq(self, hook:Callable) -> Callable:
        """
        Registers a hook for the iq event.
        The hook will be called when the client receives an iq stanza.

        Args:
            hook (Callable): The hook to register.

        Returns:
            Callable: The hook (not changed).
        """
        self.__hooks["iq"].append(hook)
        return hook


    def _recv_xml(self) -> XMLElement:
        data = self.socket.recv(4096)
        return XMLParser.parse_elements(data.decode("utf-8"))[0]
    
    def _send_xml(self, xml:XMLElement):
        self.socket.sendall(xml.to_string().encode("utf-8"))


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

        self._send_xml(stream_start)
        return self._recv_xml()
    
    def _close_xmpp_stream(self):
        self.socket.sendall(b"</stream:stream>")
    
    def _send_presence(self):
        presence = XMLElement("presence")
        self._send_xml(presence)
    

    def _listen(self):
        buffer = ""

        while True:
            data = self.socket.recv(4096)
            if not data:
                self.disconnect()
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
                    message = XMPPMessage(element)
                    hooks_result = self._trigger_hooks("message", message)
                    if hooks_result is None:
                        continue
                    self._trigger_handlers("message", hooks_result)

                elif element.name == "presence":
                    hooks_result = self._trigger_hooks("presence", element)
                    if hooks_result is None:
                        continue
                    self._trigger_handlers("presence", hooks_result)
                
                elif element.name == "iq":
                    hooks_result = self._trigger_hooks("iq", element)
                    if hooks_result is None:
                        continue
                    self._trigger_handlers("iq", hooks_result)

    def connect_feature(self, feature:XMPPFeature, permissions: List[XMPPPermission] | XMPPPermission.ALL) -> None:
        """
        Connects the given feature to the XMPP client.

        Args:
            feature (XMPPFeature): The feature to connect.
            permissions (List[XMPPPermission] | XMPPPermission.ALL): The permissions to grant.
        
        Example:
            >>> client.connect_feature(BindFeature("osmxmpp"), XMPPPermission.ALL)
        """
        
        feature.connect_ci(XMPPCI(self, permissions))
        self.__features[feature.id] = feature
        self.__features_queue.append(feature.id)

    def connect_features(self, features_with_permissions: List[Tuple[XMPPFeature, List[XMPPPermission] | XMPPPermission.ALL]] ) -> None:
        """
        Connects the given features to the XMPP client.

        Args:
            features_with_permissions (List[Tuple[XMPPFeature, List[XMPPPermission] | XMPPPermission.ALL]]): The features with permissions to connect
        
        Example:
            >>> client.connect_features([
            ...     (TLSFeature(), [XMPPPersmision.SEND_XML, XMPPPersmision.RECV_XML])
            ...     (BindFeature("osmxmpp"), XMPPPermission.ALL)
            ... ])
        """

        for feature_with_permissions in features_with_permissions:
            self.connect_feature(feature_with_permissions[0], feature_with_permissions[1]) 

    def connect(self) -> None:
        """
        Connects to the XMPP server.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            self.socket.connect((self.host, self.port))

            self.__connected = True
            self._trigger_handlers("connected")
            
            self._start_xmpp_stream()

            features_xml = self._recv_xml()
            while True:
                processed_feature = None
                for feature_id in self.__features_queue:
                    feature = self.__features[feature_id]

                    feature_xml = features_xml.get_child_by_name(feature.tag)
                    if feature_xml:
                        feature.process(feature_xml)
                        processed_feature = feature
                        break
                
                if not processed_feature.receive_new_features:
                    break

                features_xml = self._recv_xml()
            
            self._send_presence()

            self._trigger_handlers("ready")

            self._listen()
            self.socket.close()
    
    def disconnect(self):
        """
        Disconnects from the XMPP server.
        """

        if not self.__connected:
            raise Exception("XMPPClient is not connected")

        self._close_xmpp_stream()
        self.socket.close()
        self.__connected = False

        self._trigger_handlers("disconnected")
    

    def __repr__(self):
        return f"<XMPPClient {self.host}:{self.port}>"
