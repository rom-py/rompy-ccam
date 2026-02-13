from typing import Optional

from pydantic import Field

from rompy_ccam.types import CCAMBaseConfig

class CdfvidarNamelistConfigG(CCAMBaseConfig):
    """&gnml section of CDFVIDAR config namelist. See https://research.csiro.au/ccam/software-and-model-configuration/cdfvidar-process-lat-lon-input-to-cubic/."""
    # TODO: set correct data types, defaults etc.
    kl: Optional[int] = Field(
        default=None,
        description="Number of vertical levels.",
    )
    t_file: Optional[int] = Field(
        default=None,
        description="Input air temperature.",
    )
    rh_file: Optional[int] = Field(
        default=None,
        description="Input relative humidity or mixing ratio or specific humidity.",
    )
    u_file: Optional[int] = Field(
        default=None,
        description="Input zonal wind.",
    )
    v_file: Optional[int] = Field(
        default=None,
        description="Input meridonal wind.",
    )
    z_file: Optional[int] = Field(
        default=None,
        description="(optional) input geopotential height.",
    )
    lsm_file: Optional[int] = Field(
        default=None,
        description="input land-sea mask.",
    )
    zs_file: Optional[int] = Field(
        default=None,
        description="input surface geopotential height.",
    )
    ps_file: Optional[int] = Field(
        default=None,
        description="input surface pressure.",
    )
    psl_file: Optional[int] = Field(
        default=None,
        description="(optional) input mean sea level pressure.",
    )
    ts_file: Optional[int] = Field(
        default=None,
        description="input surface temperature (or tos for water).",
    )
    sic_file: Optional[int] = Field(
        default=None,
        description="(optional) input sea-ice fraction.",
    )
    snod_file: Optional[int] = Field(
        default=None,
        description="(optional) input snow depth file.",
    )
    soiltemp_file: Optional[int] = Field(
        default=None,
        description="(optional) input soil temperature file.",
    )
    soilmois_file: Optional[int] = Field(
        default=None,
        description="(optional) input soil moisture file.",
    )
    inf: Optional[int] = Field(
        default=None,
        description="(optional) single file input with all variables.  Used for backwards compatibility..",
    )
    zsfil: Optional[int] = Field(
        default=None,
        description="Topography file (from terread) to be used to remap the meteorological data.",
    )
    vfil: Optional[int] = Field(
        default=None,
        description="Output file for the conformal cubic grid.",
    )
    sgml: Optional[int] = Field(
        default=None,
        description="List of sigma levels for vertical interpolation.",
    )

class CdfvidarNamelistConfig(CCAMBaseConfig):
    """Configuration for the cdfvidar executable's configuration namelist."""
    gnml: CdfvidarNamelistConfigG

class CdfvidarConfig(CCAMBaseConfig):
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

    input: CdfvidarNamelistConfig
