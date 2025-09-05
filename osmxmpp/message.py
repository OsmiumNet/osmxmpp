from osmxml import *

class _XMPPMessageElement:
    def __init__(self, xml:XMLElement):
        self._xml = xml

    def set_attrubute(self, name:str, value:str):
        self._xml.add_attribute(XMLAttribute(name, value))

    def get_attribute_by_index(self, index:int):
        return self._xml.get_attribute_by_index(index)

    def add_child(self, child:XMLElement):
        self._xml.add_child(child)
    
    def get_child_by_index(self, index:int):
        return _get_xmpp_message_element_or_text(self._xml.get_child_by_index(index))
    

    def __getattr__(self, name):
        if self._xml.get_attribute_by_name(name):
            return self._xml.get_attribute_by_name(name).value.value
        
        return _get_xmpp_message_element_or_text(self._xml.get_child_by_name(name))
        
        return None
    
    def __getitem__(self, index):
        return self.get_child_by_index(index)
    
    def __repr__(self):
        return f"<_XMPPMessageElement {self._xml.to_string()}>"

def _get_xmpp_message_element_or_text(xml: XMLElement) -> _XMPPMessageElement | str:
    if xml == None:
        return

    has_one_child = len(xml.children) == 1

    if has_one_child and hasattr(xml.children[0], "text"):
        return xml.children[0].text
    else:
        return _XMPPMessageElement(xml)
        

class XMPPMessage:
    """
    XMPP message implementation.
    """

    def __init__(self, xml: XMLElement=None):
        if xml:
            self._xml = xml
        else:
            self._xml = XMLElement("message")
    
    def set_attrubute(self, name:str, value:str):
        self._xml.add_attribute(XMLAttribute(name, value))

    def get_attribute_by_index(self, index:int):
        return self._xml.get_attribute_by_index(index)

    def add_child(self, child:XMLElement):
        self._xml.add_child(child)
    
    def get_child_by_index(self, index:int):
        return _get_xmpp_message_element_or_text(self._xml.get_child_by_index(index))


    def __getattr__(self, name):
        if name == "from_jid":
            return self._xml.get_attribute_by_name("from").value
        
        if name == "to_jid":
            return self._xml.get_attribute_by_name("to").value
        
        if self._xml.get_attribute_by_name(name):
            return self._xml.get_attribute_by_name(name).value

        if self._xml.get_child_by_name(name):

            return _get_xmpp_message_element_or_text(self._xml.get_child_by_name(name))

        return None
    
    def __getitem__(self, index):
        return self.get_child_by_index(index)
    
    def __repr__(self):
        return f"<XMPPMessage from='{self.from_jid}' to='{self.to_jid}' type='{self.type}'>"
