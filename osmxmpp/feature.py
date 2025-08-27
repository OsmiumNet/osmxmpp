from .client import XMPPClient
from osmxml import *
import socket, ssl

class XMPPFeature:
    def __init__(self):
        pass

    def handle_client(self, client:XMPPClient, feature:XMLElement) -> XMLElement:
        pass

class TLSFeature(XMPPFeature):
    def __init__(self, verify_locations=None):
        super().__init__()

        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.ssl_context.check_hostname = True
        self.ssl_context.verify_mode = ssl.CERT_REQUIRED

        if verify_locations is not None:
            self.ssl_context.load_verify_locations(verify_locations)

    def handle_client(self, client:XMPPClient, feature:XMLElement) -> XMLElement:
        if feature.name != "starttls":
            return None

        tls_handshake = XMLElement(
            "starttls",

            attributes = [
                XMLAttribute("xmlns", "urn:ietf:params:xml:ns:xmpp-tls")
            ]
        )

        client.socket.sendall(tls_handshake.to_string().encode("utf-8"))

        data = client.socket.recv(4096)
        data = XMLParser.parse_elements(data.decode("utf-8"))[0]

        tls_socket = self.ssl_context.wrap_socket(client.socket, server_hostname=client.server)
        client.socket = tls_socket
        client.socket.do_handshake()
        
        client._start_xmpp_stream()
        return client._receive_stream_features()