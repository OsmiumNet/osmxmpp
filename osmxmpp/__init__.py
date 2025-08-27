__version__ = "0.1.0"
__author__ = "osmiumnet"

from .client import XMPPClient
from .feature import XMPPFeature

__all__ = [
    "XMPPClient",
    "XMPPFeature",
]