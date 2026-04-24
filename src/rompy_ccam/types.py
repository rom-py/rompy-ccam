from pydantic import ConfigDict
from enum import IntEnum
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
import f90nml

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


def nml_prepare_dict(d: dict) -> dict:
    """
    Prepare a pydantic model_dump() for export to .nml.

    This will recursively convert any Paths to strings, and remove any fields whose optional value is None.

    This will return a new dict, with the original being unchanged.
    """
    n: dict[Any, Any] = {}
    for key, value in d.items():
        if isinstance(value, dict):
            # Recurse into this nested dict
            n[key] = nml_prepare_dict(value)
        elif isinstance(value, Path):
            # Convert this Path into a string
            n[key] = str(value)
        elif value is not None:
            # Add this value to the new dict
            n[key] = value
    return n

class NMLConfig(CCAMBaseConfig):
    """A config that is intended to be exported as a namelist (.nml) file."""

    nml_path: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Optional path of the namelist (.nml) file to create.",
        ),
        Output,
    ]

    def write_nml_file(self, force=False, sort=False):
        if self.nml_path is None:
            raise ValueError("nml_path must be defined before calling write_nml_file()")

        dump = self.model_dump(
            mode="json",  # the output will only contain JSON serializable types (e.g. convert Path to string)
            exclude={
                "nml_path",
                "model_type",
                "checkout",
                "template",
            },  # Don't include our own nml_path field or pydantic fields that don't belong in the .nml
            by_alias=True,  # Use any serialization_aliases set on fields within the model
            exclude_none=True,  # Exclude field whose value is None
            # TODO: exclude empty list values as well somehow
        )
        nml = dump
        # nml = nml_prepare_dict(dump)
        f90nml.write(nml, self.nml_path, force=force, sort=sort),

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
