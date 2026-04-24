from pydantic import ConfigDict
from enum import IntEnum
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from rompy.core.config import BaseConfig

class CCAMBaseConfig(BaseConfig):
    """Base configuration for all CCAM models."""

    model_config = ConfigDict(extra="forbid")


    def before(self, next: Self) -> Self:
        if isinstance(self, NullConfig):
            return next
        if isinstance(next, NullConfig):
            return self
        return ComposedConfig(self, next)

    def __add__(self, other: Self) -> Self:
        return self.before(other)

    def after(self, previous: Self) -> Self:
        if isinstance(self, NullConfig):
            return previous
        if isinstance(previous, NullConfig):
            return self
        return ComposedConfig(previous, self)

    def __radd__(self, other: Self) -> Self:
        return self.after(other)


class NullConfig(CCAMBaseConfig):
    """Represents a process which does nothing; consumes no inputs and produces no outputs."""

    def __repr__(self) -> str:
        return "NullConfig()"


NULL_CONFIG = NullConfig()


@dataclass(frozen=True)
class ComposedConfig(CCAMBaseConfig):
    first: CCAMBaseConfig
    second: CCAMBaseConfig

    def __repr__(self) -> str:
        return f"ComposedConfig(first={self.first!r}, second={self.second!r})"

    def __str__(self) -> str:
        return f"{str(self.first)}\n{str(self.second)}"

    def __call__(self, *args, **kwargs):
        self.first.__call__(args, kwargs)
        self.second.__call__(args, kwargs)

class Flag(IntEnum):
    """General-purpose flag type for use with Fortran namelists which regularly use an int field with 0 meaning off and 1 meaning on. Differs from Fortran 'logical' (i.e. boolean), which has .false. and .true. values."""
    OFF = 0
    ON = 1
