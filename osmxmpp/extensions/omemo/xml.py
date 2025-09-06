import uuid

from typing import List

from osmxml import XMLParser
from osmxml import XMLElement
from osmxml import XMLAttribute
from osmxml import XMLTextElement

from osmomemo import OmemoBundle

class OmemoXml:
    @staticmethod
    def send_presence(jid_to: str) -> XMLElement:
        xml_str = f"""
        <presence to='{jid_to}'>
          <show>chat</show>
          <status>Available for OMEMO</status>
        </presence>
        """
        return XMLParser.parse_elements(xml_str)[0]

    @staticmethod
    def send_subscribe(jid_to: str) -> XMLElement:
        xml_str = f"""
        <presence type='subscribe' to='{jid_to}'>
          <status>OMEMO setup - requesting subscription</status>
        </presence>
        """
        return XMLParser.parse_elements(xml_str)[0]

    @staticmethod
    def send_subscribed(jid_to: str) -> XMLElement:
        xml_str = f"""
        <presence type='subscribed' to='{jid_to}'/>
        """
        return XMLParser.parse_elements(xml_str)[0]

    @staticmethod
    def check_node_exists(jid: str) -> XMLElement:
        xml_str = f"""
        <iq type='get' id='{OmemoXml.make_id()}' to='{jid}'>
          <query xmlns='http://jabber.org/protocol/disco#items' node='urn:xmpp:omemo:2:devices'/>
        </iq>
        """
        return XMLParser.parse_elements(xml_str)[0]

    @staticmethod
    def publish_device_list_setup(jid: str) -> XMLElement:
        xml_str = f"""
        <iq type='set' id='{OmemoXml.make_id()}' to='{jid}'>
          <pubsub xmlns='http://jabber.org/protocol/pubsub'>
            <create node='urn:xmpp:omemo:2:devices'/>
            <configure>
              <x xmlns='jabber:x:data' type='submit'>
                <field var='FORM_TYPE' type='hidden'>
                  <value>http://jabber.org/protocol/pubsub#node_config</value>
                </field>
                <field var='pubsub#access_model'><value>open</value></field>
                <field var='pubsub#persist_items'><value>true</value></field>
                <field var='pubsub#max_items'><value>1</value></field>
              </x>
            </configure>
          </pubsub>
        </iq>
        """
        return XMLParser.parse_elements(xml_str)[0]

    @staticmethod
    def publish_device(jid: str, device: int, lable: str = "OsmiumNet") -> XMLElement:
        xml_str = f"""
        <iq to='{jid}' type='set' id='{OmemoXml.make_id()}' >
          <pubsub xmlns='http://jabber.org/protocol/pubsub'>
            <publish node='urn:xmpp:omemo:2:devices'>
              <item id='current'>
                <devices xmlns='urn:xmpp:omemo:2'>
                  <device id='{device}' label='{lable}'/>
                </devices>
              </item>
            </publish>
          </pubsub>
        </iq>
        """
                
        return XMLParser.parse_elements(xml_str)[0]

    @staticmethod
    def publish_bundle_information(jid: str, bundle: OmemoBundle) -> XMLElement:
        device_id = bundle.get_device_id()
        ik = bundle.get_indentity().get_base64_public_key() 
        spk = bundle.get_prekey().get_base64_public_key()
        spk_sign = bundle.get_prekey_signature()

        opks_xml = XMLElement(
            name="prekeys",
            children=[
                XMLElement(
                    name="pk",
                    attributes=[
                        XMLAttribute("id", str(i))
                    ],
                    children=[
                        XMLTextElement(opk.get_base64_public_key())
                    ]
                ) for i, opk in bundle.get_onetime_prekeys().items()
            ]
        ).to_string()

        xml_str = f"""
        <iq from='{jid}' type='set' id='{OmemoXml.make_id()}'>
          <pubsub xmlns='http://jabber.org/protocol/pubsub'>
            <publish node='urn:xmpp:omemo:2:bundles'>
              <item id='{device_id}'>
                <bundle xmlns='urn:xmpp:omemo:2'>
                  <ik>{ik}</ik>
                  <spk id='0'>{spk}</spk>
                  <spks>{spk_sign}</spks>
                  <prekeys>
                    {opks_xml} 
                  </prekeys>
                </bundle>
              </item>
            </publish>
          </pubsub>
        </iq>
        """
        return XMLParser.parse_elements(xml_str)[0]

    @staticmethod
    def fetch_devices(jid: str, jid_to: str) -> XMLElement:
        xml_str = f"""
        <iq type='get'
            from='{jid}'
            to='{jid_to}'
            id='{OmemoXml.make_id()}'>
          <pubsub xmlns='http://jabber.org/protocol/pubsub'>
            <items node='urn:xmpp:omemo:2:devices'/>
          </pubsub>
        </iq>
        """
        return XMLParser.parse_elements(xml_str)[0]

    @staticmethod
    def fetch_bundles(jid: str, jid_to: str, device_to: int) -> XMLElement:
        xml_str = f"""
        <iq type='get' from='{jid}' to='{jid_to}' id='{OmemoXml.make_id()}'>
          <pubsub xmlns='http://jabber.org/protocol/pubsub'>
            <items node='urn:xmpp:omemo:2:bundles'>
              <item id='{device_to}'/>
            </items>
          </pubsub>
        </iq>
        """
        return XMLParser.parse_elements(xml_str)[0]

    @staticmethod
    def send_init_message(
                jid: str, 
                jid_to: str, 
                device: int, 
                device_to: int,
                wrapped: str,
            ) -> XMLElement:
        xml_str = f"""
        <message from="{jid}" to="{jid_to}" type="chat" id="{OmemoXml.make_id()}">
            <encrypted xmlns="urn:xmpp:omemo:2">
                <header sid="{device}">
                    <keys jid="{jid_to}">
                        <key rid="{device_to}" kex="true">
                             {wrapped}
                        </key>
                    </keys>
                </header>
                <payload>
                     {XMLTextElement("ciphertext-of-sce-envelope").to_string()}
                </payload>
            </encrypted>
            <body>
                [This message is OMEMO encrypted.]
            </body>
        </message>
        """
        return XMLParser.parse_elements(xml_str)[0]

    @staticmethod
    def send_message(
                jid: str, 
                jid_to: str, 
                device: int, 
                keys: List[XMLElement],
                payload: str,
            ) -> XMLElement:
        xml_str_keys = "\n".join([nkey.to_string(raw=False) for nkey in keys]) 
        xml_str = f"""
        <message from="{jid}" to="{jid_to}" type="chat" id="{OmemoXml.make_id()}">
            <encrypted xmlns="urn:xmpp:omemo:2">
                <header sid="{device}">
                    {xml_str_keys}
                </header>
                <payload>
                    {payload}
                </payload>
            </encrypted>
            <body>
                [This message is OMEMO encrypted.]
            </body>
        </message>
        """
        return XMLParser.parse_elements(xml_str)[0]

    @staticmethod
    def make_id():
        return str(uuid.uuid4()) 

