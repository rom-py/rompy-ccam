from pathlib import Path
from typing import Union, Callable, Any, Tuple
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


def find_paths_with_tag(
    tree: RompyBaseModel,
    tag: Any,
    cls: Union[type, Tuple[Union[type, Tuple[Any, ...]], ...]],
    get_subtree_paths: Callable[[Any], frozenset[Path]],
) -> frozenset[Path]:
    return frozenset().union(
        # All fields of type Path marked as `tag`
        [
            getattr(tree, field_name)
            for field_name in fields_satisfying(tree, field_is_type_with_tag(Path, tag))
        ],
        # All fields of type Optional[Path] tagged as `tag` whose value is not None
        [
            field_value
            for field in fields_satisfying(
                tree, field_is_optional_type_with_tag(Path, tag)
            )
            if (field_value := getattr(tree, field)) is not None
        ],
        # Input files of all fields which are a subclass of `cls`
        frozenset_list_union(
            [
                get_subtree_paths(getattr(tree, field))
                for field in fields_with_type_satisfying(tree, type_is_subclass(cls))
            ]
        ),
        # Input files of all fields which are an Optional[subclass of `cls`] and are not None
        frozenset_list_union(
            [
                get_subtree_paths(field_value)
                for field in fields_with_type_satisfying(
                    tree, type_is_optional_subclass(cls)
                )
                if (field_value := getattr(tree, field)) is not None
            ]
        ),
    )


class FileInputConfigAuto(FileInputConfig):
    """A class which automatically lists its input files by traversing its pydantic model."""

    @property
    def input_files(self) -> frozenset[Path]:
        """What files does this config expect to be present in the filesystem when it runs?"""
        return find_paths_with_tag(
            self, Input, FileInputConfig, lambda fi: fi.input_files
        )


class FileOutputConfig(RompyBaseModel):
    """A class which can list its output files."""

    @property
    def output_files(self) -> frozenset[Path]:
        return frozenset()


class FileOutputConfigAuto(FileOutputConfig):
    """A class which automatically lists its output files by traversing its pydantic model."""

    @property
    def output_files(self) -> frozenset[Path]:
        """What files does running this config produce?"""
        return find_paths_with_tag(
            self, Output, FileOutputConfig, lambda fi: fi.output_files
        )


class FileIOConfig(FileInputConfig, FileOutputConfig):
    """Inherit from this if your config class represents a process which takes input files and produces output files."""

    pass


class FileIOConfigAuto(FileInputConfigAuto, FileOutputConfigAuto):
    """Inherit from this to automatically find input and output files your config class consumes and produces."""

    pass
