__version__ = "0.1.0"
__author__ = "osmiumnet"

from .permission import XMPPPermission

from .ci import XMPPCI
from .client import XMPPClient

from .features.abc import XMPPFeature
from .features.tls_feature import TLSFeature
from .features.sasl_feature import SASLFeature, PLAINMechanism
from .features.bind import BindFeature

__all__ = [
    "XMPPClient",
    "XMPPCI",

    "XMPPPermission",

    "XMPPFeature",

    "TLSFeature",

    "SASLFeature",
    "PLAINMechanism",

    "BindFeature",
]