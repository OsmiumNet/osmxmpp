__version__ = "0.1.0"
__author__ = "osmiumnet"

from .permission import XMPPPermission

from .message import XMPPMessage

from .ci import XMPPCI
from .client import XMPPClient

from .features.abc import XMPPFeature
from .features.tls import TLSFeature
from .features.sasl import SASLException, SASLMechanism, SASLFeature, PLAINMechanism
from .features.bind import BindFeature

__all__ = [
    "XMPPMessage",

    "XMPPPermission",

    "XMPPClient",
    "XMPPCI",

    "XMPPFeature",

    "TLSFeature",

    "SASLException",
    "SASLMechanism",
    "SASLFeature",
    "PLAINMechanism",

    "BindFeature",
]