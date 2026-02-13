from pydantic import ConfigDict
from enum import IntEnum

from rompy.core.config import BaseConfig

class CCAMBaseConfig(BaseConfig):
    """Base configuration for all CCAM models."""

    model_config = ConfigDict(extra="forbid")

class Flag(IntEnum):
    """General-purpose flag type for use with Fortran namelists which regularly use an int field with 0 meaning off and 1 meaning on. Differs from Fortran 'logical' (i.e. boolean), which has .false. and .true. values."""
    OFF = 0
    ON = 1
