from typing import Optional

from pydantic import Field

from rompy_ccam.types import CCAMBaseConfig


class OcnbathConfigOcn:
    """&ocnnml section of OCNBATH config namelist. See https://research.csiro.au/ccam/software-and-model-configuration/ocnbath-bathymetry-and-river-routing/."""

    # TODO: set correct data types, defaults etc.
    bathout: Optional[int] = Field(
        default=None,
        description="Output file containing bathymetry and river routing data.  To be read by CCAM. .",
    )
    topofile: Optional[int] = Field(
        default=None,
        description="Topography file created by terread (to define land/sea mask).",
    )
    bathdatafile: Optional[int] = Field(
        default=None,
        description="Location of etopo1_ice_c.flt bathymetry data.",
    )
    riverdatapath: Optional[int] = Field(
        default=None,
        description="Location of river routing *.bil files.",
    )
    fastocn: Optional[int] = Field(
        default=None,
        description="When True, then ocnbath pre-aggregates data on lat/lon grid to improve speed.",
    )
    bathfilt: Optional[int] = Field(
        default=None,
        description="When True, applies a 2*dx filter to smooth bathymetry.",
    )
    binlimit: Optional[int] = Field(
        default=None,
        description="Minimum number of input data points that need to be included in an output grid point before switching from aggregation to interpolation.",
    )


class OcnbathConfig(CCAMBaseConfig):
    """Configuration for the ocnbath executable. To be output as a namelist file, e.g. ocnbath.nml."""

    ocnnml: OcnbathConfigOcn
