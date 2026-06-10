from pathlib import Path
from typing import Annotated, Optional, Literal

from pydantic import Field

from ..fileio_config import Input, Output
from ..rompy_ccam import CCAMRootConfig, CCAMExeConfig
from ..namelists import CCAMNamelistConfig


class OcnbathNamelistConfigOcn(CCAMRootConfig):
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


class OcnbathNamelistConfig(CCAMNamelistConfig):
    """Configuration for the ocnbath executable's configuration namelist."""

    nml_path: Path = Path("ocnbath.nml")

    ocnnml: OcnbathNamelistConfigOcn


class OcnbathConfig(CCAMExeConfig):
    """Configuration for the ocnbath executable, used to calculate ocean/lake bathymetry and also determine river routing."""

    model_type: Literal["ocnbath"] = "ocnbath"

    workflow_step_description: Optional[str] = (
        "Calculate ocean/lake bathymetry and determine river routing"
    )

    s: Optional[int] = Field(
        default=None,
        description="Size of array used for reading ETOPO data (typically =500). The larger the array, the faster and more accurate the output.",
    )

    input: OcnbathNamelistConfig

    def bash_invocation(self) -> str:
        args = []
        if self.s is not None:
            args.append(f"-s {self.s}")
        args.append(f'< "{self.input.nml_path}"')
        return self.bash_prettify_invocation(f'run_cmd ocnbath {" ".join(args)}')

    def __call__(
        self, runtime
    ):  # runtime is a ModelRun, which can't be imported due to circular dependency
        self.write_nml_file(Path(runtime.staging_dir))
