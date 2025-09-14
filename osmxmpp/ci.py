import socket

from typing import List, Callable

from .validation import XmppValidation
from .permission import XmppPermission

from osmxml import *

import logging


logger = logging.getLogger(__name__)


class XmppClientInterface:
    """
    Xmpp client interface implementation.
    Used by Features or Extensions to interact with the XMPP client.
    """

    def __init__(self, client, obj, permissions: List[XmppPermission] | XmppPermission.ALL):
        """
        Initializes the Xmpp client interface.

        Args:
            client (XmppClient): The XMPP client.
            permissions (List[XmppPermission] | XmppPermission.ALL): The permissions to grant.
        """

        self.__client = client
        self.variables = XmppVariableInterface(self)
        
        if permissions == XmppPermission.ALL:
            permissions = [XmppPermission.ALL]

        self.__permissions = permissions

        self.object = obj
    
    def __handle_permission(self, permission:XmppPermission):
        if self.has_permission(permission):
            return
        
        raise Exception(f"No {permission} permission")
    
    # Exposed functions
    def has_permission(self, *permissions) -> bool:
        """
        Checks if the client interface has the given permission.

        Args:
            permissions (XmppPermission): The permissions to check.

        Returns:
            bool: True if the client interface has the permission, False otherwise.
        """
        if XmppPermission.ALL in self.__permissions:
            return True
        
        for permission in permissions:
            if permission in self.__permissions:
                return True

        return False

    def send_xml(self, xml:XmlElement):
        """
        Sends an XML element to the XMPP client.
        Requires the SEND_XML permission.

        Args:
            xml (XmlElement): The XML element to send.

        Returns:
            XmlElement: The XML element sent.
        """
        self.__handle_permission(XmppPermission.SEND_XML)
        return self.__client._send_xml(xml)
    
    def recv_xml(self) -> XmlElement:
        """
        Receives an XML element from the XMPP client.
        Requires the RECV_XML permission.

        Returns:
            XmlElement: The XML element received.
        """
        self.__handle_permission(XmppPermission.RECV_XML)
        return self.__client._recv_xml()
    
    def get_jid(self, with_resouce:bool = True) -> str:
        """
        Gets the JID of the XMPP client.
        Requires the GET_JID permission.

        Args:
            with_resouce (bool): Whether to include the resource in the JID. (Default: True)

        Returns:
            str: The JID of the XMPP client.
        """
        self.__handle_permission(XmppPermission.GET_JID)

        if with_resouce:
            return self.__client.jid
        else:
            return self.__client.jid.split("/")[0]

    def get_resource(self) -> str:
        """
        Gets the resource of the XMPP client.
        Requires the GET_RESOURCE or GET_JID permissions.

        Returns:
            str: The resource of the XMPP client.
        """
        self.__handle_permission(XmppPermission.GET_RESOURCE, XmppPermission.GET_JID)
        return self.__client.resource

    def set_jid(self, jid:str):
        """
        Sets the JID of the XMPP client.
        Requires the SET_JID permission.

        Args:
            jid (str): The new JID of the XMPP client.
        """

        XmppValidation.validate_jid(jid)

        self.__handle_permission(XmppPermission.SET_JID)
        self.__client.jid = jid
        return

    def set_resource(self, resource:str):
        """
        Sets the resource of the XMPP client.
        Requires the SET_RESOURCE permission.

        Args:
            resource (str): The new resource of the XMPP client.
        """

        XmppValidation.validate_resource(resource)

        self.__handle_permission(XmppPermission.SET_RESOURCE)
        self.__client.resource = resource
        return

    def get_host(self) -> str:
        """
        Gets the host of the XMPP client.
        Requires the GET_HOST permission.

        Returns:
            str: The host of the XMPP client.
        """
        self.__handle_permission(XmppPermission.GET_HOST)
        return self.__client.host

    def get_port(self) -> int:
        """
        Gets the port of the XMPP client.
        Requires the GET_PORT permission.

        Returns:
            int: The port of the XMPP client.
        """
        self.__handle_permission(XmppPermission.GET_PORT)
        return self.__client.port
    
    def change_socket(self, socket):
        """
        Changes the socket of the XMPP client.
        Requires the CHANGE_SOCKET permission.

        Args:
            socket (socket): The new socket of the XMPP client.
        """
        self.__handle_permission(XmppPermission.CHANGE_SOCKET)
        self.__client.socket = socket
        return
    
    def get_socket(self) -> socket:
        """
        Gets the socket of the XMPP client.
        Requires the GET_SOCKET permission.

        Returns:
            socket: The socket of the XMPP client.
        """
        self.__handle_permission(XmppPermission.GET_SOCKET)
        return self.__client.socket
    
    def open_stream(self):
        """
        Opens the XMPP stream.
        Requires the OPEN_STREAM permission.
        """
        self.__handle_permission(XmppPermission.OPEN_STREAM)
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
        self.__handle_permission(XmppPermission.LISTEN_ON_CONNECT)
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
        self.__handle_permission(XmppPermission.LISTEN_ON_DISCONNECT)
        return self.__client.on_disconnect(handler)
    
    def on_ready(self, handler:Callable) -> Callable:
        """
        Registers a handler for the ready event.
        The handler will be called when the client is ready to send and receive XMPP stanzas.

        Args:
            handler (Callable): The handler to register.

        Returns:
            Callable: The handler (not changed).
        """
        self.__handle_permission(XmppPermission.LISTEN_ON_READY)
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
        self.__handle_permission(XmppPermission.LISTEN_ON_MESSAGE)
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
        self.__handle_permission(XmppPermission.LISTEN_ON_PRESENCE)
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
        self.__handle_permission(XmppPermission.LISTEN_ON_IQ)
        return self.__client.on_iq(handler)
    
    def hook_on_message(self, hook:Callable) -> Callable:
        """
        Registers a hook for the message event.
        The hook will be called when the client receives a message stanza.

        Args:
            hook (Callable): The hook to register.

        Returns:
            Callable: The hook (not changed).
        """
        self.__handle_permission(XmppPermission.HOOK_ON_MESSAGE)
        return self.__client.hook_on_message(hook)
    
    def hook_on_presence(self, hook:Callable) -> Callable:
        """
        Registers a hook for the presence event.
        The hook will be called when the client receives a presence stanza.

        Args:
            hook (Callable): The hook to register.

        Returns:
            Callable: The hook (not changed).
        """
        self.__handle_permission(XmppPermission.HOOK_ON_PRESENCE)
        return self.__client.hook_on_presence(hook)
    
    def hook_on_iq(self, hook:Callable) -> Callable:
        """
        Registers a hook for the iq event.
        The hook will be called when the client receives an iq stanza.

        Args:
            hook (Callable): The hook to register.

        Returns:
            Callable: The hook (not changed).
        """
        self.__handle_permission(XmppPermission.HOOK_ON_IQ)
        return self.__client.hook_on_iq(hook)
    
    def hook_send_message(self, hook:Callable) -> Callable:
        """
        Registers a hook for the send message event.
        The hook will be called when the client sends a message.
        
        Args:
            hook (Callable): The hook to register.
        
        Returns:
            Callable: The hook (not changed).
        """
        self.__handle_permission(XmppPermission.HOOK_SEND_MESSAGE)
        return self.__client.hook_send_message(hook)
    
    def disconnect(self):
        """
        Disconnects from the XMPP server.
        Requires the DISCONNECT permission.
        """
        self.__handle_permission(XmppPermission.DISCONNECT)
        return self.__client.disconnect()
    

    def __repr__(self):
        return f"<XmppClientInterface of '{repr(self.__client)}'>"

class XmppVariableInterface:
    """
    Xmpp variable interface implementation.
    Used by Features or Extensions to expose variables
    """

    def __init__(self, ci):
        """
        Initializes the XMPP variable interface.

        Args:
            client (XmppClient): The XMPP client.
        """

        super().__setattr__("ci", ci)
        super().__setattr__("variables", {})
    
    def function(self, function:Callable):
        """
        Registers a function to the variable.

        Args:
            function (Callable): The function to register.
        
        Returns:
            Callable: The function (not changed).
        """

        logging.debug(f"Registering function '{function.__name__}' for ''{super().__getattribute__("ci").object.ID}''...")

        super().__getattribute__("variables")[function.__name__] = function
        return function
    
    def __getattr__(self, name):
        if name in super().__getattribute__("variables"):
            return super().__getattribute__("variables")[name]
        else:
            raise AttributeError(f"No variable named '{name}'")
    
    def __setattr__(self, name, value):
        super().__getattribute__("variables")[name] = value
