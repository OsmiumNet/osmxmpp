from osmxml import *
import socket, ssl

import uuid

from .validation import XmppValidation
from .permission import XmppPermission
from .message import XmppMessage
from .features import XmppFeature
from .extensions import XmppExtension
from .ci import XmppClientInterface

from typing import Callable, List, Tuple

import logging

logger = logging.getLogger(__name__)

class XmppClient:
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
            "send_message": [],
            "on_message": [],
            "on_presence": [],
            "on_iq": [],
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

        self.__extensions = {}
        self.__extensions_queue = []


    @property    
    def extensions(self):
        extensions_functions = {}
        for extension_id, extension_ci in self.__extensions.items():
            extensions_functions[extension_id] = extension_ci.variables
            
        return extensions_functions


    @property
    def connected(self):
        return self.__connecte
    

    def _trigger_handlers(self, event:str, *args, **kwargs):
        logger.debug(f"Triggering '{event}' handlers...")
        for handler in self.__handlers[event]:
            handler(*args, **kwargs)
    
    def _trigger_hooks(self, event:str, value, *args, **kwargs):
        logger.debug(f"Triggering '{event}' hooks...")
        for hook in self.__hooks[event]:
            value = hook(value, *args, **kwargs)
            if not value:
                return None
        return value

    
    def send_message(self, *args, **kwargs):
        """
        Sends a message to the given JID.

        Args:
            jid (str): The JID to send the message to.
            message (str): The message to send.
            type (str): The message type. (Default: "chat")
        
        Example:
            >>> client.send_message("john@jabber.org", "Hello, John!")
        """

        jid = args[0] if len(args) > 0 else kwargs.get("jid")
        content = args[1] if len(args) > 1 else kwargs.get("message")
        msg_type = kwargs.get("type", "chat")

        XmppValidation.validate_jid(jid)

        message = XmppMessage()
        message.xml.add_attribute(XmlAttribute("to", jid))
        message.xml.add_attribute(XmlAttribute("type", msg_type))
        message.xml.add_attribute(XmlAttribute("id", str(uuid.uuid4())))

        message.xml.add_child(XmlElement("body"))
        message.body.xml.add_child(XmlTextElement(content))

        for hook in self.__hooks["send_message"]:
            message = hook(message, *args, **kwargs)

        if not message:
            return
        self._send_xml(message.xml)
    
    def reply_to_message(self, *args, **kwargs):
        """
        Replies to specific message.

        Args:
            message_id (str): The message ID to reply to.
            jid (str): The JID to send the message to.
            message (str): The message to send.
            type (str): The message type. (Default: "chat")
            message_author (str): The replied message author. If none, equals to jid. (Default: None)
        
        Example:
            >>> client.reply_to_message("12345678", "john@jabber.org", "Thanks, John!")
        """

        message_id = args[0] if len(args) > 0 else kwargs.get("message_id")
        jid = args[1] if len(args) > 1 else kwargs.get("jid")
        content = args[2] if len(args) > 2 else kwargs.get("message")
        msg_type = kwargs.get("type", "chat")
        message_author = kwargs.get("message_author", None)

        XmppValidation.validate_jid(jid)

        if message_author:
            XmppValidation.validate_jid(message_author)

        message = XmppMessage()
        message.xml.add_attribute(XmlAttribute("to", jid))
        message.xml.add_attribute(XmlAttribute("type", msg_type))
        message.xml.add_attribute(XmlAttribute("id", str(uuid.uuid4())))

        message.xml.add_child(XmlElement("body"))
        message.body.xml.add_child(XmlTextElement(content))

        message._xml.add_child(XmlElement("reply"))
        message.reply.xml.add_attribute(XmlAttribute("xmlns", "urn:xmpp:reply:0"))
        message.reply.xml.add_attribute(XmlAttribute("id", message_id))
        if message_author:
            message.reply.xml.add_attribute(XmlAttribute("to", message_author))
        else:
            message.reply.xml.add_attribute(XmlAttribute("to", jid))

        for hook in self.__hooks["send_message"]:
            message = hook(message, *args, **kwargs)

        if not message:
            return
        self._send_xml(message.xml)

    def edit_message(self, *args, **kwargs):
        """
        Editing specific message.

        Args:
            message_id (str): The message ID to edit.
            jid (str): The JID to send the message to.
            message (str): The message to send.
            type (str): The message type. (Default: "chat")
        
        Example:
            >>> client.edit_message("12345679", "john@jabber.org", "Thank you very much, John!")
        """

        message_id = args[0] if len(args) > 0 else kwargs.get("message_id")
        jid = args[1] if len(args) > 1 else kwargs.get("jid")
        content = args[2] if len(args) > 2 else kwargs.get("message")
        msg_type = kwargs.get("type", "chat")

        XmppValidation.validate_jid(jid)

        message = XmppMessage()
        message.xml.add_attribute(XmlAttribute("to", jid))
        message.xml.add_attribute(XmlAttribute("type", msg_type))
        message.xml.add_attribute(XmlAttribute("id", str(uuid.uuid4())))

        message.xml.add_child(XmlElement("body"))
        message.body.xml.add_child(XmlTextElement(content))

        message.xml.add_child(XmlElement("replace"))
        message.replace.xml.add_attribute(XmlAttribute("xmlns", "urn:xmpp:message-correct:0"))
        message.replace.xml.add_attribute(XmlAttribute("id", message_id))

        for hook in self.__hooks["send_message"]:
            message = hook(message, *args, **kwargs)

        if not message:
            return
        self._send_xml(message.xml)


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

        Example:
            >>> @client.on_message
            ... def on_message(message):
            ...     if message.body is None: #Messages body can be empty
            ...         return
            ...
            ...     print(f"Received message from {message.from_jid}: {message.body}")
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


    def hook_on_message(self, hook:Callable) -> Callable:
        """
        Registers a hook for the message event.
        The hook will be called when the client receives a message stanza.

        Args:
            hook (Callable): The hook to register.

        Returns:
            Callable: The hook (not changed).
        """
        self.__hooks["on_message"].append(hook)
        return hook
    
    def hook_on_presence(self, hook:Callable) -> Callable:
        """
        Registers a hook for the presence event.
        The hook will be called when the client receives a presence stanza.

        Args:
            hook (Callable): The hook to register.

        Returns:
            Callable: The hook (not changed).
        """
        self.__hooks["on_presence"].append(hook)
        return hook
    
    def hook_on_iq(self, hook:Callable) -> Callable:
        """
        Registers a hook for the iq event.
        The hook will be called when the client receives an iq stanza.

        Args:
            hook (Callable): The hook to register.

        Returns:
            Callable: The hook (not changed).
        """
        self.__hooks["on_iq"].append(hook)
        return hook
    
    def hook_send_message(self, hook:Callable) -> Callable:
        """
        Registers a hook for the send message event.
        The hook will be called when the client sends a message.
        
        Args:
            hook (Callable): The hook to register.
        
        Returns:
            Callable: The hook (not changed).
        """
        self.__hooks["send_message"].append(hook)
        return hook


    def _recv_xml(self) -> XmlElement:
        data = self.socket.recv(4096)
        return XmlParser.parse_elements(data.decode("utf-8"))[0]
    
    def _send_xml(self, xml:XmlElement):
        self.socket.sendall(xml.to_string().encode("utf-8"))


    def _start_xmpp_stream(self):
        logger.debug(f"Starting XMPP stream...")

        stream_start = XmlElement(
            "stream:stream", 
            attributes = [
                XmlAttribute("xmlns", "jabber:client"), 
                XmlAttribute("xmlns:stream", "http://etherx.jabber.org/streams"), 
                XmlAttribute("version", "1.0"), 
                XmlAttribute("to", self.host)
            ],
            is_closed=False
        )

        self._send_xml(stream_start)
    
    def _close_xmpp_stream(self):
        logger.debug(f"Closing XMPP stream...")

        self.socket.sendall(b"</stream:stream>")
    
    def _send_presence(self):
        logger.debug(f"Sending presence...")

        presence = XmlElement(
            "presence",
        )

        self._send_xml(presence)
    

    def _listen(self):
        logger.debug(f"Listening for XMPP stanzas...")

        buffer = ""

        while True:
            data = self.socket.recv(4096)
            if not data:
                self.disconnect()
                break

            buffer += data.decode("utf-8")

            try:
                elements = XmlParser.parse_elements(buffer)
                buffer = ""
            except Exception:
                # Incomplete stanza
                continue

            for element in elements:
                if element.name == "message":
                    message = XmppMessage(element)
                    hooks_result = self._trigger_hooks("on_message", message)
                    if hooks_result is None:
                        continue
                    self._trigger_handlers("message", hooks_result)

                elif element.name == "presence":
                    hooks_result = self._trigger_hooks("on_presence", element)
                    if hooks_result is None:
                        continue
                    self._trigger_handlers("presence", hooks_result)
                
                elif element.name == "iq":
                    hooks_result = self._trigger_hooks("on_iq", element)
                    if hooks_result is None:
                        continue
                    self._trigger_handlers("iq", hooks_result)

    def connect_feature(self, feature:XmppFeature, permissions: List[XmppPermission] | XmppPermission.ALL) -> None:
        """
        Connects the given feature to the XMPP client.

        Args:
            feature (XmppFeature): The feature to connect.
            permissions (List[XmppPermission] | XmppPermission.ALL): The permissions to grant.
        
        Example:
            >>> client.connect_feature(BindFeature("osmxmpp"), XmppPermission.ALL)
        """
        
        logger.debug(f"Connecting feature '{feature.ID}'...")

        XmppValidation.validate_id(feature.ID)

        feature_ci = XmppClientInterface(self, feature, permissions)

        feature._connect_ci(feature_ci)
        self.__features[feature.ID] = feature_ci
        self.__features_queue.append(feature.ID)

    def connect_features(self, features_with_permissions: List[Tuple[XmppFeature, List[XmppPermission] | XmppPermission.ALL]] ) -> None:
        """
        Connects the given features to the XMPP client.

        Args:
            features_with_permissions (List[Tuple[XmppFeature, List[XmppPermission] | XmppPermission.ALL]]): The features with permissions to connect
        
        Example:
            >>> client.connect_features([
            ...     (TLSFeature(), [XmppPersmision.SEND_XML, XmppPersmision.RECV_XML])
            ...     (BindFeature("osmxmpp"), XmppPermission.ALL)
            ... ])
        """

        for feature_with_permissions in features_with_permissions:
            self.connect_feature(feature_with_permissions[0], feature_with_permissions[1]) 


    def connect_extension(self, extension:XmppExtension, permissions: List[XmppPermission] | XmppPermission.ALL) -> None:
        """
        Connects the given extension to the XMPP client.

        Args:
            extension (XmppExtension): The extension to connect.
            permissions (List[XmppPermission] | XmppPermission.ALL): The permissions to grant.
        
        Example:
            >>> client.connect_extension(SomeExtension(), XmppPermission.ALL)
        """

        logger.debug(f"Connecting extension '{extension.ID}'...")

        XmppValidation.validate_id(extension.ID)

        extension_ci = XmppClientInterface(self, extension, permissions)
        
        extension._connect_ci(extension_ci)

        self.__extensions[extension.ID] = extension_ci
        self.__extensions_queue.append(extension.ID)

        self.__extensions[extension.ID].object._process()
    
    def connect_extensions(self, extensions_with_permissions: List[Tuple[XmppExtension, List[XmppPermission] | XmppPermission.ALL]] ) -> None:
        """
        Connects the given extensions to the XMPP client.

        Args:
            extensions_with_permissions (List[Tuple[XmppExtension, List[XmppPermission] | XmppPermission.ALL]]): The extensions with permissions to connect
        
        Example:
            >>> client.connect_extensions([
            ...     (SomeExtension(), [XmppPersmision.SEND_XML, XmppPersmision.RECV_XML])
            ...     (SomeOtherExtension(), XmppPermission.ALL)
            ... ])
        """

        for extension_with_permissions in extensions_with_permissions:
            self.connect_extension(extension_with_permissions[0], extension_with_permissions[1])


    def connect(self) -> None:
        """
        Connects to the XMPP server.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            self.socket.connect((self.host, self.port))

            self.__connected = True

            logger.info(f"Connected to {self.host}:{self.port}")

            self._trigger_handlers("connected")
            
            self._start_xmpp_stream()

            # Features can sometimes be placed immediately at the start of the stream
            def recv_xml_features():
                xml = self._recv_xml()
                name = "stream:features"

                if (xml.name == name):
                    return xml

                features = xml.children[0].get_child_by_name(name)
                if (features):
                    return features

                return self._recv_xml()
                

            features_xml = recv_xml_features()
            while True:
                if (features_xml is None):
                    raise Exception("No stream features received")
                    
                processed_feature = None
                for feature_id in self.__features_queue:
                    feature = self.__features[feature_id].object

                    feature_xml = features_xml.get_child_by_name(feature.TAG)
                    if feature_xml:
                        logger.debug(f"Processing feature '{feature.ID}'...")
                        
                        feature._process(feature_xml)
                        processed_feature = feature
                        break
                
                if (processed_feature and not processed_feature.RECEIVE_NEW_FEATURES):
                    break

                features_xml = recv_xml_features()
            
            self._send_presence()

            self._trigger_handlers("ready")

            self._listen()
            self.socket.close()
    
    def disconnect(self):
        """
        Disconnects from the XMPP server.
        """

        if not self.__connected:
            raise Exception("XmppClient is not connected")

        self._close_xmpp_stream()
        self.socket.close()
        self.__connected = False

        self._trigger_handlers("disconnected")
        logger.info(f"Disconnected from {self.host}:{self.port}")
    

    def __repr__(self):
        return f"<XmppClient {self.host}:{self.port}>"
