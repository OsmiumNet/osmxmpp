from osmxml import *
import socket, ssl

from .feature import XMPPFeature
from .permission import XMPPPermission

from typing import Callable, List


class XMPPCI:
    """
    XMPP client interface implementation.
    Used by Features or Extensions to interact with the XMPP client.
    """

    def __init__(self, client, permissions: List[XMPPPermission] | XMPPPermission.ALL):
        """
        Initializes the XMPP client interface.

        Args:
            client (XMPPClient): The XMPP client.
            permissions (List[XMPPPermission] | XMPPPermission.ALL): The permissions to grant.
        """

        self.__client = client
        
        if permissions == XMPPPermission.ALL:
            permissions = [XMPPPermission.ALL]

        self.__permissions = permissions
    
    def __handle_permission(self, permission:XMPPPermission):
        if self.has_permission(XMPPPermission.ALL):
            return

        if self.has_permission(permission):
            return
        
        raise Exception(f"No {permission} permission")
    
    # Exposed functions
    def has_permission(self, permission:XMPPPermission) -> bool:
        """
        Checks if the client interface has the given permission.

        Args:
            permission (XMPPPermission): The permission to check.

        Returns:
            bool: True if the client interface has the permission, False otherwise.
        """
        return permission in self.__permissions

    def send_xml(self, xml:XMLElement):
        """
        Sends an XML element to the XMPP client.
        Requires the SEND_XML permission.

        Args:
            xml (XMLElement): The XML element to send.

        Returns:
            XMLElement: The XML element sent.
        """
        self.__handle_permission(XMPPPermission.SEND_XML)
        return self.__client._send_xml(xml)
    
    def recv_xml(self) -> XMLElement:
        """
        Receives an XML element from the XMPP client.
        Requires the RECV_XML permission.

        Returns:
            XMLElement: The XML element received.
        """
        self.__handle_permission(XMPPPermission.RECV_XML)
        return self.__client._recv_xml()
    
    def get_jid(self) -> str:
        """
        Gets the JID of the XMPP client.
        Requires the GET_JID permission.

        Returns:
            str: The JID of the XMPP client.
        """
        self.__handle_permission(XMPPPermission.GET_JID)
        return self.__client.jid

    def get_resource(self) -> str:
        """
        Gets the resource of the XMPP client.
        Requires the GET_RESOURCE permission.

        Returns:
            str: The resource of the XMPP client.
        """
        self.__handle_permission(XMPPPermission.GET_RESOURCE)
        return self.__client.resource

    def set_jid(self, jid:str):
        """
        Sets the JID of the XMPP client.
        Requires the SET_JID permission.

        Args:
            jid (str): The new JID of the XMPP client.
        """
        self.__handle_permission(XMPPPermission.SET_JID)
        self.__client.jid = jid
        return

    def set_resource(self, resource:str):
        """
        Sets the resource of the XMPP client.
        Requires the SET_RESOURCE permission.

        Args:
            resource (str): The new resource of the XMPP client.
        """
        self.__handle_permission(XMPPPermission.SET_RESOURCE)
        self.__client.resource = resource
        return

    def get_host(self) -> str:
        """
        Gets the host of the XMPP client.
        Requires the GET_HOST permission.

        Returns:
            str: The host of the XMPP client.
        """
        self.__handle_permission(XMPPPermission.GET_HOST)
        return self.__client.host

    def get_port(self) -> int:
        """
        Gets the port of the XMPP client.
        Requires the GET_PORT permission.

        Returns:
            int: The port of the XMPP client.
        """
        self.__handle_permission(XMPPPermission.GET_PORT)
        return self.__client.port

    def open_stream(self):
        """
        Opens the XMPP stream.
        Requires the OPEN_STREAM permission.
        """
        self.__handle_permission(XMPPPermission.OPEN_STREAM)
        return self.__client._start_xmpp_stream()
    
    def close_stream(self):
        """
        Closes the XMPP stream.
        Requires the CLOSE_STREAM permission.
        """
        self.__handle_permission(XMPPPermission.CLOSE_STREAM)
        return self.__client._close_xmpp_stream()
    
    def change_socket(self, socket):
        """
        Changes the socket of the XMPP client.
        Requires the CHANGE_SOCKET permission.

        Args:
            socket (socket): The new socket of the XMPP client.
        """
        self.__handle_permission(XMPPPermission.CHANGE_SOCKET)
        self.__client.socket = socket
        return
    
    def get_socket(self) -> socket:
        """
        Gets the socket of the XMPP client.
        Requires the GET_SOCKET permission.

        Returns:
            socket: The socket of the XMPP client.
        """
        self.__handle_permission(XMPPPermission.GET_SOCKET)
        return self.__client.socket
        

    

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

    def connect_feature(self, feature:XMPPFeature, permissions: List[XMPPPermission] | XMPPPermission.ALL = XMPPPermission.ALL) -> None:
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


    def connect(self) -> None:
        """
        Connects to the XMPP server.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            self.socket.connect((self.host, self.port))

            self.__connected = True
            for handler in self.__handlers["connected"]:
                handler()
            
            self._start_xmpp_stream()

            features_xml = self._recv_xml()
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

                features_xml = self._recv_xml()
            
            self._send_presence()

            for handler in self.__handlers["ready"]:
                handler()

            self._listen()