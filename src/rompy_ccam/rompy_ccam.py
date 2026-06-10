"""Main module."""

from pathlib import Path
from typing import Optional

from pydantic import ConfigDict, Field

from rompy.core.config import BaseConfig

from .fileio_config import FileIOConfigAuto
from .frozenset_utils import frozenset_format_as_file_list


class CCAMRootConfig(FileIOConfigAuto):
    """A config class for rompy_ccam. Automatically traverses itself and its children to find input and output files."""

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

    def executable_steps(self) -> list["CCAMExeConfig"]:
        """List all the CCAMExeConfigs that this class calls directly."""
        return []

    def bash_prettify_invocation(self, inv: str) -> str:
        return f"""# {self.workflow_step_description}
{inv}
"""

    def bash_invocation(self) -> str:
        """Return a command to add to a bash script to invoke this class's list of executable steps."""
        return "\n".join(step.bash_invocation() for step in self.executable_steps())

    def __call__(
        self, runtime
    ) -> dict:  # runtime is a ModelRun, which can't be imported due to circularity
        for step in self.executable_steps():
            step(runtime)

    def __str__(self) -> str:
        steps = self.executable_steps()
        step_summaries = "\n           ".join([str(step) for step in steps])
        return (
            f"CCAM workflow step: {type(self).__name__}"
            + (
                f"<{self.workflow_step_description}>"
                if self.workflow_step_description is not None
                else ""
            )
            + f"\n    (consumes {frozenset_format_as_file_list(self.input_files)})"
            + f"\n    (produces {frozenset_format_as_file_list(self.output_files)})"
            + (f"\n    (calls {step_summaries})" if step_summaries != "" else "")
        )


class CCAMExeConfig(CCAMBaseConfig):
    """Configuration for one of the CCAM executables."""

    def bash_invocation(self) -> str:
        """Return a command to add to a bash script to invoke this CCAM executable with the given configuration."""
        raise ValueError(f"TODO: implement bash_invocation for {type(self).__name__}")
