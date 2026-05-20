from typing import Literal

from pydantic import Field

from .rompy_ccam import CCAMBaseConfig


class CCAMWorkflowSequence(CCAMBaseConfig):
    """A workflow which consists of a sequence of sub-workflows, e.g. to achieve high-resolution results over a small grid area by performing nested CCAM simulations."""

    model_type: Literal["ccam-nested-workflow"] = Field(
        default="ccam-nested-workflow",
        description="Model type discriminator",
    )

    workflows: list[CCAMBaseConfig] = []

    def __call__(self, *args, **kwargs) -> dict:
        for workflow in self.workflows:
            workflow()

    def bash_invocation(self) -> str:
        return "\n".join(workflow.bash_invocation() for workflow in self.workflows)
