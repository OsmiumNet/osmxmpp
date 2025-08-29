from osmxml import *
import socket

from .permission import XMPPPermission

from typing import List, Callable

class XMPPClientInterface:
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
    
    def open_stream(self):
        """
        Opens the XMPP stream.
        Requires the OPEN_STREAM permission.
        """
        self.__handle_permission(XMPPPermission.OPEN_STREAM)
        return self.__client._start_xmpp_stream()
    
    def on_connect(self, handler:Callable) -> Callable:
        """
        Registers a handler for the connected event.
        The handler will be called when the client is connected to the XMPP server, but not ready yet.

        Args:
            handler (Callable): The handler to register.

        Returns:
            Callable: The handler (not changed).
        """
        self.__handle_permission(XMPPPermission.LISTEN_ON_CONNECT)
        return self.__client.on_connect(handler)
    
    def on_disconnect(self, handler:Callable) -> Callable:
        """
        Registers a handler for the disconnected event.
        The handler will be called when the client is disconnected from the XMPP server.

        Args:
            handler (Callable): The handler to register.

        Returns:
            Callable: The handler (not changed).
        """
        self.__handle_permission(XMPPPermission.LISTEN_ON_DISCONNECT)
        return self.__client.on_disconnect(handler)
    
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
        self.__handle_permission(XMPPPermission.LISTEN_ON_READY)
        return self.__client.on_ready(handler)

    def on_message(self, handler:Callable) -> Callable:
        """
        Registers a handler for the message event.
        The handler will be called when the client receives a message stanza.

        Args:
            handler (Callable): The handler to register.

        Returns:
            Callable: The handler (not changed).
        """
        self.__handle_permission(XMPPPermission.LISTEN_ON_MESSAGE)
        return self.__client.on_message(handler)
    
    def on_presence(self, handler:Callable) -> Callable:
        """
        Registers a handler for the presence event.
        The handler will be called when the client receives a presence stanza.

        Args:
            handler (Callable): The handler to register.

        Returns:
            Callable: The handler (not changed).
        """
        self.__handle_permission(XMPPPermission.LISTEN_ON_PRESENCE)
        return self.__client.on_presence(handler)
    
    def on_iq(self, handler:Callable) -> Callable:
        """
        Registers a handler for the iq event.
        The handler will be called when the client receives an iq stanza.

        Args:
            handler (Callable): The handler to register.

        Returns:
            Callable: The handler (not changed).
        """
        self.__handle_permission(XMPPPermission.LISTEN_ON_IQ)
        return self.__client.on_iq(handler)
    
    def hook_message(self, hook:Callable) -> Callable:
        """
        Registers a hook for the message event.
        The hook will be called when the client receives a message stanza.

        Args:
            hook (Callable): The hook to register.

        Returns:
            Callable: The hook (not changed).
        """
        self.__handle_permission(XMPPPermission.HOOK_MESSAGE)
        return self.__client.hook_message(hook)
    
    def hook_presence(self, hook:Callable) -> Callable:
        """
        Registers a hook for the presence event.
        The hook will be called when the client receives a presence stanza.

        Args:
            hook (Callable): The hook to register.

        Returns:
            Callable: The hook (not changed).
        """
        self.__handle_permission(XMPPPermission.HOOK_PRESENCE)
        return self.__client.hook_presence(hook)
    
    def hook_iq(self, hook:Callable) -> Callable:
        """
        Registers a hook for the iq event.
        The hook will be called when the client receives an iq stanza.

        Args:
            hook (Callable): The hook to register.

        Returns:
            Callable: The hook (not changed).
        """
        self.__handle_permission(XMPPPermission.HOOK_IQ)
        return self.__client.hook_iq(hook)
    
    def disconnect(self):
        """
        Disconnects from the XMPP server.
        Requires the DISCONNECT permission.
        """
        self.__handle_permission(XMPPPermission.DISCONNECT)
        return self.__client.disconnect()
    

    def __repr__(self):
        return f"<XMPPClientInterface of '{repr(self.__client)}'>"
