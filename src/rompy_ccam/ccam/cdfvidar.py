import sys

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
from typing import Optional, Annotated, Literal
from pathlib import Path

from pydantic import Field, model_validator

from rompy_ccam import CCAMRootConfig, CCAMExeConfig, CCAMNamelistConfig, Input, Output


class CdfvidarNamelistConfigG(CCAMRootConfig):
    """&gnml section of CDFVIDAR config namelist. See https://research.csiro.au/ccam/software-and-model-configuration/cdfvidar-process-lat-lon-input-to-cubic/."""

    @model_validator(mode="after")
    def check_inf_or_t_file(self) -> Self:
        if self.inf is None and self.t_file is None:
            raise ValueError("Either 'inf' or 't_file' must be provided", self)
        return self

    # TODO: set correct data types, defaults etc.
    kl: Optional[int] = Field(
        default=None,
        description="Number of vertical levels.",
    )
    t_file: Annotated[
        Optional[Path],
        Input,
        Field(
            default=None,
            description="Input air temperature.",
        ),
    ]
    rh_file: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input relative humidity or mixing ratio or specific humidity.",
        ),
        Input,
    ]
    u_file: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input zonal wind.",
        ),
        Input,
    ]
    v_file: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input meridonal wind.",
        ),
        Input,
    ]
    z_file: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="(optional) input geopotential height.",
        ),
        Input,
    ]
    lsm_file: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="input land-sea mask.",
        ),
        Input,
    ]
    zs_file: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="input surface geopotential height.",
        ),
        Input,
    ]
    ps_file: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="input surface pressure.",
        ),
        Input,
    ]
    psl_file: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="(optional) input mean sea level pressure.",
        ),
        Input,
    ]
    ts_file: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="input surface temperature (or tos for water).",
        ),
        Input,
    ]
    sic_file: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="(optional) input sea-ice fraction.",
        ),
        Input,
    ]
    snod_file: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="(optional) input snow depth file.",
        ),
        Input,
    ]
    soiltemp_file: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="(optional) input soil temperature file.",
        ),
        Input,
    ]
    soilmois_file: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="(optional) input soil moisture file.",
        ),
        Input,
    ]
    inf: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="(optional) single file input with all variables.  Used for backwards compatibility.",
        ),
        Input,
    ]
    zsfil: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Topography file (from terread) to be used to remap the meteorological data.",
        ),
        Input,
    ]
    vfil: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Output file for the conformal cubic grid.",
        ),
        Output,
    ]
    sgml: list[float] = Field(
        default=[],
        description="List of sigma levels for vertical interpolation.",
    )

    # The below were undocumented at time of writing, but in use
    inzsavn: Optional[int] = Field(default=None, description="TODO")
    zsavn: Annotated[
        Optional[Path],
        Field(default=None, description="TODO"),
        Input,
    ]
    inlsavn: Optional[int] = Field(default=None, description="TODO")
    lsavn: Annotated[
        Optional[Path],
        Field(default=None, description="TODO"),
        Input,
    ]
    io_out: Optional[int] = Field(default=None, description="TODO")
    nrh: Optional[int] = Field(default=None, description="TODO")
    mxcyc: Optional[int] = Field(default=None, description="TODO")
    debug: Optional[bool] = Field(default=None, description="TODO")
    nvsig: Optional[int] = Field(default=None, description="TODO")
    in_: Optional[int] = Field(
        default=None, description="TODO", serialization_alias="in"
    )
    iout: Optional[int] = Field(default=None, description="TODO")
    notop: Optional[bool] = Field(default=None, description="TODO")
    oform: Optional[bool] = Field(default=None, description="TODO")
    oesig: Optional[bool] = Field(default=None, description="TODO")
    ptop: Optional[float] = Field(default=None, description="TODO")
    calout: Optional[bool] = Field(default=None, description="TODO")
    ints: Optional[int] = Field(default=None, description="TODO")
    inzs: Optional[int] = Field(default=None, description="TODO")
    opre: Optional[bool] = Field(default=None, description="TODO")
    spline: Optional[bool] = Field(default=None, description="TODO")
    ntimes: Optional[int] = Field(default=None, description="TODO")
    splineu: Optional[bool] = Field(default=None, description="TODO")
    splinev: Optional[bool] = Field(default=None, description="TODO")
    splinet: Optional[bool] = Field(default=None, description="TODO")
    zerowinds: Optional[bool] = Field(default=None, description="TODO")


class CdfvidarNamelistConfig(CCAMNamelistConfig):
    """Configuration for the cdfvidar executable's configuration namelist."""

    nml_path: Path = Path("cdfvidar.nml")

    gnml: CdfvidarNamelistConfigG = Field(
        default_factory=CdfvidarNamelistConfigG,
        description="gnml section of the cdfvidar configuration namelist",
    )


class CdfvidarConfig(CCAMExeConfig):
    """Configuration options to be given to the cdfvidar executable.

    Cdfvidar is used to convert GCM, reanalyses, analyses or other weather and climate data into initial conditions or mesonest host files for nudging with the conformal cubic format.
    Input files are usually formatted as described in the table below.
    Typically the input files are on pressure levels (hPa) or sigma-pressure levels.

    +------------------------------------------+-----------------+-----------+----------------------------------------+
    | Name                                     | Units           | Dimension | cdfvidar name in input netcdf file     |
    +==========================================+=================+===========+========================================+
    | Geopotential height (optional)           | m               |        3D | hgt, z or geop_ht                      |
    +------------------------------------------+-----------------+-----------+----------------------------------------+
    | Air temperature                          | K               |        3D | temp, ta or air_temp                   |
    +------------------------------------------+-----------------+-----------+----------------------------------------+
    | U-component of wind                      | m/s             |        3D | u, ua or zonal_wnd                     |
    +------------------------------------------+-----------------+-----------+----------------------------------------+
    | V-component of wind                      | m/s             |        3D | v, va or merid_wnd                     |
    +------------------------------------------+-----------------+-----------+----------------------------------------+
    | Relative humidity                        | % or fraction   |        3D | rh or relhum                           |
    +------------------------------------------+-----------------+-----------+----------------------------------------+
    | Water vapour mixing ratio                |                 |           |                                        |
    | (as an alternative to relative humidity) | kg/kg           |        3D | mix_rto or hus                         |
    +------------------------------------------+-----------------+-----------+----------------------------------------+
    | Surface geopotential height              | m               |        2D | zs, orog, topo or topog                |
    +------------------------------------------+-----------------+-----------+----------------------------------------+
    | Surface temperature                      |                 |           |                                        |
    | (including sea surface temperature)      | K               |        2D | tss, tos or sfc_temp                   |
    +------------------------------------------+-----------------+-----------+----------------------------------------+
    | Mean sea level pressure (optional)       | Pa              |        2D | mslp, psl or pmsl                      |
    +------------------------------------------+-----------------+-----------+----------------------------------------+
    | Surface pressure                         | Pa              |        2D | ps or sfc_pres                         |
    +------------------------------------------+-----------------+-----------+----------------------------------------+
    | Land/sea mask (sea=0, land>0)            | index           |        2D | land, lsm, sftlf, sfc_lsm or land_mask |
    +------------------------------------------+-----------------+-----------+----------------------------------------+
    | Sea ice cover fraction (optional)        | fraction        |        2D | fracice, sic or seaice                 |
    +------------------------------------------+-----------------+-----------+----------------------------------------+
    | Snow depth (optional)                    | m               |        2D | snod or snow_amt_lnd                   |
    +------------------------------------------+-----------------+-----------+----------------------------------------+
    | Soil temperature (optional)              | K               |        3D | soil_temp                              |
    +------------------------------------------+-----------------+-----------+----------------------------------------+
    | Soil moisture (optional)                 | m3/m3           |        3D | soil_moist                             |
    +------------------------------------------+-----------------+-----------+----------------------------------------+
    """

    model_type: Literal["cdfvidar"] = "cdfvidar"

    workflow_step_description: Optional[str] = (
        "Convert weather or climate data into conformal cubic format"
    )

    input: CdfvidarNamelistConfig = Field(
        default_factory=CdfvidarNamelistConfig,
        description="Configuration for cdfvidar, given as a namelist",
    )

    def bash_invocation(self) -> str:
        return self.bash_prettify_invocation(f"cdfvidar < {self.input.nml_path}")

    def __call__(
        self, runtime
    ):  # runtime is a ModelRun, which can't be imported due to circularity
        self.input.write_nml_file(Path(runtime.staging_dir))
