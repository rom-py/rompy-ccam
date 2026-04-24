import sys
from dataclasses import dataclass
from pathlib import Path
from enum import IntEnum
from typing import (
    Any,
    Optional,
    get_origin,
    get_args,
    Union,
    Callable,
    Tuple,
    Annotated,
)

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
from functools import reduce
from operator import or_


import f90nml
from pydantic import ConfigDict, Field
from pydantic.fields import FieldInfo

from rompy.core.config import BaseConfig


def type_is_optional(t: type[Any]) -> Callable[[type[Any]], bool]:
    """Return a predicate which checks whether a type is Optional[t]."""
    return lambda f: get_origin(f) is Union and get_args(f) == (t, type(None))


def type_is_optional_satisfying(
    p: Callable[[type[Any]], bool],
) -> Callable[[type[Any]], bool]:
    return (
        lambda f: get_origin(f) is Union
        and (len(args := get_args(f)) == 2)
        and (args[1] == type(None))
        and p(args[0])
    )


def type_is_subclass(
    superclass: Union[type, Tuple[Union[type, Tuple[Any, ...]], ...]],
) -> Callable[[type[Any]], bool]:
    return lambda f: isinstance(f, type) and issubclass(f, superclass)


def type_is_optional_subclass(
    superclass: Union[type, Tuple[Union[type, Tuple[Any, ...]], ...]],
) -> Callable[[type[Any]], bool]:
    return type_is_optional_satisfying(type_is_subclass(superclass))


def field_type_satisfies(p: Callable[[type[Any]], bool]) -> Callable[[FieldInfo], bool]:
    return lambda f: f.annotation is not None and p(f.annotation)


def field_type_is(t: type[Any]) -> Callable[[FieldInfo], bool]:
    return field_type_satisfies(lambda f: f is t)


def field_has_tag(tag: Any) -> Callable[[FieldInfo], bool]:
    return lambda f: tag in f.metadata


def field_is_type_with_tag(typ: type[Any], tag: Any) -> Callable[[FieldInfo], bool]:
    return lambda f: field_type_is(typ)(f) and field_has_tag(tag)(f)


def field_is_optional_type_with_tag(
    typ: type[Any], tag: Any
) -> Callable[[FieldInfo], bool]:
    return lambda f: field_type_satisfies(type_is_optional(typ))(f) and field_has_tag(
        tag
    )(f)


def frozenset_list_union(lst: list[frozenset[Any]]) -> frozenset[Any]:
    return reduce(or_, lst, frozenset())


def frozenset_format_as_file_list(s: frozenset[Path]) -> str:
    return "nothing" if not s else ", ".join(str(p) for p in sorted(s, key=str))


class CCAMBaseConfig(BaseConfig):
    """Base configuration for all CCAM models."""

    model_config = ConfigDict(extra="forbid")

    workflow_step_description: Optional[str] = None

    @classmethod
    def fields_satisfying(cls, p: Callable[[FieldInfo], bool]) -> list[str]:
        """Return the names of fields which satisfy this predicate on their info."""
        return [
            field_name
            for field_name, model_field in cls.model_fields.items()
            if p(model_field)
        ]

    @classmethod
    def fields_with_type_satisfying(cls, p: Callable[[type[Any]], bool]) -> list[str]:
        """Return the names of fields which satisfy this predicate on their annotated type."""
        return cls.fields_satisfying(field_type_satisfies(p))

    @classmethod
    def fields_of_type(cls, t: type[Any]) -> list[str]:
        """
        Return the names of fields in this model of type t.
        Note that this won't work for more complex types such as Optional[Path]; for that, use fields_satisfying(type_is_optional(Path)).
        """
        return cls.fields_with_type_satisfying(lambda f: f is t)

    @property
    def input_files(self) -> frozenset[Path]:
        """What files does this config expect to be present in the filesystem when it runs?"""
        return frozenset().union(
            # All fields of type Path marked as Input
            [
                getattr(self, field_name)
                for field_name in self.fields_satisfying(
                    field_is_type_with_tag(Path, Input)
                )
            ],
            # All fields of type Optional[Path] tagged as Input whose value is not None
            [
                field_value
                for field in self.fields_satisfying(
                    field_is_optional_type_with_tag(Path, Input)
                )
                if (field_value := getattr(self, field)) is not None
            ],
            # Input files of all fields which are a subclass of CCAMBaseConfig
            frozenset_list_union(
                [
                    getattr(self, field).input_files
                    for field in self.fields_with_type_satisfying(
                        type_is_subclass(CCAMBaseConfig)
                    )
                ]
            ),
            # Input files of all fields which are an Optional[subclass of CCAMBaseConfig] and are not None
            frozenset_list_union(
                [
                    field_value.input_files
                    for field in self.fields_with_type_satisfying(
                        type_is_optional_subclass(CCAMBaseConfig)
                    )
                    if (field_value := getattr(self, field)) is not None
                ]
            ),
        )

    @property
    def output_files(self) -> frozenset[Path]:
        """What files does running this config produce?"""
        return frozenset().union(
            # All fields of type Path marked as Output
            [
                getattr(self, field_name)
                for field_name in self.fields_satisfying(
                    field_is_type_with_tag(Path, Output)
                )
            ],
            # All fields of type Optional[Path] tagged as Output whose value is not None
            [
                field_value
                for field in self.fields_satisfying(
                    field_is_optional_type_with_tag(Path, Output)
                )
                if (field_value := getattr(self, field)) is not None
            ],
            # Output files of all fields which are a subclass of CCAMBaseConfig
            frozenset_list_union(
                [
                    getattr(self, field).output_files
                    for field in self.fields_with_type_satisfying(
                        type_is_subclass(CCAMBaseConfig)
                    )
                ]
            ),
            # Output files of all fields which are an Optional[subclass of CCAMBaseConfig] and are not None
            frozenset_list_union(
                [
                    field_value.output_files
                    for field in self.fields_with_type_satisfying(
                        type_is_optional_subclass(CCAMBaseConfig)
                    )
                    if (field_value := getattr(self, field)) is not None
                ]
            ),
        )

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

    def __str__(self) -> str:
        return (
            f"CCAM workflow step: {type(self).__name__}"
            + (
                f"<{self.workflow_step_description}>"
                if self.workflow_step_description is not None
                else ""
            )
            + f" (consumes {frozenset_format_as_file_list(self.input_files)}; produces {frozenset_format_as_file_list(self.output_files)})"
        )


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


class _Input:
    pass


Input = _Input()


class _Output:
    pass


Output = _Output()


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

    def __post_init__(self) -> None:
        conflicting_output_files: frozenset[Path] = (
            self.first.output_files & self.second.output_files
        )
        if conflicting_output_files:
            raise ValueError(
                f"Different steps of workflow would create/overwrite these files: {frozenset_format_as_file_list(conflicting_output_files)}:\n***First workflow:***\n{str(self.first)}\n***Second workflow:***\n{str(self.second)}"
            )

    @property
    def input_files(self) -> frozenset[Path]:
        # Return the first config's input files, plus any of the second config's input
        # files which are *not* produced by the first config.
        return self.first.input_files | (
            self.second.input_files - self.first.output_files
        )

    @property
    def output_files(self) -> frozenset[Path]:
        # Return the union of the two sets of outputs
        return self.first.output_files | self.second.output_files

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
