"""Main module."""

import sys
from pathlib import Path
from typing import Any, Optional, Literal

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from pydantic import ConfigDict, Field

from rompy.core.config import BaseConfig

from .fileio_config import FileIOConfigAuto
from .frozenset_utils import frozenset_format_as_file_list


class CCAMRootConfig(FileIOConfigAuto):
    """A config class for rompy_ccam."""

    pass


HERE = Path(__file__).parent


class CCAMBaseConfig(CCAMRootConfig, BaseConfig):
    """Base configuration for all CCAM models."""

    template: str = Field(
        default=str(HERE / "templates" / "base"),
        description="The model config template directory",
    )

    checkout: Optional[str] = None

    model_config = ConfigDict(extra="forbid")

    workflow_step_description: Optional[str] = None

    def before(self, next: Self) -> Self:
        if isinstance(self, NullConfig):
            return next
        if isinstance(next, NullConfig):
            return self
        return ComposedConfig(first=self, second=next)

    def __add__(self, other: Self) -> Self:
        return self.before(other)

    def after(self, previous: Self) -> Self:
        if isinstance(self, NullConfig):
            return previous
        if isinstance(previous, NullConfig):
            return self
        return ComposedConfig(first=previous, second=self)

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


class CCAMExeConfig(CCAMBaseConfig):
    """Configuration for one of the CCAM executables."""

    def bash_prettify_invocation(self, inv: str) -> str:
        return f"""# {self.workflow_step_description}
{inv}
"""

    def bash_invocation(self) -> str:
        """Return a command to add to a bash script to invoke this CCAM executable with the given configuration."""
        return f"TODO: implement bash_invocation for {type(self).__name__}"


class NullConfig(CCAMBaseConfig):
    """Represents a process which does nothing; consumes no inputs and produces no outputs."""

    model_type: Literal["null"] = "null"

    def __repr__(self) -> str:
        return "NullConfig()"


NULL_CONFIG = NullConfig()


class ComposedConfig(CCAMExeConfig):
    """A config composed of two steps, `first` and `second`."""

    first: CCAMExeConfig
    second: CCAMExeConfig

    model_type: Literal["composed"] = "composed"

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

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

    def generate(self) -> str:
        return self.first.generate() + self.second.generate()

    def __repr__(self) -> str:
        return f"ComposedConfig(first={self.first!r}, second={self.second!r})"

    def __str__(self) -> str:
        return f"{str(self.first)}\n{str(self.second)}"

    def bash_invocation(self) -> str:
        return self.first.bash_invocation() + "\n" + self.second.bash_invocation()

    def __call__(self, *args, **kwargs):
        self.first.__call__(args, kwargs)
        self.second.__call__(args, kwargs)
