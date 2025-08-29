from osmxml import *

class _XMPPMessageElement:
    def __init__(self, xml:XMLElement):
        self._xml = xml
    
    def __getattr__(self, name):
        if self._xml.get_attribute_by_name(name):
            return self._xml.get_attribute_by_name(name).value.value
        
        return _getXMPPMessageElementOrText(self._xml.get_child_by_name(name))
        
        return None
    
    def __getitem__(self, index):
        return _getXMPPMessageElementOrText(self._xml.children[index])

def _getXMPPMessageElementOrText(xml:XMLElement) -> _XMPPMessageElement | str:
    hasOneChild = len(xml.children) == 1

    if hasOneChild and hasattr(xml.children[0], "text"):
        return xml.children[0].text
    else:
        return _XMPPMessageElement(xml)
        

class XMPPMessage:
    """
    XMPP message implementation.
    """

    def __init__(self, xml:XMLElement=None):
        if xml:
            self._xml = xml
        else:
            self._xml = XMLElement("message")

    def __getattr__(self, name):
        if name == "from_jid":
            return self._xml.get_attribute_by_name("from").value
        
        if name == "to_jid":
            return self._xml.get_attribute_by_name("to").value
        
        if self._xml.get_attribute_by_name(name):
            return self._xml.get_attribute_by_name(name).value

        if self._xml.get_child_by_name(name):

            return _getXMPPMessageElementOrText(self._xml.get_child_by_name(name))

        return None
    
    def __repr__(self):
        return f"<XMPPMessage from='{self.from_jid}' to='{self.to_jid}' type='{self.type}'>"