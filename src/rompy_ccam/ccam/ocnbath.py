from pathlib import Path
from typing import Annotated, Optional, Literal

from pydantic import Field

from rompy_ccam.rompy_ccam import CCAMConfig, CCAMBaseConfig
from rompy_ccam.namelists import CCAMNamelistConfig
from rompy_ccam.composable_fileio_config import Input, Output


class OcnbathConfigOcn(CCAMConfig):
    """&ocnnml section of OCNBATH config namelist. See https://research.csiro.au/ccam/software-and-model-configuration/ocnbath-bathymetry-and-river-routing/."""

    bathout: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Output file containing bathymetry and river routing data.  To be read by CCAM. .",
        ),
        Output,
    ]
    topofile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Topography file created by terread (to define land/sea mask).",
        ),
        Input,
    ]
    bathdatafile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Location of etopo1_ice_c.flt bathymetry data.",
        ),
        Input,
    ]
    riverdatapath: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Location of river routing *.bil files.",
        ),
        Input,
    ]
    fastocn: Optional[bool] = Field(
        default=None,
        description="When True, then ocnbath pre-aggregates data on lat/lon grid to improve speed.",
    )
    bathfilt: Optional[bool] = Field(
        default=None,
        description="When True, applies a 2*dx filter to smooth bathymetry.",
    )
    binlimit: Optional[int] = Field(
        default=None,
        description="Minimum number of input data points that need to be included in an output grid point before switching from aggregation to interpolation.",
    )


class OcnbathConfig(CCAMBaseConfig, CCAMNamelistConfig):
    """Configuration for the ocnbath executable. To be output as a namelist file, e.g. ocnbath.nml."""

    model_type: Literal["ocnbath"] = "ocnbath"

    ocnnml: OcnbathConfigOcn
