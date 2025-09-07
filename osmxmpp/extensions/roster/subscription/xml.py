import uuid

from osmxml import XmlParser
from osmxml import XmlElement
from osmxml import XmlAttribute
from osmxml import XmlTextElement

class SubscriptionXml:
    @staticmethod
    def check_for_subscription(jid: str) -> XmlElement:
        xml_str = f"""
        <iq from='{jid}' type='get' id='{SubscriptionXml.make_id()}'>
          <query xmlns='jabber:iq:roster'/>
        </iq>        
        """
        return XmlParser.parse_elements(xml_str)[0]

    @staticmethod
    def check_for_subscription_filter(xml: XmlElement) -> bool:
        if (xml.name != "iq"):
            return False

        query = xml.get_child_by_name("query")
        if (query is None):
            return False

        query_xmlns = query.get_attribute_by_name("xmlns")
        if ((query_xmlns is None) or (query_xmlns.value != "jabber:iq:roster")):
            return False

        return True 

    @staticmethod
    def send_presence(jid_to: str) -> XmlElement:
        xml_str = f"""
        <presence to='{jid_to}'>
          <show>chat</show>
          <status>Available for OMEMO</status>
        </presence>
        """
        return XmlParser.parse_elements(xml_str)[0]

    @staticmethod
    def send_subscribe(jid_to: str) -> XmlElement:
        xml_str = f"""
        <presence type='subscribe' to='{jid_to}'>
          <status>Subscription</status>
        </presence>
        """
        return XmlParser.parse_elements(xml_str)[0]

    @staticmethod
    def send_subscribe_filter(xml: XmlElement) -> bool:
        if (xml.name != "presence"):
            return False

        presence_type = xml.get_attribute_by_name("type")
        if ((presence_type is None) or (presence_type.value != "subscribe")):
            return False

        return True 

    @staticmethod
    def send_subscribed(jid_to: str) -> XmlElement:
        xml_str = f"""
        <presence type='subscribed' to='{jid_to}'/>
        """
        return XmlParser.parse_elements(xml_str)[0]

    @staticmethod
    def make_id():
        return str(uuid.uuid4()) 

