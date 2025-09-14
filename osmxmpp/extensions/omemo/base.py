import os
import base64
import json
import time
import random
import struct
import secrets

from typing import Callable, List, Tuple, Dict

from osmxml import XmlParser, XmlElement, XmlAttribute, XmlTextElement

from osmomemo import Omemo, OmemoBundle, XKeyPair, EdKeyPair
from osmomemo.storage import OmemoStorage

from ..abc import XmppExtension
from ...message import XmppMessage
from ...permission import XmppPermission

from .xml import OmemoXml


class OmemoExtension(XmppExtension):
    """
    XEP-0384: OMEMO Encryption implementation.
    """

    ID = "osmiumnet.omemo"

    # List of required permissions
    REQUIREMENTS: List[XmppPermission] = [
        XmppPermission.GET_JID,
        XmppPermission.SEND_XML,
        XmppPermission.LISTEN_ON_READY,
        XmppPermission.LISTEN_ON_IQ,
        XmppPermission.HOOK_ON_MESSAGE,
        XmppPermission.HOOK_SEND_MESSAGE,
    ]

    def __init__(self, bundle: OmemoBundle, storage: OmemoStorage):
        self.__bundle = bundle
        self.__omemo = Omemo(self.__bundle, storage)

        self.__registered_xmls: Dict[str, str] = {}

        self.__contact_bundles = {}

    def _connect_ci(self, ci):
        self.__ci = ci

    def _process(self):
        # Listeners
        @self.__ci.on_ready
        def on_ready():
            self.__on_ready()

        @self.__ci.on_iq
        def on_iq(iq):
            self.__on_iq(iq)


        # Hooks
        @self.__ci.hook_on_message
        def hook_on_message(message: XmppMessage):
            return self.__hook_on_message(message)

        @self.__ci.hook_send_message
        def hook_send_message(message: XmppMessage, *args, **kwargs):
            return self.__hook_send_message(message)


        # Variables
        @self.__ci.variables.function
        def publish_device_information():
            xml = OmemoXml.publish_device(self.__ci.get_jid(False), self.__bundle.get_device_id())
            self.__send_registered_xml(xml, "publish_device:func")

        @self.__ci.variables.function
        def fetch_bundles(jid: str | List[str]):
            if (isinstance(jid, list)):
                for j in jid:
                    self.fetch_bundles(j)
            else:
                self.fetch_bundles(jid)

    def fetch_bundles(self, jid):
        """
        Fetches the bundles from the given JID.

        Args:
            jid (str): The JID to fetch the bundles from.
        
        Example:
            >>> client.extensions["osmiumnet.omemo"].fetch_bundles("john@jabber.org")
        """

        xml = OmemoXml.fetch_devices(self.__ci.get_jid(), jid)
        self.__send_registered_xml(xml, "fetch_devices:func")


    def __send_registered_xml(self, xml: XmlElement, name: str):
        self.__register_xml(xml, name)
        self.__ci.send_xml(xml)


    # Manage text to ensure they were sent from the extension 
    def __register_xml(self, xml: XmlElement, name: str):
        xml_id = xml.get_attribute_by_name("id").value
        if (xml_id):
            self.__registered_xmls[xml_id] = name

    def __get_xml_registration(self, xml: XmlElement) -> Tuple[bool, str]:
        is_registered = False
        name = ""

        id_attr = xml.get_attribute_by_name("id")
        if (id_attr):
            xml_id =    id_attr.value 
            is_registered = xml_id in self.__registered_xmls 
            if (is_registered):
                name = self.__registered_xmls[xml_id]
                del self.__registered_xmls[xml_id]
        return is_registered, name
    


    # Client events 
    def __on_ready(self):
        pass

    def __on_iq(self, iq):
        is_registered, name = self.__get_xml_registration(iq)

        if (not is_registered):
            return

        if (name == "publish_device:func"):
            xml = OmemoXml.publish_bundle_information(self.__ci.get_jid(False), self.__bundle)
            self.__send_registered_xml(xml, "publish_bundle_information")
        elif (name == "fetch_devices:func"):
            self.__parse_devices_response(iq)

            # Fetch bundles for contacts devices that are not cached yet
            for contact_jid, devices in self.__contact_bundles.items():
                for contact_device, bundle in self.__contact_bundles[contact_jid].items():
                    if (bundle == {}):
                        xml = OmemoXml.fetch_bundles(self.__ci.get_jid(), contact_jid, contact_device)
                        self.__send_registered_xml(xml, "fetch_bundles")
        elif (name == "fetch_bundles"):
            self.__parse_bundle_response(iq)

    def __hook_on_message(self, message: XmppMessage):
        final_message = None

        jid_from = message.from_jid.split("/")[0]
        if (message.encrypted):
            # Find and store JID keys
            device_keys = None
            for jid_keys in message.encrypted.header.xml.children:
                jid = jid_keys.get_attribute_by_name("jid").value
                if (self.__ci.get_jid(False) == jid):
                    device_keys = jid_keys
                    break

            if (not device_keys):
                return message

            # Find and store that device key
            device_key = None
            for key in device_keys.children:
                rid = key.get_attribute_by_name("rid").value
                device_rid = self.__bundle.get_device_id()
                if (device_rid == int(rid)):
                    device_key = key
                    break

            if (not device_key):
                return message

            key_data = device_key.children[0].to_string()
            device_from = int(message.encrypted.header.xml.get_attribute_by_name("sid").value)

            devices = self.__omemo.get_device_list(jid_from)
            if (type(devices) == list):
                key_data_js = json.loads(base64.b64decode(key_data).decode('utf-8'))

                wrapped = key_data_js["k"]
                payload = key_data_js["p"]

                wrapped_key_bytes = base64.b64decode(wrapped.encode("utf-8"))
                payload_bytes = base64.b64decode(payload.encode("utf-8"))

                de_message = self.__omemo.receive_message(
                            jid=jid_from, 
                            device=device_from,
                            wrapped_message_key=wrapped_key_bytes, 
                            payload=payload_bytes
                )

                final_massage = message
                final_massage.body = de_message.decode("utf-8")
            else:
                de_message = self.__receive_init_message(jid_from, device_from, key_data)

                if (de_message):
                    final_massage = message
                    final_massage.body = de_message

        return final_message if final_message else message 

    def __hook_send_message(self, message: XmppMessage):
        final_message = None

        jid_to = message.to_jid.split("/")[0]
        body = message.body
        encrypted_message = None

        devices = self.__omemo.get_device_list(jid_to)
        if (type(devices) == list):
            xml_keys = XmlElement("keys", [XmlAttribute("jid", jid_to)])
            payload = ""
            for device in devices:
                wrapped_key_bytes, payload_bytes = self.__omemo.send_message(
                            jid=jid_to,
                            device=device,
                            message_bytes=body.encode("utf-8")
                )

                wrapped = base64.b64encode(wrapped_key_bytes).decode("utf-8")
                payload = base64.b64encode(payload_bytes).decode("utf-8")

                key_data_blob = json.dumps({
                    "k": wrapped,
                    "p": payload
                }).encode('utf-8')

                key_data = base64.b64encode(key_data_blob).decode('utf-8')

                xml_keys.add_child(
                    XmlElement(
                        "key", 
                        [XmlAttribute("rid", device)],
                        [XmlTextElement(key_data)]
                    )
                )

            encrypted_message = OmemoXml.send_message(
                        self.__ci.get_jid(),
                        jid_to,
                        self.__bundle.get_device_id(),
                        [xml_keys]
            )
        elif (devices is None):
            encrypted_message = self.__send_init_message(jid_to, body)

        if (encrypted_message):
            if (not final_message):
                final_message = message
            # Wrap encrypted message into message
            final_message.xml.add_child(encrypted_message.get_child_by_name("encrypted"))
            final_message.xml.remove_child_by_name("body")
            final_message.xml.add_child(encrypted_message.get_child_by_name("body"))

        return final_message if final_message else message 

    # Parse device information from IQ response
    def __parse_devices_response(self, iq):
        try:
            # Check if this is a devices response
            pubsub = iq.get_child_by_name("pubsub")
            if (not pubsub):
                return
                
            items = pubsub.get_child_by_name("items")
            if (not items or items.get_attribute_by_name("node").value != "urn:xmpp:omemo:2:devices"):
                return
                
            item = items.get_child_by_name("item")
            if (not item):
                return

            devices = item.get_child_by_name("devices")
            if (not devices):
                return
            
            contact_jid = iq.get_attribute_by_name("from").value.split("/")[0]
            if contact_jid not in self.__contact_bundles:
                self.__contact_bundles[contact_jid] = {}

            for device in devices.children:
                device_id = int(device.get_attribute_by_name("id").value)
                self.__contact_bundles[contact_jid][device_id] = {}
        except Exception as e:
            print(f"Error parsing devices: {e}")
        
    # Parse bundle information from IQ response
    def __parse_bundle_response(self, iq):
        try:
            # Check if this is a bundle response
            pubsub = iq.get_child_by_name("pubsub")
            if (not pubsub):
                return
                
            items = pubsub.get_child_by_name("items")
            if (not items or items.get_attribute_by_name("node").value != "urn:xmpp:omemo:2:bundles"):
                return
                
            item = items.get_child_by_name("item")
            if (not item):
                return
                
            bundle = item.get_child_by_name("bundle")
            if (not bundle):
                return
                
            # Extract bundle information
            device_id = int(item.get_attribute_by_name("id").value)
            contact_jid = iq.get_attribute_by_name("from").value.split("/")[0]
            
            bundle_data = {
                "spk": bundle.get_child_by_name("spk").children[0].to_string().strip(),
                "spks": bundle.get_child_by_name("spks").children[0].to_string().strip(), 
                "ik": bundle.get_child_by_name("ik").children[0].to_string().strip(),
                "opks": {}
            }
            
            prekeys_elem = bundle.get_child_by_name("prekeys")
            if prekeys_elem:
                for pk in prekeys_elem.children:
                    pk_id = pk.get_attribute_by_name("id").value
                    pk_data = pk.children[0].to_string()
                    bundle_data["opks"][pk_id] = pk_data
            
            # Store the bundle
            if contact_jid not in self.__contact_bundles:
                self.__contact_bundles[contact_jid] = {}
            self.__contact_bundles[contact_jid][device_id] = bundle_data
        except Exception as e:
            print(f"Error parsing bundle: {e}")


    def __send_init_message(self, jid_to: str, message: str):
        if (jid_to in self.__contact_bundles):
            # TODO: many devices
            device_to = list(self.__contact_bundles[jid_to].keys())[0]
            bundle_to = self.__contact_bundles[jid_to][device_to]
            
            # Choose random opk id
            opk_id = random.choice(list(bundle_to["opks"].keys())) 

            ek_pub, en_message = self.__omemo.create_init_message(
                    jid=jid_to,
                    device=device_to,
                    message_bytes=message.encode("utf-8"),
                    indentity_key=EdKeyPair.base64_to_public_key(bundle_to["ik"]),
                    signed_prekey=XKeyPair.base64_to_public_key(bundle_to["spk"]),
                    prekey_signature=base64.b64decode(bundle_to["spks"].encode("utf-8")),
                    onetime_prekey=XKeyPair.base64_to_public_key(bundle_to["opks"][opk_id])
            )
            
            key_data_blob = json.dumps({
                "ik": self.__bundle.get_indentity().get_base64_public_key(),
                "ek": XKeyPair.public_key_to_base64(ek_pub),
                "spk_id": "0",
                "opk_id": opk_id,
                "ct": base64.b64encode(en_message).decode("utf-8") 
            }).encode('utf-8')

            key_data = base64.b64encode(key_data_blob).decode('utf-8')

            xml_message = OmemoXml.send_init_message(
                    jid=self.__ci.get_jid(),
                    jid_to=jid_to,
                    device=self.__bundle.get_device_id(),
                    device_to=device_to,
                    key_data=key_data 
            )
            
            return xml_message

    def __receive_init_message(self, jid_from: str, device_from: int, wrapped: str):
        message = None
        if (jid_from in self.__contact_bundles):
            key_data_js = json.loads(base64.b64decode(wrapped).decode('utf-8'))

            en_message = base64.b64decode(key_data_js["ct"].encode("utf-8"))
            indentity_key = EdKeyPair.base64_to_public_key(key_data_js["ik"])
            ephemeral_key = XKeyPair.base64_to_public_key(key_data_js["ek"])
            spk_id = key_data_js["spk_id"]
            opk_id = key_data_js["opk_id"]

            de_message = self.__omemo.accept_init_message(
                    jid=jid_from,
                    device=device_from,
                    encrypted_message=en_message,
                    indentity_key=indentity_key,
                    ephemeral_key=ephemeral_key,
                    spk_id=spk_id,
                    opk_id=opk_id
            )

            message = de_message.decode("utf-8")

        return message

