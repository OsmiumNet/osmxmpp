import re

osmxmpp_id_regex = re.compile(r'^[A-Za-z0-9]+\.[A-Za-z0-9]+$')

xmpp_jid_regex = re.compile(r'^(?:([a-zA-Z0-9._%+-]+)@)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(?:/(.+))?$')
xmpp_resource_regex = re.compile(r'^[^\s/]+$')

class ValidationException(Exception):
    pass


class XmppValidation:
    """
    OsmXmpp validation methods
    """

    @staticmethod
    def validate_id(id:str):
        """
        Validates the extension/feature ID.

        Args:
            id (str): The ID to validate.
        
        Raises:
            ValidationException: If the ID is invalid.
        """

        if type(id) != str:
            raise ValidationException(f"ID '{id}' is not a string")
        
        if not osmxmpp_id_regex.match(id):
            raise ValidationException(f"Invalid ID '{id}'")

    @staticmethod
    def validate_jid(jid:str):
        """
        Validates the JID.

        Args:
            jid (str): The JID to validate.

        Raises:
            ValidationException: If the JID is invalid.
        """

        if type(jid) != str:
            raise ValidationException(f"JID '{jid}' is not a string")
        
        if not xmpp_jid_regex.match(jid):
            raise ValidationException(f"Invalid JID '{jid}'")

    @staticmethod
    def validate_resource(resource:str):
        """
        Validates the resource.

        Args:
            resource (str): The resource to validate.

        Raises:
            ValidationException: If the resource is invalid.
        """

        if type(resource) != str:
            raise ValidationException(f"Resource '{resource}' is not a string")

        if not xmpp_resource_regex.match(resource):
            raise ValidationException(f"Invalid resource '{resource}'")