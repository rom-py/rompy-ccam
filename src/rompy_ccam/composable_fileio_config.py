import sys
from pathlib import Path
from dataclasses import dataclass
from typing import (
    Literal,
)

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from rompy.core.config import BaseConfig, RompyBaseModel

from rompy_ccam.frozenset_utils import (
    frozenset_list_union,
    frozenset_format_as_file_list,
)
from rompy_ccam.pydantic import (
    fields_satisfying,
    field_is_type_with_tag,
    field_is_optional_type_with_tag,
    fields_with_type_satisfying,
    type_is_subclass,
    type_is_optional_subclass,
)


class _Input:
    pass


Input = _Input()


class _Output:
    pass


Output = _Output()


class FileInputConfig(RompyBaseModel):
    """A class which can list its input files."""

    @property
    def input_files(self) -> frozenset[Path]:
        return frozenset()


class FileInputConfigAuto(FileInputConfig, RompyBaseModel):
    """A class which automatically lists its input files by traversing its pydantic model."""

    @property
    def input_files(self) -> frozenset[Path]:
        """What files does this config expect to be present in the filesystem when it runs?"""
        return frozenset().union(
            # All fields of type Path marked as Input
            [
                getattr(self, field_name)
                for field_name in fields_satisfying(
                    self, field_is_type_with_tag(Path, Input)
                )
            ],
            # All fields of type Optional[Path] tagged as Input whose value is not None
            [
                field_value
                for field in fields_satisfying(
                    self, field_is_optional_type_with_tag(Path, Input)
                )
                if (field_value := getattr(self, field)) is not None
            ],
            # Input files of all fields which are a subclass of FileInputConfig
            frozenset_list_union(
                [
                    getattr(self, field).input_files
                    for field in fields_with_type_satisfying(
                        self, type_is_subclass(FileInputConfig)
                    )
                ]
            ),
            # Input files of all fields which are an Optional[subclass of FileInputConfig] and are not None
            frozenset_list_union(
                [
                    field_value.input_files
                    for field in fields_with_type_satisfying(
                        self, type_is_optional_subclass(FileInputConfig)
                    )
                    if (field_value := getattr(self, field)) is not None
                ]
            ),
        )


class FileOutputConfig(RompyBaseModel):
    """A class which can list its output files."""

    @property
    def output_files(self) -> frozenset[Path]:
        return frozenset()


class FileOutputConfigAuto(FileOutputConfig, RompyBaseModel):
    """A class which automatically lists its output files by traversing its pydantic model."""

    @property
    def output_files(self) -> frozenset[Path]:
        """What files does running this config produce?"""
        return frozenset().union(
            # All fields of type Path marked as Output
            [
                getattr(self, field_name)
                for field_name in fields_satisfying(
                    self, field_is_type_with_tag(Path, Output)
                )
            ],
            # All fields of type Optional[Path] tagged as Output whose value is not None
            [
                field_value
                for field in fields_satisfying(
                    self, field_is_optional_type_with_tag(Path, Output)
                )
                if (field_value := getattr(self, field)) is not None
            ],
            # Output files of all fields which are a subclass of FileOutputConfig
            frozenset_list_union(
                [
                    getattr(self, field).output_files
                    for field in fields_with_type_satisfying(
                        self, type_is_subclass(FileOutputConfig)
                    )
                ]
            ),
            # Output files of all fields which are an Optional[subclass of FileOutputConfig] and are not None
            frozenset_list_union(
                [
                    field_value.output_files
                    for field in fields_with_type_satisfying(
                        self, type_is_optional_subclass(FileOutputConfig)
                    )
                    if (field_value := getattr(self, field)) is not None
                ]
            ),
        )


class FileIOConfig(FileInputConfig, FileOutputConfig):
    """Inherit from this if your config class represents a process which takes input files and produces output files."""

    pass


class FileIOConfigAuto(FileInputConfigAuto, FileOutputConfigAuto):
    """Inherit from this to automatically find input and output files your config class consumes and produces."""

    pass


class NullConfig(FileIOConfig, BaseConfig):
    """Represents a process which does nothing; consumes no inputs and produces no outputs."""

    model_type: Literal["null"] = "null"

    def __repr__(self) -> str:
        return "NullConfig()"


NULL_CONFIG = NullConfig()


@dataclass(frozen=True)
class ComposedConfig(FileIOConfig, BaseConfig):
    """A config composed of two steps, `first` and `second`."""

    first: FileIOConfig
    second: FileIOConfig

    model_type: Literal["composed"] = "composed"

    def __init__(self, first: FileIOConfig, second: FileIOConfig) -> None:
        # super().__init__()
        object.__setattr__(self, "first", first)
        object.__setattr__(self, "second", second)
        object.__setattr__(self, "model_type", "composed")

        conflicting_output_files: frozenset[Path] = (
            self.first.output_files & self.second.output_files
        )
        if conflicting_output_files:
            raise ValueError(
                f"Different steps of workflow would create/overwrite these files: {frozenset_format_as_file_list(conflicting_output_files)}:\n***First workflow:***\n{str(self.first)}\n***Second workflow:***\n{str(self.second)}"
            )

    def before(self, next: Self) -> Self:
        if isinstance(self, NullConfig):
            return next
        if isinstance(next, NullConfig):
            return self
        return type(self)(self, next)

    def __add__(self, other: Self) -> Self:
        return self.before(other)

    def after(self, previous: Self) -> Self:
        if isinstance(self, NullConfig):
            return previous
        if isinstance(previous, NullConfig):
            return self
        return type(self)(previous, self)

    def __radd__(self, other: Self) -> Self:
        return self.after(other)

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
