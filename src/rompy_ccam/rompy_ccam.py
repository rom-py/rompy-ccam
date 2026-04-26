"""Main module."""

from pathlib import Path
from typing import Optional

from pydantic import ConfigDict

from rompy.core.config import BaseConfig

from rompy_ccam.composable_fileio_config import FileIOConfigAuto
from rompy_ccam.frozenset_utils import frozenset_format_as_file_list


class CCAMConfig(FileIOConfigAuto):
    """A config class for rompy_ccam."""

    pass


class CCAMBaseConfig(CCAMConfig, BaseConfig):
    """Base configuration for all CCAM models."""

    template: Optional[str] = None
    checkout: Optional[str] = None

    model_config = ConfigDict(extra="forbid")

    workflow_step_description: Optional[str] = None

    def render(self, context: dict, output_dir: Path | str):
        """Override parent class render(), as we're not using templates."""
        pass

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
