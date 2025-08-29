from .feature import XMPPFeature
from osmxml import *

class BindFeature(XMPPFeature):
    """
    Bind feature implementation.

    Attributes:
        resource (str): The resource to bind to.
    """

    id = "osmiumnet.bind"
    tag = "bind"

    receive_new_features = False

    def __init__(self, resource:str):
        self.__resource = resource
    
    def connect_ci(self, ci):
        self.__ci = ci
    
    def process(self, element):
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
                                XMLTextElement(self.__resource)
                            ]
                        )
                    ]
                )
            ]
        )

        self.__ci.send_xml(bind_xml)
        data = self.__ci.recv_xml()

        if data.name != "iq":
            return None
        
        if data.get_attribute_by_name("type").value != "result":
            return None

        if data.get_child_by_name("bind") is None:
            return None

        jid = data.get_child_by_name("bind").get_child_by_name("jid").children[0].text

        self.__ci.set_jid(jid)
        self.__ci.set_resource(self.__resource)