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
    REQUIRED_PERMISSIONS: List[XmppPermission] = [
        XmppPermission.SEND_XML,
    ]

    def __init__(self):
        pass
     
    def _connect_ci(self, ci):
        self.__ci = ci
    
    def discover(self):
        """
        Sends a service discovery request.

        Example:
            >>> client.extensions["osmiumnet.service.discovery"].discover()
        """

        xml = DiscoveryXml.discover()
        self.__ci.send_xml(xml)

    def _process(self):
        # Variables
        self.__ci.variables.function(self.discover)

