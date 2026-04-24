from pathlib import Path

from pydantic import Field

from rompy_ccam.types import CCAMBaseConfig


class CasafieldConfig(CCAMBaseConfig):
    """Configuration options to be given to the casafield executable.

    CASAFIELD is used to create input files for the CASA-CNP carbon cycle model available with CCAM. In addition to simulating the terrestrial carbon cycle, this option also allows the CABLE land-surface scheme to run with a prognostic Leaf Area Index (LAI) and the Populations-Order-Physiology (POP) model.
    """

    topofile: Path = Field(
        description="Input topography file created by terread.",
    )

    input: Path = Field(
        description="The casaNP_gridinfo_1dx1d.nc file for carbon cycle emissions.",
    )

    output: Path = Field(
        description="Output carbon cycle emissions on the cubic grid (to be read by CCAM).",
    )
