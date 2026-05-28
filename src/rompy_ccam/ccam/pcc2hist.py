import sys
from enum import IntEnum

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum
from pathlib import Path
from typing import Optional, Annotated

from pydantic import Field

from rompy_ccam import CCAMRootConfig, CCAMExeConfig, Input, Output, CCAMNamelistConfig


class Pcc2HistType(StrEnum):
    """Type of output field for pcc2hist."""

    AVE = "ave"  # The default
    MAX = "max"
    MIN = "min"
    INST = "inst"
    FIXED = "fixed"


class Pcc2HistInterp(IntEnum):
    """Interpolation modes for PCC2HIST"""

    BICUBIC = 0
    NEAREST = 1
    BILINEAR = 2
    NONE = 5
    TAPM = 9


class Pcc2HistInterpLong(StrEnum):
    """String versions of interpolation modes for PCC2HIST"""

    NONE = "none"  # output cubic grid (for combining parallel files)
    NEAREST = "nearest"  # nearest value interpolation
    LINEAR = "linear"  # use bi-linear interpolation
    TAPM = "tapm"  # output on the TAPM grid


class Pcc2HistVExtrap(StrEnum):
    """Vertical extrapolation modes for PCC2HIST"""

    NONE = "none"  # no extrapolation
    LINEAR = "linear"  # linearly extrapolate vertical values
    MISSING = "missing"  # use missing values instead of extrapolation


class Pcc2HistNamelistConfigHistnl(CCAMRootConfig):
    """&histnl section of PCC2HIST config namelist."""

    hnames: list[str] = Field(
        default=[],  # TODO: should the default instead be ["all"]?
        description="List of output variable names.  Use hnames=”all” for all output variables.",
    )
    hfreq: Optional[int] = Field(
        default=None,
        description="Frequency of output data in minutes.  hfreq=0 is instantaneous output, hfreq=1440 is daily output.",
    )
    htype: Optional[Pcc2HistType] = Field(
        default=None,
        description="Type of output field. Default is 4 byte floating point output.",
    )


class Pcc2HistNamelistConfigInput(CCAMRootConfig):
    """&input section of PCC2HIST config namelist."""

    # TODO: set correct data types, defaults etc.
    ifile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input filename (output from CCAM).  Do not include the “.000000” extension, but use the same name as the CCAM ofile.",
        ),
        Input,
    ]
    ofile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Output filename.",
        ),
        Output,
    ]
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
    minlat: Optional[float] = Field(
        default=None,
        description="Minimum latitude of bounding box for regular output.",
        ge=-90,
        le=90,
    )
    maxlat: Optional[float] = Field(
        default=None,
        description="Maximum latitude of bounding box for regular output.",
    )
    minlon: Optional[float] = Field(
        default=None,
        description="Minimum longitude of bounding box for regular output.",
        ge=0,
        le=360,
    )
    maxlon: Optional[float] = Field(
        default=None,
        description="Maximum longitude of bounding box for regular output.",
        ge=0,
        le=360,
    )
    hres: Optional[float] = Field(
        default=None,
        description="Output resolution in degrees.",
        ge=0,
    )
    use_plevs: Optional[bool] = Field(
        default=None,
        description="Set to True for output on pressure levels.",
    )
    plevs: list[int] = Field(
        default=[],
        description="List of pressure levels for output in hPa.",
    )
    use_meters: Optional[bool] = Field(
        default=None,
        description="Set to True for output on meters above surface.",
    )
    mlevs: list[int] = Field(
        default=[],
        description="List of meter heights for output.",
    )
    dx: Optional[float] = Field(
        default=None,
        description="X grid spacing in meters for TAPM output.",
        gt=0,
    )
    dy: Optional[float] = Field(
        default=None,
        description="Y grid spacing in meters for TAPM output.",
    )
    lx: Optional[int] = Field(
        default=None,
        description="Number of X grid points for TAPM output.",
        gt=0,
    )
    ly: Optional[int] = Field(
        default=None,
        description="Number of Y grid points for TAPM output.",
        gt=0,
    )
    save_ccam_parameters: Optional[bool] = Field(
        default=None,
        description="Allows CCAM parameters to be saved in the history file when True (default).",
    )
    int_default: Optional[Pcc2HistInterp] = Field(
        default=None,
        description="The default interpolation mode to use.",
    )


class Pcc2HistNamelistConfig(CCAMNamelistConfig):
    """Configuration for the pcc2hist executable's configuration namelist (.nml).
    See https://research.csiro.au/ccam/software-and-model-configuration/pcc2hist-process-cubic-output-to-lat-lon/.
    """

    # This can be overridden
    nml_path: Optional[Path] = Path("cc.nml")

    input: Optional[Pcc2HistNamelistConfigInput] = None
    histnl: Optional[Pcc2HistNamelistConfigHistnl] = None


class Pcc2HistConfig(CCAMExeConfig):
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
    interp: Pcc2HistInterpLong = Field(
        default=Pcc2HistInterpLong.NONE,
        description="The interpolation mode",
    )
    vextrap: Pcc2HistVExtrap = Field(
        default=Pcc2HistVExtrap.NONE,
        description="The vertical extrapolation mode",
    )
    input: Pcc2HistNamelistConfig

    def bash_invocation(self) -> str:
        args = []
        if self.cordex:
            args.append("--cordex")
        if self.interp != Pcc2HistInterpLong.NONE:
            args.append(f"--interp {self.interp}")
        if self.vextrap != Pcc2HistVExtrap.NONE:
            args.append(f"--vextrap {self.vextrap}")
        args.append(f'-c "{self.input.nml_path}"')
        return self.bash_prettify_invocation(f'run_mpi_cmd pcc2hist {" ".join(args)}')

    def __call__(self, *args, **kwargs):
        self.input.write_nml_file()
