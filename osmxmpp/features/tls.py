from .abc import XmppFeature
from osmxml import *
import socket, ssl

import logging

logger = logging.getLogger(__name__)

class TlsFeature(XmppFeature):
    """
    TLS feature implementation.

    Attributes:
        ssl_context (ssl.SSLContext): The SSL context to use.
        verify_locations (List[str]): The locations to verify the server certificate.
    """

    ID = "osmiumnet.tls"
    TAG = "starttls"

    RECEIVE_NEW_FEATURES = True

    REQUIRED_PERMISSIONS: List[XmppPermission] = [
        XmppPermission.SEND_XML,
        XmppPermission.RECV_XML,
        XmppPermission.OPEN_STREAM,
        XmppPermission.GET_HOST,
        XmppPermission.GET_SOCKET,
        XmppPermission.CHANGE_SOCKET,
    ]

    def __init__(self, ssl_context=None, verify_locations=None):
        if ssl_context is None:
            logger.debug(f"Creating default SSL context...")
            self.__ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            self.__ssl_context.check_hostname = True
            self.__ssl_context.verify_mode = ssl.CERT_REQUIRED

        if verify_locations is not None:
            logger.debug(f"Loading verify locations...")
            self.__ssl_context.load_verify_locations(verify_locations)
    
    def _connect_ci(self, ci):
        self.__ci = ci

    def _process(self, element):
        tls_handshake = XmlElement(
            "starttls",

            attributes = [
                XmlAttribute("xmlns", "urn:ietf:params:xml:ns:xmpp-tls")
            ]
        )

        logger.debug(f"Sending TLS handshake...")
        self.__ci.send_xml(tls_handshake)
        data = self.__ci.recv_xml()

        if data.name != "proceed":
            return None
        
        logger.debug(f"Wrapping socket...")
        tls_socket = self.__ssl_context.wrap_socket(self.__ci.get_socket(), server_hostname=self.__ci.get_host())
        
        logger.debug(f"Performing TLS handshake...")
        tls_socket.do_handshake()

        logger.debug(f"Done! Changing client socket...")
        self.__ci.change_socket(tls_socket)
        
        self.__ci.open_stream()
