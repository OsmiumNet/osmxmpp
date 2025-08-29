from osmxml import *
import socket

from .permission import XMPPPermission

from typing import List

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
    
    def disconnect(self):
        """
        Disconnects from the XMPP server.
        Requires the DISCONNECT permission.
        """
        self.__handle_permission(XMPPPermission.DISCONNECT)
        return self.__client.disconnect()
    

    def __repr__(self):
        return f"<XMPPClientInterface of '{repr(self.__client)}'>"