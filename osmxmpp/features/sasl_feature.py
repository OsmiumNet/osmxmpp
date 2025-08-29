import base64
from osmxml import *
from .feature import XMPPFeature

from abc import ABC, abstractmethod
from typing import List

class SASLMechanism(ABC):
    name = None

    @abstractmethod
    def process(self, ci):
        ...

class PLAINMechanism(SASLMechanism):
    name = "PLAIN"

    def __init__(self, username:str, password:str):
        self.__auth_string = f"\0{username}\0{password}"
        self.__auth_string = base64.b64encode(self.__auth_string.encode("utf-8")).decode()

    def process(self, ci):
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

        ci.send_xml(auth_xml)
        data = ci.recv_xml()

        return data


class SASLFeature(XMPPFeature):
    id = "osmiumnet.sasl"
    tag = "mechanisms"

    receive_new_features = True

    def __init__(self, mechanisms:List[SASLMechanism]):
        self.__mechanisms = mechanisms
    
    def connect_ci(self, ci):
        self.__ci = ci
    
    def process(self, element):
        mechanisms_xml = element

        recv_data = None
        for mechanism in self.__mechanisms:
            if mechanism.name in [mechanism_xml.children[0].text for mechanism_xml in mechanisms_xml.children]:
                recv_data = mechanism.process(self.__ci)
                break
        
        if recv_data is None or recv_data.name != "success":
            raise Exception("SASL authentication failed")
        
        self.__ci.open_stream()
