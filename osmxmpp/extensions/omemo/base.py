import os
import base64
import json
import time
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
        self._bundle = bundle
        self.__omemo = Omemo(self._bundle, storage)

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
        self.__ci.send_xml(xml)

    def __on_ready(self):
        #xml = OmemoXml.publish_device(self.__ci.get_jid(False), self._bundle.get_device_id())
        #self.__ci.send_xml(xml)

        #xml = OmemoXml.publish_bundle_information(self.__ci.get_jid(False), self._bundle)
        #self.__ci.send_xml(xml)
        pass
        

    def __on_iq(self, iq):
        iq_id = iq.get_attribute_by_name("id")

        self._parse_bundle_response(iq)
        self._parse_devices_response(iq)

    def __hook_on_message(self, message: XmppMessage):
        final_message = None

        jid_from = message.from_jid.split("/")[0]
        if (message.encrypted):
            # TODO: check device 
            wrapped = message.encrypted.header.keys.key
            payload = message.encrypted.payload
            device_from = int(message.encrypted.header._xml.get_attribute_by_name("sid").value)

            devices = self.__omemo.get_device_list(jid_from)
            if (type(devices) == list):
                wrapped_bytes = base64.b64decode(wrapped.encode("utf-8"))
                payload_bytes = base64.b64decode(payload.encode("utf-8"))
                de_message = self.__omemo.receive_message(jid_from, device_from, wrapped_bytes, payload_bytes)

                final_massage = message
                final_massage.body = de_message.decode("utf-8")
            else:
                de_message = self._receive_init_message(jid_from, device_from, wrapped)

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
                wrapped_key, payload_bytes = self.__omemo.send_message(
                            jid=jid_to,
                            device=device,
                            message_bytes=body.encode("utf-8")
                )

                wrapped = base64.b64encode(wrapped_key).decode("utf-8")
                payload = base64.b64encode(payload_bytes).decode("utf-8")

                xml_keys.add_child(
                            XmlElement(
                                "key", 
                                [XmlAttribute("rid", device)],
                                [XmlTextElement(wrapped)])
                )

            encrypted_message = OmemoXml.send_message(
                        self.__ci.get_jid(),
                        jid_to,
                        self._bundle.get_device_id(),
                        [xml_keys],
                        payload
            )
        elif (devices is None):
            encrypted_message = self._send_init_message(jid_to, body)

        if (encrypted_message):
            if (not final_message):
                final_message = message
            # Wrap encrypted message into message
            final_message._xml.add_child(encrypted_message.get_child_by_name("encrypted"))
            final_message._xml.remove_child_by_name("body")
            final_message._xml.add_child(encrypted_message.get_child_by_name("body"))

        return final_message if final_message else message 

    # Parse device information from IQ response
    def _parse_devices_response(self, iq):
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

                xml = OmemoXml.fetch_bundles(self.__ci.get_jid(),  contact_jid, device_id)
                self.__ci.send_xml(xml)

        except Exception as e:
            print(f"Error parsing devices: {e}")
        
    # Parse bundle information from IQ response
    def _parse_bundle_response(self, iq):
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


    def _send_init_message(self, jid_to: str, message: str):
        if (jid_to in self.__contact_bundles):
            # TODO: many devices
            device_to = list(self.__contact_bundles[jid_to].keys())[0]
            bundle_to = self.__contact_bundles[jid_to][device_to]
            # TODO: random opk id
            opk_id = "0" 
            ek_pub, en_message = self.__omemo.create_init_message(
                    jid=jid_to,
                    device=device_to,
                    message_bytes=message.encode("utf-8"),
                    indentity_key=EdKeyPair.base64_to_public_key(bundle_to["ik"]),
                    signed_prekey=XKeyPair.base64_to_public_key(bundle_to["spk"]),
                    prekey_signature=base64.b64decode(bundle_to["spks"].encode("utf-8")),
                    onetime_prekey=XKeyPair.base64_to_public_key(bundle_to["opks"][opk_id])
            )
            
            wrapped_blob = json.dumps({
                "ik": self._bundle.get_indentity().get_base64_public_key(),
                "ek": XKeyPair.public_key_to_base64(ek_pub),
                "spk_id": "0",
                "opk_id": opk_id,
                "ct": base64.b64encode(en_message).decode("utf-8") 
            }).encode('utf-8')

            wrapped = base64.b64encode(wrapped_blob).decode('utf-8')

            xml_message = OmemoXml.send_init_message(
                    jid=self.__ci.get_jid(),
                    jid_to=jid_to,
                    device=self._bundle.get_device_id(),
                    device_to=device_to,
                    wrapped=wrapped 
            )
            
            return xml_message

    def _receive_init_message(self, jid_from: str, device_from: int, wrapped: str):
        message = None
        if (jid_from in self.__contact_bundles):
            wrapped_js = json.loads(base64.b64decode(wrapped).decode('utf-8'))

            en_message = base64.b64decode(wrapped_js["ct"].encode("utf-8"))
            indentity_key = EdKeyPair.base64_to_public_key(wrapped_js["ik"])
            ephemeral_key = XKeyPair.base64_to_public_key(wrapped_js["ek"])
            spk_id = wrapped_js["spk_id"]
            opk_id = wrapped_js["opk_id"]

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

