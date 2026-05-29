from typing import Literal, Optional

from pydantic import Field

from .rompy_ccam import CCAMBaseConfig

from .ccam.globpea import GlobpeaConfig
from .ccam.terread import TerreadConfig
from .ccam.igbpveg import IgbpvegConfig
from .ccam.cdfvidar import CdfvidarConfig
from .ccam.pcc2hist import Pcc2HistConfig


class CCAMDefaultWorkflow(CCAMBaseConfig):
    """A fixed sequence of CCAM execution; a typical use of CCAM."""

    model_type: Literal["ccam-default-workflow"] = Field(
        default="ccam-default-workflow",
        description="Model type discriminator",
    )

    terread: TerreadConfig = TerreadConfig()
    igbpveg: IgbpvegConfig = IgbpvegConfig()
    cdfvidar: Optional[CdfvidarConfig]
    globpea: GlobpeaConfig
    pcc2hist: Optional[Pcc2HistConfig]

    def __call__(self, *args, **kwargs) -> dict:
        self.terread()
        self.igbpveg()
        if self.cdfvidar is not None:
            self.cdfvidar()
        self.globpea()
        if self.pcc2hist is not None:
            self.pcc2hist()

    def bash_invocation(self) -> str:
        r = self.terread.bash_invocation()
        r += "\n" + self.igbpveg.bash_invocation()
        if self.cdfvidar is not None:
            r += "\n" + self.cdfvidar.bash_invocation()
        r += "\n" + self.globpea.bash_invocation()
        if self.pcc2hist is not None:
            r += "\n" + self.pcc2hist.bash_invocation()

        return r
