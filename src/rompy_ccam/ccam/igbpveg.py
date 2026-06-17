import sys
from typing import Optional, Annotated, Literal

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum
from pathlib import Path

from pydantic import Field

from ..fileio_config import Input, Output
from ..rompy_ccam import CCAMRootConfig, CCAMExeConfig
from ..namelists import CCAMNamelistConfig


class IgbpvegOutputMode(StrEnum):
    """Output mode for IGBPVEG"""

    CABLEPFT = "cablepft"  # output indices are for CABLE plant functional types
    IGBP = "igbp"  # output indices are in terms of IGBP vegetation classes


class IgbpvegNamelistConfigVeg(CCAMRootConfig):
    """&vegnml section of IGBPVEG config namelist. See https://research.csiro.au/ccam/software-and-model-configuration/igbpveg-vegetation-soil-and-urban/"""

    # TODO: set correct data types, defaults etc.
    month: Optional[int] = Field(
        default=None,
        description="Month of the year (month=1-12) to process land-cover data.  Specifically, month determines what LAI data is used for the output file.  month=0 processes all months of the year. 0 is igbpveg's default.",
    )
    topofile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input topography file which determines the cubic grid and (possibly) land-sea mask.",
        ),
        Input,
    ]
    newtopofile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Output topography file.  This file is created for when the user specifies that the land-use dataset should determine the land-sea mask, by setting `igbplsmask = True`.  Hence newtopofile contains the modified topography file to account for the land-sea changes.",
        ),
        Output,
    ]
    landtypeout: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Output land-use file.  In NetCDF mode, the landtypeout file contains all the land-use data for a specified month.  This file is used by the CCAM simulation.",
        ),
        Output,
    ]
    veginput: Annotated[
        Path,
        Field(
            default=Path("gigbp2_0ll.img"),
            description="Specifies the location of the land-use classification input file (i.e., gigbp2_0ll.img).",
        ),
        Input,
    ]
    soilinput: Annotated[
        Path,
        Field(
            default=Path("usda4.img"),
            description="Specify location of the soil texture input file (i.e., usda4.img).",
        ),
        Input,
    ]
    laiinput: Annotated[
        Path,
        Field(
            # we have set a default path, because igpbveg's default is the empty string,
            # so it ends up looking for e.g. /slai01.img, which isn't helpful.
            # TODO: we could put in some validation around this, to check that laiinput is
            # a directory if month=0, otherwise a file, etc.
            default=Path("."),
            description="If month is 0, then this specifies the directory where the Leaf Area Index (LAI) data is located (i.e., slai[1-12].img). If month is between 1 and 12 then this specifies the LAI data file to use (e.g. slai03.img).",
        ),
        Input,
    ]
    albvisinput: Annotated[
        Path,
        Field(
            default=Path("salbvis_landcover2020.img.nc"),
            description="Specify the location of the visible soil albedo input file (e.g. salbvis223.img).",
        ),
        Input,
    ]
    albnirinput: Annotated[
        Path,
        Field(
            default=Path("salbnir_landcover2020.img.nc"),
            description="Specify the location of the near-infrared soil albedo input file (e.g., salbnir223.img).",
        ),
        Input,
    ]
    fastigbp: Optional[bool] = Field(
        default=None,
        description="Option to improve the processing speed of igbpveg (fastigbp=True), by aggregating data on the lat/lon grid.",
    )
    igbplsmask: Optional[bool] = Field(
        default=None,
        description="When set to True, this option specifies that the land-sea mask should be determined by the land-use data.",
    )
    binlimit: Optional[int] = Field(
        default=None,
        description="Specifies when igbpveg should switch from binning data to using nearest neighbour.  binlimit=2 indicates that there should be at least 2 x 2 grid points used from the input data for binning in an output grid point.",
    )
    tile: Optional[bool] = Field(
        default=None,
        description="When set to True, allows multiple vegetation tiles and LAI to be assigned to a grid point.",
    )
    outputmode: Optional[IgbpvegOutputMode] = Field(
        default=None,
        description="Specifies the format of the output land-use data.  When using ‘cablepft’, then the output indices are for CABLE plant functional types.  When using ‘igbp’ then output indices are in terms of IGBP vegetation classes.",
    )
    pftconfig: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input file that defines plant functional type parameters.",
        ),
        Input,
    ]
    mapconfig: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input file that relates indices in the input file to plant functional types.",
        ),
        Input,
    ]
    atebconfig: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input file that defines the parameters for different urban classes.",
        ),
        Input,
    ]
    user_veginput: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="User specified land-cover data that is used to override the default land-cover data for the specified domain.",
        ),
        Input,
    ]
    ovegfrac: Optional[bool] = Field(
        default=None,
        description="Option to use vegtype fractions to determine land use type instead of land_cover (default False).",
    )
    user_laiinput: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="User specified LAI data that is used to override the default LAI data for the specified domain.",
        ),
        Input,
    ]


class IgbpvegNamelistConfig(CCAMNamelistConfig):
    """Configuration for the igbpveg executable. To be output as a namelist file. e.g. igbpveg.nml."""

    nml_path: Path = Path("igbpveg.nml")

    vegnml: IgbpvegNamelistConfigVeg = Field(
        default_factory=IgbpvegNamelistConfigVeg,
        description="vegnml section of the igbpveg namelist",
    )


class IgbpvegConfig(CCAMExeConfig):
    """Configuration for the igbpveg executable, which produces land-cover datasets for CCAM with the CABLE land-surface model."""

    model_type: Literal["igbpveg"] = "igbpveg"

    workflow_step_description: Optional[str] = "Produce land-cover dataset"

    s: int = Field(
        default=500,
        description="Command-line option which controls how much data is processed in memory. Larger values of -s increase memory usage, but can speed-up igbpveg.",
    )

    input: IgbpvegNamelistConfig = Field(
        default_factory=IgbpvegNamelistConfig,
        description="igbpveg configuration given as a namelist",
    )

    def bash_invocation(self) -> str:
        args = [f"-s {self.s}", f'< "{self.input.nml_path}"']
        return self.bash_prettify_invocation(f'igbpveg {" ".join(args)}')

    def __call__(
        self, runtime
    ):  # runtime is a ModelRun, which can't be imported due to circularity
        self.input.write_nml_file(Path(runtime.staging_dir))
