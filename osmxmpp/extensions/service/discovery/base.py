from typing import Callable, List, Tuple, Dict

from ...abc import XmppExtension
from ....message import XmppMessage
from ....permission import XmppPermission

from .xml import DiscoveryXml


class ServiceDiscoveryExtension(XmppExtension):
    """
    XEP-0030: Service Discovery implementation.
    """

    ID = "osmiumnet.service.discovery"

    # List of required permissions
    REQUIREMENTS: List[XmppPermission] = [
        XmppPermission.SEND_XML,
    ]

    def __init__(self):
        pass
     
    def connect_ci(self, ci):
        self.__ci = ci

    def process(self):
        # Variables
        @self.__ci.variables.function
        def discover():
            xml = DiscoveryXml.discover()
            self.__ci.send_xml(xml)

