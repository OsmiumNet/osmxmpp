import base64
from osmxml import *
from .abc import XmppFeature
from ..permission import XmppPermission

from abc import ABC, abstractmethod
from typing import List

import logging

logger = logging.getLogger(__name__)

class SaslException(Exception):
    pass

class SaslMechanism(ABC):
    """
    SASL mechanisms are used to authenticate the user.

    Attributes:
        NAME (str): The name of the mechanism.
    """

    NAME = None

    @abstractmethod
    def process(self, ci):
        """
        Processes the mechanism.

        Args:
            ci (XmppClientInterface): The client interface given from the SaslFeature.
        """
        ...


class PlainMechanism(SaslMechanism):
    """
    PLAIN SASL mechanism implementation.

    Attributes:
        username (str): The username to authenticate with.
        password (str): The password to authenticate with.
    """

    NAME = "PLAIN"

    def __init__(self, username:str, password:str):
        self.__auth_string = f"\0{username}\0{password}"
        self.__auth_string = base64.b64encode(self.__auth_string.encode("utf-8")).decode()

    def process(self, ci):
        auth_xml = XmlElement(
            "auth",

            attributes = [
                XmlAttribute("xmlns", "urn:ietf:params:xml:ns:xmpp-sasl"),
                XmlAttribute("mechanism", "PLAIN"),
            ],

            children = [
                XmlTextElement(self.__auth_string),
            ]
        )

        ci.send_xml(auth_xml)
        data = ci.recv_xml()

        return data


class SaslFeature(XmppFeature):
    """
    SASL feature implementation.

    Attributes:
        mechanisms (List[SaslMechanism]): The SASL mechanisms to use.
    
    Raises:
        SaslException: If authentication fails.
    """

    ID = "osmiumnet.sasl"
    TAG = "mechanisms"

    RECEIVE_NEW_FEATURES = True

    REQUIRED_PERMISSIONS: List[XmppPermission] = [
        XmppPermission.SEND_XML,
        XmppPermission.RECV_XML,
        XmppPermission.OPEN_STREAM,
    ]

    def __init__(self, mechanisms:List[SaslMechanism]):
        self.__mechanisms = mechanisms
    
    def _connect_ci(self, ci):
        self.__ci = ci
    
    def _process(self, element):
        mechanisms_xml = element

        logger.debug(f"Processing mechanisms...")

        recv_data = None
        for mechanism in self.__mechanisms:
            if mechanism.NAME in [mechanism_xml.children[0].text for mechanism_xml in mechanisms_xml.children]:
                logger.debug(f"Processing mechanism '{mechanism.NAME}'...")
                recv_data = mechanism.process(self.__ci)
                break
        
        if recv_data is None or recv_data.name != "success":
            raise SaslException("SASL authentication failed")
        
        self.__ci.open_stream()
