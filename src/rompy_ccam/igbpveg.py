import sys
from typing import Optional, Annotated

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum
from pathlib import Path

from pydantic import Field

from rompy_ccam.types import CCAMBaseConfig, NMLConfig, Input, Output


class IgbpvegOutputMode(StrEnum):
    """Output mode for IGBPVEG"""

    CABLEPFT = "cablepft"  # output indices are for CABLE plant functional types
    IGBP = "igbp"  # output indices are in terms of IGBP vegetation classes


class IgbpvegNamelistConfigVeg(CCAMBaseConfig):
    """&vegnml section of IGBPVEG config namelist. See https://research.csiro.au/ccam/software-and-model-configuration/igbpveg-vegetation-soil-and-urban/"""

    # TODO: set correct data types, defaults etc.
    month: Optional[int] = Field(
        default=None,
        description="Month of the year (month=1-12) to process land-cover data.  Specifically, month determines what LAI data is used for the output file.  month=0 processes all months of the year.",
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
            description="Output topography file.  This file is created for when the user specifies that the land-use dataset should determine the land-sea mask.  Hence newtopofile contains the modified topography file to account for the land-sea changes.",
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
        Optional[Path],
        Field(
            default=None,
            description="Specifies the location of the land-use classification input file (i.e., gigbp2_0ll.img).",
        ),
        Input,
    ]
    soilinput: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Specify location of the soil texture input file (i.e., usda4.img).",
        ),
        Input,
    ]
    laiinput: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Specify the directory where the LAI data is located (i.e., slai*.img).",
        ),
        Input,
    ]
    albvisinput: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Specify the location of the visible soil albedo input file (i.e., salbvis223.img).",
        ),
        Input,
    ]
    albnirinput: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Specify the location of the near-infrared soil albedo input file (i.e., salbnir223.img).",
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


class IgbpvegNamelistConfig(NMLConfig):
    """Configuration for the igbpveg executable. To be output as a namelist file. e.g. igbpveg.nml."""

    # nml_path is None as igbpveg takes its namelist from stdin

    vegnml: IgbpvegNamelistConfigVeg


class IgbpvegConfig(CCAMBaseConfig):
    """Configuration for the igbpveg executable, which produces land-cover datasets for CCAM with the CABLE land-surface model."""

    s: Optional[int] = Field(
        default=None,
        description="Command-line option which controls how much data is processed in memory. Larger values of -s increase memory usage, but can speed-up igbpveg.",
    )

    input: IgbpvegNamelistConfig
