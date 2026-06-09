from typing import Literal, Optional

from pydantic import Field

from .rompy_ccam import CCAMBaseConfig, CCAMExeConfig

from .ccam.globpea import GlobpeaConfig
from .ccam.terread import TerreadConfig
from .ccam.igbpveg import IgbpvegConfig
from .ccam.cdfvidar import CdfvidarConfig
from .ccam.aeroemiss import AeroemissConfig
from .ccam.ocnbath import OcnbathConfig
from .ccam.pcc2hist import Pcc2HistConfig
from .ccam.casafield import CasafieldConfig


class CCAMWorkflow(CCAMBaseConfig):
    """A fixed sequence of CCAM execution; a typical use of CCAM."""

    model_type: Literal["ccam-default-workflow"] = Field(
        default="ccam-default-workflow",
        description="Model type discriminator",
    )

    terread: TerreadConfig = Field(
        default_factory=TerreadConfig,
        description="First, terread creates a 'topout' file which is basically the topograph. This defines the user grid based on centre lat/lon, grid size and resolution.",
    )

    igbpveg: IgbpvegConfig = Field(
        default_factory=IgbpvegConfig,
        description="igbpveg creates a vegetation map, reading terread's 'topout' as input.",
    )

    cdfvidar: Optional[CdfvidarConfig] = Field(
        default=None,
        description="cdfvidar creates initial conditions, reading 'topout' as input. This is required on the first pass, but can be skipped when downscaling (nesting).",
    )

    aeroemiss: Optional[AeroemissConfig] = Field(
        default=None,
        description="Create aerosol emissions for CCAM. Be sure to set globpea's aerosol input file (globpea.input.datafile.so4tfile) to aeroemiss's output file (aeroemiss.output), etc.",
    )

    ocnbath: Optional[OcnbathConfig] = Field(
        default=None,
        description="Calculate ocean/lake bathymetry and also determine river routing. Be sure to set globpea's input bathymetry file (globpea.input.datafile.bathfile) to ocnbath's output file (ocnbath.input.ocnml.bathout), etc.",
    )

    casafield: Optional[CasafieldConfig] = Field(
        default=None,
        description="Create input files for the CASA-CNP carbon cycle model. Be sure to set globpea's input carbon cycle file (globpea.input.datafile.casafile) to casafield's output (casafield.output), etc.",
    )

    # globpea uses all the topography, initial conditions, vegetation etc. to run the simulation.
    globpea: GlobpeaConfig

    # pcc2hist post-processes the output from globpea, usually converting back into a lat/lon grid.
    # pcc2hist may be run multiple times, depending on what output is required.
    pcc2hists: list[Pcc2HistConfig]

    def executable_steps(self) -> list[CCAMExeConfig]:
        """List all the CCAMExeConfigs that this class calls directly."""
        return [
            step
            for step in (
                [
                    self.terread,
                    self.igbpveg,
                    self.cdfvidar,
                    self.aeroemiss,
                    self.ocnbath,
                    self.casafield,
                    self.globpea,
                ]
                + self.pcc2hists
            )
            if step is not None
        ]


class CCAMInitialWorkflow(CCAMWorkflow):
    """A CCAM initial, or top-level workflow."""

    pass


class CCAMNestedWorkflow(CCAMWorkflow):
    """A CCAM nested, or downscaled workflow."""

    pass
