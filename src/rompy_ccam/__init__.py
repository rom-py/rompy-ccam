"""Top-level package for rompy-ccam."""

from .fileio_config import Input, Output
from .types import Flag
from .rompy_ccam import CCAMConfig, CCAMBaseConfig, NULL_CONFIG
from .namelists import CCAMNamelistConfig

__author__ = """Rompy Developers"""
__email__ = "developers@rompy.com"
__version__ = "0.1.0"

__all__ = [
    "Input",
    "Output",
    "NULL_CONFIG",
    "Flag",
    "CCAMConfig",
    "CCAMBaseConfig",
    "CCAMNamelistConfig",
]
