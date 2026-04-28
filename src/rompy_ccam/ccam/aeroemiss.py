from pathlib import Path
from typing import Annotated, Optional, Literal

from pydantic import Field

from rompy_ccam import CCAMRootConfig, CCAMExeConfig, CCAMNamelistConfig, Input, Output


class AeroemissConfigAero(CCAMRootConfig):
    """&aero section of AEROEMISS config namelist."""

    # TODO: set correct data types, defaults etc.
    month: Optional[int] = Field(
        default=None,
        description="Month of the year to process aerosol emissions (1-12).",
    )
    topofile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Topography file (from TERREAD) used to configure the CCAM grid.",
        ),
        Input,
    ]
    so2_anth: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input data file for anthropogenic SO2 emissions.",
        ),
        Input,
    ]
    so2_ship: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input data file for ship SO2 emissions.",
        ),
        Input,
    ]
    so2_biom: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input data file for biomass burning SO2 emissions.",
        ),
        Input,
    ]
    bc_anth: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input data file for anthropogenic black carbon emissions.",
        ),
        Input,
    ]
    bc_ship: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input data file for ship black carbon emissions.",
        ),
        Input,
    ]
    bc_biom: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input data file for biomass burning black carbon emissions.",
        ),
        Input,
    ]
    oc_anth: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input data file for anthropogenic organic carbon emissions.",
        ),
        Input,
    ]
    oc_ship: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input data file for ship organic carbon emissions.",
        ),
        Input,
    ]
    oc_biom: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input data file for biomass burning organic carbon emissions.",
        ),
        Input,
    ]
    volcano: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input data file for volcanic emissions.",
        ),
        Input,
    ]
    dmsfile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input data file for DMS and natural organics.",
        ),
        Input,
    ]
    dustfile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input data file for dust emissions.",
        ),
        Input,
    ]


class AeroemissConfig(CCAMExeConfig, CCAMNamelistConfig):
    """Configuration options to be given to the aeroemiss executable.

    AEROEMISS creates aerosol emissions for CCAM.  Prognostic aerosols can influence the CCAM simulation through direct effects on the simulated radiation, as well as indirect effects with the cloud microphysics.
    """

    model_type: Literal["aeroemiss"] = "aeroemiss"

    output: Annotated[
        Path,
        Field(description="The output.nc Erosol emission file on the cubic grid."),
        Output,
    ]

    aero: AeroemissConfigAero

    def bash_invocation(self) -> str:
        args = [f"-o {self.output}", f"< {self.nml_path}"]
        return self.bash_prettify_invocation(f'aeromiss {" ".join(args)}')

    def __call__(self, *args, **kwargs):
        self.write_nml_file()
