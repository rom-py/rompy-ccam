import sys
from typing import Optional
if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum

from pydantic import Field

from rompy_ccam.types import CCAMBaseConfig

class Pcc2HistNamelistConfigHistnl(CCAMBaseConfig):
    """&histnl section of PCC2HIST config namelist."""
    hnames: Optional[int] = Field(
        default=None,
        description="List of output variable names.  Use hnames=”all” for all output variables.",
    )
    hfreq: Optional[int] = Field(
        default=None,
        description="Frequency of output data in minutes.  hfreq=0 is instantaneous output, hfreq=1440 is daily output.",
    )
    htype: Optional[int] = Field(
        default=None,
        description="Type of output field.  Default is 4 byte floating point output.",
    )

class Pcc2HistNamelistConfigInput(CCAMBaseConfig):
    """&input section of PCC2HIST config namelist."""
    # TODO: set correct data types, defaults etc.
    ifile: Optional[int] = Field(
        default=None,
        description="Input filename (output from CCAM).  Do not include the “.000000” extension, but use the same name as the CCAM ofile.",
    )
    ofile: Optional[int] = Field(
        default=None,
        description="Output filename.",
    )
    kta: Optional[int] = Field(
        default=None,
        description="Start time for reading data in mins (seconds for high-frequency output).",
    )
    ktb: Optional[int] = Field(
        default=None,
        description="End time for reading data in mins (seconds for high-frequency output).",
    )
    ktc: Optional[int] = Field(
        default=None,
        description="Time step for reading data in mins (seconds for high-frequency output).  Use -1 for all time-steps.",
    )
    minlat: Optional[int] = Field(
        default=None,
        description="Minimum latitude of bounding box for regular output.",
    )
    maxlat: Optional[int] = Field(
        default=None,
        description="Maximum latitude of bounding box for regular output.",
    )
    minlon: Optional[int] = Field(
        default=None,
        description="Minimum longitude of bounding box for regular output.",
    )
    maxlon: Optional[int] = Field(
        default=None,
        description="Maximum longitude of bounding box for regular output.",
    )
    hres: Optional[int] = Field(
        default=None,
        description="Output resolution in degrees.",
    )
    use_plevs: Optional[int] = Field(
        default=None,
        description="Set to True for output on pressure levels.",
    )
    plevs: Optional[int] = Field(
        default=None,
        description="List of pressure levels for output in hPa.",
    )
    use_meters: Optional[int] = Field(
        default=None,
        description="Set to True for output on meters above surface.",
    )
    mlevs: Optional[int] = Field(
        default=None,
        description="List of meter heights for output.",
    )
    dx: Optional[int] = Field(
        default=None,
        description="X grid spacing in meters for TAPM output.",
    )
    dy: Optional[int] = Field(
        default=None,
        description="Y grid spacing in meters for TAPM output.",
    )
    lx: Optional[int] = Field(
        default=None,
        description="Number of X grid points for TAPM output.",
    )
    ly: Optional[int] = Field(
        default=None,
        description="Number of Y grid points for TAPM output.",
    )
    save_ccam_parameters: Optional[bool] = Field(
        default=None,
        description="Allows CCAM parameters to be saved in the history file when TRUE (default).",
    )

class Pcc2HistNamelistConfig(CCAMBaseConfig):
    """Configuration for the pcc2hist executable's configuration namelist (.nml).
    See https://research.csiro.au/ccam/software-and-model-configuration/pcc2hist-process-cubic-output-to-lat-lon/.
    """
    input: Pcc2HistNamelistConfigInput
    histnl: Pcc2HistNamelistConfigHistnl

class Pcc2HistInterp(StrEnum):
    """Interpolation modes for PCC2HIST"""
    INTERP_NONE = "none"       # output cubic grid (for combining parallel files)
    INTERP_NEAREST = "nearest" # nearest value interpolation
    INTERP_LINEAR = "linear"   # use bi-linear interpolation
    INTERP_TAPM = "tapm"       # output on the TAPM grid

class Pcc2HistVExtrap(StrEnum):
    """Vertical extrapolation modes for PCC2HIST"""
    EXTRAP_NONE = "none"       # no extrapolation
    EXTRAP_LINEAR = "linear"   # linearly extrapolate vertical values
    EXTRAP_MISSING = "missing" # use missing values instead of extrapolation

class Pcc2histConfig(CCAMBaseConfig):
    """Configuration options for the pcc2hist executable.

    PCC2HIST is used to post-process CCAM output from the cubic grid to the required output grid.
    Usually the output is a regular latitude / longitude grid.
    However, it is possible to output raw cubic grid (for combining parallel files) or TAPM grids.
    A list of pcc2hist output variables can be found at https://research.csiro.au/ccam/scientific-description/ccam-output-variables/.
    """
    cordex: bool = Field(
        default=False,
        description="Format output for CORDEX.",
    )
    interp: Pcc2HistInterp = Field(
        default=Pcc2HistInterp.INTERP_NONE,
        description="The interpolation mode",
    )
    vextrap: Pcc2HistVExtrap = Field(
        default=Pcc2HistVExtrap.EXTRAP_NONE,
        description="The vertical extrapolation mode",
    )
    input: Pcc2HistNamelistConfig
