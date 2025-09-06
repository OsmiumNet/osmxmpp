from osmxml import *

class _XmppMessageElement:
    def __init__(self, xml:XMLElement):
        self._xml = xml

    def get_attribute_by_index(self, index:int):
        return self._xml.get_attribute_by_index(index)
    
    def get_child_by_index(self, index:int):
        return _get_xmpp_message_element_or_text(self._xml.get_child_by_index(index))
    

    def __getattr__(self, name):
        if self._xml.get_attribute_by_name(name):
            return self._xml.get_attribute_by_name(name).value
        
        return _get_xmpp_message_element_or_text(self._xml.get_child_by_name(name))
    
    def __getitem__(self, index):
        return self.get_child_by_index(index)
    
    def __repr__(self):
        return f"<_XmppMessageElement {self._xml.to_string()}>"

def _get_xmpp_message_element_or_text(xml: XMLElement) -> _XmppMessageElement | str:
    if xml == None:
        return

    has_one_child = len(xml.children) == 1

    if has_one_child and hasattr(xml.children[0], "text"):
        return xml.children[0].text
    else:
        return _XmppMessageElement(xml)
        

class XmppMessage:
    """
    XMPP message implementation.
    """

    def __init__(self, xml: XMLElement=None):
        if xml:
            self._xml = xml
        else:
            self._xml = XMLElement("message")

    def get_attribute_by_index(self, index:int):
        return self._xml.get_attribute_by_index(index)
    
    def get_child_by_index(self, index:int):
        return _get_xmpp_message_element_or_text(self._xml.get_child_by_index(index))


    def __getattr__(self, name):
        if name == "from_jid":
            return self._xml.get_attribute_by_name("from").value
        
        if name == "to_jid":
            return self._xml.get_attribute_by_name("to").value
        
        if self._xml.get_attribute_by_name(name):
            return self._xml.get_attribute_by_name(name).value

        return _get_xmpp_message_element_or_text(self._xml.get_child_by_name(name))
    
    def __getitem__(self, index):
        return self.get_child_by_index(index)
    
    def __repr__(self):
        return f"<XmppMessage from='{self.from_jid}' to='{self.to_jid}' type='{self.type}'>"
