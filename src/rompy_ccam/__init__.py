"""Top-level package for rompy-ccam."""

from .config import CCAMConfig, DEFAULT_CCAM_INSTALL
from .fileio_config import Input, Output
from .types import Flag
from .rompy_ccam import CCAMRootConfig, CCAMBaseConfig, CCAMExeConfig, NULL_CONFIG
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
    "DEFAULT_CCAM_INSTALL" "CCAMRootConfig",
    "CCAMBaseConfig",
    "CCAMExeConfig",
    "CCAMNamelistConfig",
]
