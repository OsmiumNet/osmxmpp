from typing import Callable, List, Tuple, Dict

from osmxml import XmlElement

from ...abc import XmppExtension
from ....message import XmppMessage
from ....permission import XmppPermission

from .xml import SubscriptionXml


class SubscriptionExtension(XmppExtension):
    """
    XEP-0379: Pre-Authenticated Roster Subscription implementation.
    """

    ID = "osmiumnet.roster.subscription"

    # List of required permissions
    REQUIREMENTS: List[XmppPermission] = [
        XmppPermission.GET_JID,
        XmppPermission.SEND_XML,
        XmppPermission.LISTEN_ON_READY,
        XmppPermission.LISTEN_ON_PRESENCE,
        XmppPermission.LISTEN_ON_IQ,
    ]

    def __init__(self):
        self.__ensure_list: List[str] = [] 

        self.__handlers = {
            "on_check_subscriptions": [],
        }
     
    def connect_ci(self, ci):
        self.__ci = ci

    def process(self):
        # Listeners
        @self.__ci.on_presence
        def on_presence(presence: XmlElement):
            self.__on_presence(presence)
        
        # Hooks
        @self.__ci.hook_on_iq
        def hook_on_iq(iq: XmlElement):
            self.__hook_on_iq(iq)

        # Variables
        @self.__ci.variables.function
        def on_check_subscriptions(handler:Callable):
            self.__handlers["on_check_subscriptions"].append(handler)
            return handler

        @self.__ci.variables.function
        def check_for_subscriptions():
            xml = SubscriptionXml.check_for_subscription(self.__ci.get_jid(False))
            self.__ci.send_xml(xml)

        @self.__ci.variables.function
        def ensure_subscription(jid_to: str):
            self.__ensure_list.append(jid_to)


    def __on_presence(self, presence: XmlElement):
        if(SubscriptionXml.send_subscribe_filter(presence)):
            # If it receives subscribe request, and jid in ensure list,
            # it sends subscribed to it
            jid = presence.get_attribute_by_name("from")
            if (jid in self.__ensure_list):
                # Send subscribed
                xml = SubscriptionXml.send_subscribed(jid)
                self.__ci.send_xml(xml)

    def __hook_on_iq(self, iq: XmlElement):
        calls = [
            self.__process_check_subscriptions(iq),
        ]

        if True in calls:
            return

        return iq
    
    def __process_check_subscriptions(self, iq: XmlElement):
        iq_type = iq.get_attribute_by_name("type").value
        if not (SubscriptionXml.check_for_subscription_filter(iq) and iq_type == "result"):
            return False
        
        query = iq.get_child_by_name("query")
        
        # Get subscribed query children
        subscribed_children_list = []
        ask_children_list = []
        for query_child in query.children:
            if (query_child.name == "item"):
                jid = query_child.get_attribute_by_name("jid").value
                # Check subscription status
                subscription_status = query_child.get_attribute_by_name("subscription").value
                if (subscription_status == "both"):
                    subscribed_children_list.append(jid)
                elif (subscription_status == "none"):
                    ask =  query_child.get_attribute_by_name("ask").value
                    if (ask == "subscribe"):
                        ask_children_list.append(jid)

        # If jid from ensure list is not subsribed, it sends subscription to it
        for ensure_jid in self.__ensure_list:
            if (ensure_jid not in subscribed_children_list):
                # Send to subscribe
                xml = SubscriptionXml.send_subscribe(ensure_jid)
                self.__ci.send_xml(xml)

                xml = SubscriptionXml.send_presence(ensure_jid)
                self.__ci.send_xml(xml)

        # If jid from ask list is in ensure list, it sends subscribed to it
        for ask_child in ask_children_list:
            if (ask_child in self.__ensure_list):
                # Send subscribed
                xml = SubscriptionXml.send_subscribed(ensure_jid)
                self.__ci.send_xml(xml)
        
        return True
