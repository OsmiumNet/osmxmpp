from .feature import XMPPFeature
from osmxml import *
import socket, ssl

class TLSFeature(XMPPFeature):
    id = "osmiumnet.tls"
    tag = "starttls"

    receive_new_features = True

    def __init__(self, ssl_context=None, verify_locations=None):
        if ssl_context is None:
            self.__ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            self.__ssl_context.check_hostname = True
            self.__ssl_context.verify_mode = ssl.CERT_REQUIRED

        if verify_locations is not None:
            self.__ssl_context.load_verify_locations(verify_locations)
    
    def connect_ci(self, ci):
        self.__ci = ci

    def process(self, element):
        tls_handshake = XMLElement(
            "starttls",

            attributes = [
                XMLAttribute("xmlns", "urn:ietf:params:xml:ns:xmpp-tls")
            ]
        )

        self.__ci.send_xml(tls_handshake)
        data = self.__ci.recv_xml()

        tls_socket = self.__ssl_context.wrap_socket(self.__ci.get_socket(), server_hostname=self.__ci.get_host())
        tls_socket.do_handshake()

        self.__ci.change_socket(tls_socket)
        
        self.__ci.open_stream()