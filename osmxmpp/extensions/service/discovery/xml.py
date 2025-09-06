import uuid

from osmxml import XmlParser
from osmxml import XmlElement
from osmxml import XmlAttribute
from osmxml import XmlTextElement

class DiscoveryXml:
    @staticmethod
    def discover() -> XmlElement:
        xml_str = f"""
        <iq type='get' id='{DiscoveryXml.make_id()}'>
          <query xmlns='http://jabber.org/protocol/disco#info'/>
        </iq>
        """
        return XmlParser.parse_elements(xml_str)[0]

    @staticmethod
    def make_id():
        return str(uuid.uuid4()) 

