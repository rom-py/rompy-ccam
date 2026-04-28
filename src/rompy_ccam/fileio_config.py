from pathlib import Path
from rompy_ccam.pydantic import (
    fields_satisfying,
    field_is_type_with_tag,
    field_is_optional_type_with_tag,
    fields_with_type_satisfying,
    type_is_subclass,
    type_is_optional_subclass,
)

from rompy.core.config import RompyBaseModel

from rompy_ccam.frozenset_utils import (
    frozenset_list_union,
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
