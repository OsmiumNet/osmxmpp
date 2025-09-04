import base64
from osmxml import *
from .abc import XMPPFeature

from abc import ABC, abstractmethod
from typing import List

import logging

logger = logging.getLogger(__name__)

class SASLException(Exception):
    pass

class SASLMechanism(ABC):
    """
    SASL mechanisms are used to authenticate the user.

    Attributes:
        name (str): The name of the mechanism.
    """

    name = None

    @abstractmethod
    def process(self, ci):
        """
        Processes the mechanism.

        Args:
            ci (XMPPClientInterface): The client interface given from the SASLFeature.
        """
        ...


class PLAINMechanism(SASLMechanism):
    """
    PLAIN SASL mechanism implementation.

    Attributes:
        username (str): The username to authenticate with.
        password (str): The password to authenticate with.
    """

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
    """
    SASL feature implementation.

    Attributes:
        mechanisms (List[SASLMechanism]): The SASL mechanisms to use.
    
    Raises:
        SASLException: If authentication fails.
    """

    id = "osmiumnet.sasl"
    tag = "mechanisms"

    receive_new_features = True

    def __init__(self, mechanisms:List[SASLMechanism]):
        self.__mechanisms = mechanisms
    
    def connect_ci(self, ci):
        self.__ci = ci
    
    def process(self, element):
        mechanisms_xml = element

        logger.debug(f"Processing mechanisms...")

        recv_data = None
        for mechanism in self.__mechanisms:
            if mechanism.name in [mechanism_xml.children[0].text for mechanism_xml in mechanisms_xml.children]:
                logger.debug(f"Processing mechanism '{mechanism.name}'...")
                recv_data = mechanism.process(self.__ci)
                break
        
        if recv_data is None or recv_data.name != "success":
            raise SASLException("SASL authentication failed")
        
        self.__ci.open_stream()
