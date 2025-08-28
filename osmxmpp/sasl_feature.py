import base64
from osmxml import *
from .feature import XMPPFeature

class SASLMechanism:
    def __init__(self):
        pass

class PLAINMechanism(SASLMechanism):
    def __init__(self, username:str, password:str):
        super().__init__()

        self.__auth_string = f"\0{username}\0{password}"
        self.__auth_string = base64.b64encode(self.__auth_string.encode("utf-8")).decode()

    def handle_client(self, client, mechanisms):
        if "PLAIN" in [str(mechanism.children[0].value) for mechanism in mechanisms]:
            auth_xml = XMLElement(
                "auth",

                attributes = [
                    XMLAttribute("xmlns", "urn:ietf:params:xml:ns:xmpp-sasl"),
                    XMLAttribute("mechanism", "PLAIN"),
                ],

                children = [
                    XMLTextElement(self.__auth_string),
                ]
            )

            client.socket.sendall(auth_xml.to_string().encode("utf-8"))

            data = client.socket.recv(4096)
            data = XMLParser.parse_elements(data.decode("utf-8"))[0]

            client._start_xmpp_stream()

            return client._receive_stream_features()


class SASLFeature(XMPPFeature):
    def __init__(self, mechanisms):
        super().__init__()
        self.mechanisms = mechanisms
    
    def handle_client(self, client, feature):
        if not feature.name == "mechanisms":
            return None

        features_xml = None
        for mechanism in self.mechanisms:
            features_xml = mechanism.handle_client(client, feature.children)
            if features_xml is not None:
                break
        
        return features_xml
