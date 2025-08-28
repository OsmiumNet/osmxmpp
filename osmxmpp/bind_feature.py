from .feature import XMPPFeature
from osmxml import *

class BindFeature(XMPPFeature):
    def __init__(self, resource:str):
        self.resource = resource
        super().__init__()
    
    def handle_client(self, client, feature):
        if not feature.name == "bind":
            return None
        
        bind_xml = XMLElement(
            "iq",

            attributes = [
                XMLAttribute("type", "set"),
                XMLAttribute("id", "bind_1"),
            ],

            children = [
                XMLElement(
                    "bind",

                    attributes = [
                        XMLAttribute("xmlns", "urn:ietf:params:xml:ns:xmpp-bind")
                    ],

                    children = [
                        XMLElement(
                            "resource",
                            children = [
                                XMLTextElement(self.resource)
                            ]
                        )
                    ]
                )
            ]
        )

        client.socket.sendall(bind_xml.to_string().encode("utf-8"))

        data = client.socket.recv(4096)
        data = XMLParser.parse_elements(data.decode("utf-8"))[0]

        if data.name != "iq":
            return None
        
        if data.get_attribute_by_name("type").value != "result":
            return None

        if data.get_child_by_name("bind") is None:
            return None
        
        jid = data.get_child_by_name("bind").get_child_by_name("jid").text

        client.jid = jid
        client.resource = self.resource

        return