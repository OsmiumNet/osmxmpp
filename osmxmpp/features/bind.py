from typing import List

from .abc import XmppFeature
from ..permission import XmppPermission

from osmxml import *

import logging


logger = logging.getLogger(__name__)


class BindFeature(XmppFeature):
    """
    Bind feature implementation.

    Attributes:
        resource (str): The resource to bind to.
    """

    ID = "osmiumnet.bind"
    TAG = "bind"

    RECEIVE_NEW_FEATURES = False

    REQUIRED_PERMISSIONS: List[XmppPermission] = [
        XmppPermission.SEND_XML,
        XmppPermission.RECV_XML,
        XmppPermission.SET_JID,
        XmppPermission.SET_RESOURCE,
    ]

    def __init__(self, resource:str):
        self.__resource = resource
    
    def _connect_ci(self, ci):
        self.__ci = ci
    
    def _process(self, element):
        bind_xml = XmlElement(
            "iq",

            attributes = [
                XmlAttribute("type", "set"),
                XmlAttribute("id", "bind_1"),
            ],

            children = [
                XmlElement(
                    "bind",

                    attributes = [
                        XmlAttribute("xmlns", "urn:ietf:params:xml:ns:xmpp-bind")
                    ],

                    children = [
                        XmlElement(
                            "resource",
                            children = [
                                XmlTextElement(self.__resource)
                            ]
                        )
                    ]
                )
            ]
        )

        logger.debug(f"Sending bind request...")

        self.__ci.send_xml(bind_xml)
        data = self.__ci.recv_xml()

        if data.name != "iq":
            return None
        
        if data.get_attribute_by_name("type").value != "result":
            return None

        if data.get_child_by_name("bind") is None:
            return None

        jid = data.get_child_by_name("bind").get_child_by_name("jid").children[0].text

        logger.debug(f"Binded to '{jid}'!")

        self.__ci.set_jid(jid)
        self.__ci.set_resource(self.__resource)
