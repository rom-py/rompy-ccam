from typing import Optional, Annotated, Literal
from pathlib import Path

from pydantic import Field

from rompy_ccam import Input, Output, CCAMRootConfig, CCAMExeConfig, CCAMNamelistConfig


class TerreadNamelistConfigTop(CCAMRootConfig):
    """
    &topnml section of TERREAD config namelist.
    See https://research.csiro.au/ccam/software-and-model-configuration/terread-orography/.
    """

    # TODO: set correct data types, defaults etc.

    il: Optional[int] = Field(
        default=None,
        description="Size of the cubic grid.  For example, il=96 refers to 96 x 96 x 6 horizontal grid points, or 96 x 96 grid points for each of the six cubic panels.",
    )
    rlong0: Optional[float] = Field(
        default=None,
        description="Longitude corresponding to the centre of the variable resolution cubic grid.",
    )
    rlat0: Optional[float] = Field(
        default=None,
        description="Latitude corresponding to the centre of the variable resolution cubic grid.",
    )
    schmidt: Optional[float] = Field(
        default=None,
        description="Schmidt factor that controls the amount of grid stretching ( 0 > schmidt >= 1).  A value of schmidt=1 indicates no stretching or a (quasi-) uniform global grid.  The lower the value of Schmidt, then the greater the amount of stretching.  Simulations without atmospheric nudging are not recommended to use schmidt<0.3.  Also grids with schmidt<0.005 can require modifications to the atmospheric nudging.  Note that the mathematical Schmidt factor is >=1, so this parameter is the inverse of the mathematical definition.",
    )
    debug: Optional[bool] = Field(
        default=None,
        description="Whether to enable debug mode.",
    )
    idia: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    jdia: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    id: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    jd: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    luout: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    fileout: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Output filename for the orography data on the cubic grid, to be used by CCAM.",
        ),
        Output,
    ]
    do1km: Optional[bool] = Field(
        default=None,
        description="Set to ‘true’ to include 1 km DEM data in the output orography file.",
    )
    do250: Optional[bool] = Field(
        default=None,
        description="Set to ‘true’ to include 250m orography data for Australia in the output orography file.",
    )
    dosrtm: Optional[bool] = Field(
        default=None,
        description="Set to ‘true’ to include 50m STRM data in the output orography file.  This requires the user to download at least some of the STRM data.",
    )
    netout: Optional[bool] = Field(
        default=None,
        description="Set to ‘true’ to use NetCDF formatted output files (recommended).",
    )
    topfilt: Optional[bool] = Field(
        default=None,
        description="Set to ‘true’ to impose a 2*dx filter to smooth orography (recommended).",
    )
    filepath10km: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Location of 10 km input orography data (i.e., topo2).",
        ),
        Input,
    ]
    filepath1km: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Location of 1 km input orography data (i.e., location of *.DEM files).",
        ),
        Input,
    ]
    filepath250m: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Location of 250 m input orography data (i.e., location of *.ter files).",
        ),
        Input,
    ]
    filepathsrtm: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Location of 50 m input orography data (i.e., location of *.hgt files).",
        ),
        Input,
    ]
    do250lsm: Optional[bool] = Field(
        default=None,
        description="set to ‘true’ if wanting to use modis/srtm 250 m land sea mask data for high resolution region (Note: with this, possibly set siblsm=f in sibveg).",
    )
    filepath250mlsm: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="directory which contains the 250m grid land-sea mask panel data (data can be downloaded from https://hpc.csiro.au/users/72365/lsmdata/).",
        ),
        Input,
    ]


class TerreadNamelistConfig(CCAMNamelistConfig):
    """Configuration for the terread executable's configuration namelist (.nml)."""

    # nml_path is None as terread takes its namelist from stdin

    topnml: TerreadNamelistConfigTop


class TerreadConfig(CCAMExeConfig):
    """Configuration for the terread executable, used to create orography and land-sea mask data for the specified cubic grid."""

    model_type: Literal["terread"] = "terread"

    workflow_step_description = 'Create orography and land-sea mask data'

    input: TerreadNamelistConfig

    def bash_invocation(self) -> str:
        return self.bash_prettify_invocation(
            f'terread < "{self.input.nml_path}"'
        )

    def __call__(self, *args, **kwargs):
        self.input.write_nml_file()
