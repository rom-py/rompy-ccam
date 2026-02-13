from pathlib import Path
from typing import Optional

from pydantic import Field

from rompy_ccam.types import CCAMBaseConfig

class AeroemissConfigAero(CCAMBaseConfig):
    """&aero section of AEROEMISS config namelist."""

    # TODO: set correct data types, defaults etc.
    month: Optional[int] = Field(
        default=None,
        description="Month of the year to process aerosol emissions (1-12).",
    )
    topofile: Optional[int] = Field(
        default=None,
        description="Topography file (from TERREAD) used to configure the CCAM grid.",
    )
    so2_anth: Optional[int] = Field(
        default=None,
        description="Input data file for anthropogenic SO2 emissions.",
    )
    so2_ship: Optional[int] = Field(
        default=None,
        description="Input data file for ship SO2 emissions.",
    )
    so2_biom: Optional[int] = Field(
        default=None,
        description="Input data file for biomass burning SO2 emissions.",
    )
    bc_anth: Optional[int] = Field(
        default=None,
        description="Input data file for anthropogenic black carbon emissions.",
    )
    bc_ship: Optional[int] = Field(
        default=None,
        description="Input data file for ship black carbon emissions.",
    )
    bc_biom: Optional[int] = Field(
        default=None,
        description="Input data file for biomass burning black carbon emissions.",
    )
    oc_anth: Optional[int] = Field(
        default=None,
        description="Input data file for anthropogenic organic carbon emissions.",
    )
    oc_ship: Optional[int] = Field(
        default=None,
        description="Input data file for ship organic carbon emissions.",
    )
    oc_biom: Optional[int] = Field(
        default=None,
        description="Input data file for biomass burning organic carbon emissions.",
    )
    volcano: Optional[int] = Field(
        default=None,
        description="Input data file for volcanic emissions.",
    )
    dmsfile: Optional[int] = Field(
        default=None,
        description="Input data file for DMS and natural organics.",
    )
    dustfile: Optional[int] = Field(
        default=None,
        description="Input data file for dust emissions.",
    )


class AeroemissConfig(CCAMBaseConfig):
    """Configuration options to be given to the aeroemiss executable.

    AEROEMISS creates aerosol emissions for CCAM.  Prognostic aerosols can influence the CCAM simulation through direct effects on the simulated radiation, as well as indirect effects with the cloud microphysics."""

    output: Path = Field(
        description="The output.nc Erosol emission file on the cubic grid."
    )

    aero: AeroemissConfigAero
