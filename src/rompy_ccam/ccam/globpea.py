"""Rompy config for the globpea executable (the main CCAM model).

This should match the CCAM namelist options at https://research.csiro.au/ccam/software-and-model-configuration/globpea-atmospheric-model/
and can be used to generate the namelist (.nml) and other files for a run of `globpea`.
"""

from datetime import date, time
from enum import IntEnum
from pathlib import Path
from typing import Optional, Annotated, Literal

from pydantic import Field, field_serializer

from ..fileio_config import Input, Output
from ..rompy_ccam import CCAMRootConfig, CCAMExeConfig
from ..namelists import CCAMNamelistConfig
from ..types import Flag


class GlobpeaNamelistConfigDefaults(CCAMRootConfig):
    """&defaults section of globpea config namelist. See https://research.csiro.au/ccam/software-and-model-configuration/globpea-atmospheric-model/defaults-default-switch-values/"""

    nversion: Optional[str] = Field(
        default=None,
        description="Selects the version number in YYMM format of the required default switches. Defaults to the current version of CCAM.",
    )


class GlobpeaLeapMode(IntEnum):
    """Whether to use leap years or 365-day calendars."""

    NO_LEAP = 0
    LEAP = 1


# Unfortunately this enum isn't exhaustive - values of -1, -2900, and others are also valid
class GlobpeaPrecon(IntEnum):
    """Methods for solving the Helmholtz equation"""

    MULTI_GRID = -10000
    CONJUGATE_GRADIENT = 0
    SOR = -3900


class GlobpeaDynamics(IntEnum):
    """Allows for hydrostatic and non-hydrostatic dynamics."""

    HYDROSTATIC = 0
    NON_HYDROSTATIC = 5


class GlobpeaHorizontalDiffusion(IntEnum):
    """Method used for horizontal diffusion"""

    SMAGORINSKY = 0
    DEFORMATION = 1
    DEFORMATION2 = 2
    SMAG_TKE = 3


class GlobpeaHorizontalDiffusionTerms(IntEnum):
    """Controls horizontal diffusion for which terms"""

    T_QG_TKE_U_V = 0
    T_QG_TKE = -1
    U_V = -2
    QG = -3
    T_QG_CLOUD_TKE_AEROSOLS = -4
    T = -5
    T_QG = -6


class GlobpeaMassFixer(IntEnum):
    """Mass fixer algorithm to use (if any)."""

    OFF = 0
    SEA_LEVEL_PRESSURE = -1
    SURFACE_PRESSURE_1 = 1
    SURFACE_PRESSURE_2 = 2
    SURFACE_PRESSURE_4 = 3


class GlobpeaQGFix(IntEnum):
    """Correction for saturated air."""

    DISABLED = -1
    INTERNAL_CHECKS = 0
    REMOVE_NEGATIVE_MOISTURE = 1
    REMOVE_SATURATED_MOISTURE = 2


class GlobpeaFarFieldNudging(IntEnum):
    """Far-field nudging options."""

    OFF = 0
    FAR_FIELD = 1
    LINEARLY_INCREASING_PANEL_4 = -1
    QUADRATICALLY_INCREASING_PANEL_4 = -2
    FAR_FIELD_NO_PANEL_1 = -3
    FAR_FIELD_2_NO_PANEL_1 = -4
    FAR_FIELD_SOME_PANEL_1 = -5
    ONE_WAY_NESTING = -6
    FAR_FIELD_3_NO_PANEL_1 = -7
    FAR_FIELD_NO_PANEL_1_SEPARATE_DAVU = 3
    FAR_FIELD_2_NO_PANEL_1_SEPARATE_DAVU = 4
    FAR_FIELD_SOME_PANEL_1_SEPARATE_DAVU = 5
    ONE_WAY_NESTING_SEPARATE_DAVU = 6
    FAR_FIELD_3_NO_PANEL_1_SEPARATE_DAVU = 7


class GlobpeaEnsembleMode(IntEnum):
    """Ensemble mode."""

    OFF = 0
    CONTROL = 1
    BREEDING = 2


class GlobpeaNMLO(IntEnum):
    OFF = 0
    SINGLE_COLUMN = -1
    DYNAMICAL_OCEAN = -3


class GlobpeaLandSurfaceModel(IntEnum):
    ORIGINAL = 3
    MODIS = 5
    CABLE = 7


class GlobpeaUrbanCanopyModel(IntEnum):
    NO_URBAN = 0
    URBAN_SAVE_IN_RESTART_FILE = 1
    URBAN_SAVE_IN_HISTORY_AND_RESTART_FILES = -1


class GlobpeaCloudOverlapMode(IntEnum):
    RANDOM_OVERLAP = 0
    MAXIMUM_RANDOM_OVERLAP = 1
    MAXIMUM_RANDOM_OVERLAP_WITHOUT_BULK_CLOUD_PROPERTIES = 2


class GlobpeaRadiationModel(IntEnum):
    ORIGINAL = 4
    SEA_ESF = 5  # from GFDL AM3


class GlobpeaAerosolModel(IntEnum):
    NO_AEROSOL_EFFECTS = 0
    PRESCRIBED_SO4_BURDEN_AND_DIRECT_AEROSOL_EFFECTS = (
        1  # Typically used for CMIP3 experiments
    )
    PRESCRIBED_SO4_BURDEN_AND_DIRECT_AEROSOL_EFFECTS_ADDITIONAL_INFO_IN_HISTORY_FILE = (
        -1
    )
    PROGNOSTIC_AEROSOLS = 2  # Prognostic (single moment) aerosols based on CSIRO Mk3.6.  Includes direct and indirect effects and is typically used for CMIP5 experiments.
    PROGNOSTIC_AEROSOLS_ADDITIONAL_INFO_IN_HISTORY_FILE = -2
    PROGNOSTIC_AEROSOLS_PLUS_IN_RAIN = 3  # Same as for PROGNOSTIC_AEROSOLS but also includes aerosols in prognostic rain.  This option is currently experimental.
    PROGNOSTIC_AEROSOLS_PLUS_IN_RAIN_ADDITIONAL_INFO_IN_HISTORY_FILE = -3


class GlobpeaBoundaryLayerTurbulenceModel(IntEnum):
    LOCAL_RI = 3
    EDMF_WITH_KE_CLOSURE = 6
    JING = 7


class GlobpeaCounterGradientModel(IntEnum):
    OFF = 0
    DIAGNOSED = 6
    MASS_FLUX = 7


class GlobpeaProcessRateMode(IntEnum):
    OFF = 0
    MICROPHYSICS_DIAGNOSTICS = 2  # value 1 was commented out at time of writing


class GlobpeaOutputFilePrecision(IntEnum):
    SHORT = 0
    FLOAT = 1


class GlobpeaNamip(IntEnum):
    """Controls source of Sea Surface Temperatures (SSTs) and Sea-ice."""

    NO_INPUT_DATA = 0  # No input data
    PERSISTED_SST_ANOMALIES = -1  # Persisted SST anomalies
    PWCB_INTERPOLATE_SSTS_DIAGNOSE_SEA_ICE = (
        1  # Use PWCB intepolation for SSTs, diagnose sea-ice
    )
    LINEAR_INTERPOLATE_SSTS_AND_SEA_ICE = 2  # Use linear interpolation for SSTs and sea-ice (assumes pre-processing of monthly SSTs)
    PWCB_INTERPOLATE_SSTS_SEA_ICE_MONTHLY = (
        3  # Use PWCB interpolation for SSTs and sea-ice equals supplied monthly value
    )
    PWCB_INTERPOLATE_SSTS_AND_SEA_ICE = 4  # Use PWCB interpolation for SSTs and sea-ice
    PWCB_INTERPOLATE_SSTS_SEA_ICE_AND_SALINITY = (
        5  # Use PWCB interpolation for SSTs, sea-ice and salinity
    )
    JMC_INTERPOLATE_SSTS_DIAGNOSE_SEA_ICE = (
        11  # Use JMc interpolation for SSTs, diagnose sea-ice
    )
    JMC_INTERPOLATE_SSTS_SEA_ICE_MONTHLY = (
        13  # Use JMc interpolation for SSTs and sea-ice equals supplied monthly
    )
    JMC_INTERPOLATE_SSTS_AND_SEA_ICE = 14  # Use JMc interpolation for SSTs and sea-ice
    JMC_INTERPOLATE_SSTS_SEA_ICE_AND_SALINITY = (
        15  # Use JMc interpolation for SSTs, sea-ice and salinity
    )
    INTERPOLATE_SSTS_DIAGNOSE_SEA_ICE = (
        21  # Use approx linear AMIP interpolation for SSTs and diagnose sea-ice
    )
    INTERPOLATE_SSTS_AND_SEA_ICE = (
        24  # Use approx linear AMIP interpolation for SSTs and sea-ice
    )
    INTERPOLATE_SSTS_SEA_ICE_AND_SALINITY = (
        25  # Use approx linear AMIP interpolation for SSTs, sea-ice and salinity
    )


class GlobpeaHelmholtzMethod(IntEnum):
    """Versions of D'Azevedo method to use in solving the Helmholtz equation."""

    DAZEVEDO_1 = 0  # !
    DAZEVEDO_STANDARD = 1


def GlobpeaGridresRecommendedTimestep(
    gridres_km: float,
) -> int:  # pylint: disable=too-complex
    if gridres_km >= 60:
        return 900
    if gridres_km >= 45:
        return 720
    if gridres_km >= 36:
        return 600
    if gridres_km >= 30:
        return 360
    if gridres_km >= 18:
        return 300
    if gridres_km >= 15:
        return 240
    if gridres_km >= 12:
        return 180
    if gridres_km >= 9:
        return 120
    if gridres_km >= 6:
        return 90
    if gridres_km >= 5:
        return 80
    if gridres_km >= 4:
        return 60
    if gridres_km >= 3:
        return 40
    if gridres_km >= 1:
        return 20
    if gridres_km >= 0.5:
        return 10
    if gridres_km >= 0.2:
        return 4
    if gridres_km >= 0.1:
        return 2
    raise ValueError(f"Grid resolution of {gridres_km}km is too small.")


class GlobpeaNamelistConfigCardin(CCAMRootConfig):
    """&cardin section of globpea config namelist. See https://research.csiro.au/ccam/software-and-model-configuration/globpea-atmospheric-model/cardin-general-switches/"""

    # Date, run length and miscellaneous
    kdate_s: date = Field(
        description="Start date of simulation in YYYYMMDD format.",
    )

    @field_serializer("kdate_s")
    def serialize_kdate_s(self, dt: date) -> int:
        return int(dt.strftime("%Y%m%d"))

    ktime_s: time = Field(
        default=time(0, 0),
        description="Start time of simulation in ZZmm format.",
    )

    @field_serializer("ktime_s")
    def serialize_ktime_s(self, t: time) -> int:
        return int(t.strftime("%H%M"))

    leap: GlobpeaLeapMode = Field(
        default=GlobpeaLeapMode.LEAP,
        description="To use leap years (LEAP) or to use 365-day calendar (NO_LEAP).",
    )

    dt: float = Field(
        # These are the same constraints as enforced by globpea; see https://github.com/csiro/ccam-ccam/blob/b09005f35f53ddedb23f671beb64364143f65acb/main/general/config_m.f90#L412
        gt=0,
        le=3600,
        description="Simulation time-step in seconds. Call GlobpeaGridresRecommendedTimestep() with your simulation's resolution to get an appropriate value. Note that the recommended time-step is specified as a factor of 1 hour. See https://research.csiro.au/ccam/software-and-model-configuration/globpea-atmospheric-model/cardin-general-switches/dt/ for more details.",
    )
    # TODO: something should calculate this as (time.interval.total_seconds()) / dt
    nwt: Optional[int] = Field(
        default=None,
        gt=0,
        description="Standard output period in time-steps.",
    )

    @field_serializer("nwt", mode="plain")
    def serialize_nwt(self, nwt: Optional[int]) -> int:
        """Globpea treats the -99 value as meaning 24 hours, i.e. daily output."""
        return -99 if nwt is None else nwt

    tbave: Optional[int] = Field(
        default=None,
        gt=0,
        description="High-frequency output period in time-steps. Typically used for selected near surface variables (e.g., extreme rainfall).",
    )

    # TODO: further checking of tbave and ntau
    # TODO: somewhere calculate ntau in terms of run length and dt
    ntau: int = Field(
        description="Run length of simulation in time-steps.",
    )
    # TODO: check this description. Most usage seems to just test `nmaxpr==1`, except one which tests `nmaxpr<=ntau`
    nmaxpr: Optional[int] = Field(
        default=None,
        description="Period of output diagnostics in time-steps.",
    )
    newtop: Optional[int] = Field(
        default=None,
        ge=0,
        le=2,
        description="Adjust interpolated input data (e.g., nudging) for differences in orography (newtop=1).",
    )
    # TODO: define enum with valid values for this. The code doesn't match the documentation linked in the description, so for now it's unconstrained
    nrungcm: Optional[int] = Field(
        default=None,
        description="Default option for soil datasets. See https://research.csiro.au/ccam/software-and-model-configuration/globpea-atmospheric-model/cardin-general-switches/nrungcm/ for more details.",
    )
    namip: Optional[GlobpeaNamip] = Field(
        default=None,
        description="Controls source of Sea Surface Temperatures and Sea-ice. See https://research.csiro.au/ccam/software-and-model-configuration/globpea-atmospheric-model/cardin-general-switches/namip/ for more details.",
    )
    rescrn: Optional[Flag] = Field(
        default=None,
        description="Recomputes near-surface diagnostics for consistency in output (rescrn=1).",
    )

    # Parallel computing

    maxtilesize: Optional[int] = Field(
        default=None,
        description="Controls vector length for physics routines. Can lead to speed improvements when optimized for the host computer.",
    )

    async_length: Optional[int] = Field(
        default=None,
        description="Controls number of asynchronous streams for computing on GPUs.",
    )

    nagg: Optional[int] = Field(
        default=None,
        description="Controls the maximum number of tracers sent in a single MPI message.",
    )

    # Dynamical core

    helmmeth: Optional[GlobpeaHelmholtzMethod] = Field(
        default=None,
        description="Which version of D'Azevedo Method to use in solving the Helmholtz equation.",
    )
    # TODO: use GlobpeaPrecon (see comment there)?
    precon: Optional[int] = Field(
        default=None,
        le=0,
        description="Controls the method used to solve the Helmholtz equation (precon=-10000 for multi-grid, precon=0 for conjugate-gradient and precon=-3900 is for SOR).",
    )
    restol: Optional[float] = Field(
        default=None,
        description="Tolerance of the iterative solution for the Helmholtz equation.",
    )
    nh: Optional[GlobpeaDynamics] = Field(
        default=None,
        description="Allows for hydrostatic (nh=0) and non-hydrostatic (nh=5) dynamics.",
    )
    # TODO: can we constrain knh to >= 0? It looks like ccam allows -ve values, e.g. see https://github.com/csiro/ccam-ccam/blob/4c12a38bc2adbae976135f6387f8ca9b5068cfa6/dynamic/atmosphere/adjust5.f90#L322
    knh: Optional[int] = Field(
        default=None,
        description="Delays the use of the non-hydrostatic dynamics for the specified number of time-steps. Has no effect if the initial conditions are a CCAM restart file. Effectively knh only works after interpolating initial conditions from a lower resolution.",
    )
    epsp: Optional[float] = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="Off-centring term for pressure where epsp=-1 is fully explicit, epsp=0 is half explicit and half implicit, whereas epsp=1 is fully implicit.",
    )
    epsu: Optional[float] = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="Off-centring term for momentum where epsu=-1 is fully explicit, epsu=0 is half explicit and half implicit, whereas epsu=1 is fully implicit.",
    )
    epsh: Optional[float] = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="Off-centring term for non-hydrostatic equation where epsh=-1 is fully explicit, epsh=0 is half explicit and half implicit, whereas epsh=1 is fully implicit.",
    )
    # TODO: epsf?
    nstagu: Optional[int] = Field(
        default=None,
        description="Controls period of switching direction for reversible staggering.",
    )
    khor: Optional[int] = Field(
        default=None,
        description="Controls strength of horizontal diffusion at different vertical levels.",
    )
    mh_bs: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    nhorjlm: Optional[GlobpeaHorizontalDiffusion] = Field(
        default=None,
        description="Method used for horizontal diffusion (nhorjlm=0 for Smagorinsky, nhorjlm=1 for deformation, nhorjlm=3 for Smag+TKE).",
    )
    nhorps: Optional[GlobpeaHorizontalDiffusionTerms] = Field(
        default=None,
        description="Controls horizontal diffusion for which terms.",
    )
    always_mspeca: Optional[bool] = Field(
        default=None,
        description="Forces CCAM to recalculate dynamics and radiation variables on the first time-step instead of using data from the restart file.",
    )

    # Mass fixer

    mfix: Optional[GlobpeaMassFixer] = Field(
        default=None,
        description="Turns mass fixer on (mfix=1) or off (mfix=0) to conserve surface pressure.",
    )
    mfix_qg: Optional[Flag] = Field(
        default=None,
        description="Turns moisture fixer on or off to conserve moisture fields (i.e., qv, ql, qf, qs, qg).",
    )
    mfix_aero: Optional[Flag] = Field(
        default=None,
        description="Turns aerosol mass fixed on or off to conserve aerosol fields.",
    )
    qg_fix: Optional[GlobpeaQGFix] = Field(
        default=None,
        description="Correction for saturated air.",
    )

    # Nudging

    nbd: Optional[GlobpeaFarFieldNudging] = Field(
        default=None,
        description="Far-field nudging options (nbd=-3). Spectral filter (mbd) is now the preferred option.",
    )
    mbd: Optional[int] = Field(
        default=None,
        ge=0,
        description="Spectral filter. mbd=20 is the nudging for the length of the front panel. mbd=40 is half the size of the front panel, etc. Possibly overwritten by mbd_maxscale or mbd_maxgrid.",
    )
    mbd_maxscale: Optional[int] = Field(
        default=None,
        gt=0,  # Must be >0 when mbd is not 0
        description="Overrides mbd to limit the maximum length in kilometres. Default value set to 3000 km.",
    )
    mbd_maxgrid: Optional[int] = Field(
        default=None,
        gt=0,  # Must be >0 when mbd is not 0
        description="Overrides mbd to limit the maximum length in grid points, instead of width of the front panel.",
    )
    mbd_mlo: Optional[int] = Field(
        default=None,
        ge=0,
        description="Spectral filter. The same as mbd but applied to the ocean model. mbd_mlo=20 is the nudging for the length of the front panel. mbd_mlo=40 is half the size of the front panel, etc. Possibly overwritten by mbd_maxscale_mlo or mbd_maxgrid_mlo.",
    )
    mbd_maxscale_mlo: Optional[int] = Field(
        default=None,
        gt=0,  # Must be >0 when mbd_mlo is not 0
        description="Same as mbd_maxscale, but applied to the ocean model.",
    )
    mbd_maxgrid_mlo: Optional[int] = Field(
        default=None,
        gt=0,  # Must be >0 when mbd_mlo is not 0
        description="Same as mbd_maxgrid, but applied to the ocean model.",
    )
    # TODO: is this still used as described? see ccam-ccam/main/file/nesting.f90
    mloalpha: Optional[int] = Field(
        default=None,
        description="Nudging strength for the ocean model. mloalpha=10 is full strength, mloalpha=20 is half strength, etc.",
    )
    nud_p: Optional[Flag] = Field(
        default=None,
        description="Turn on or off nudging for surface pressure.",
    )
    nud_t: Optional[Flag] = Field(
        default=None,
        description="Turn on or off nudging for air temperture.",
    )
    nud_q: Optional[Flag] = Field(
        default=None,
        description="Turn on or off nudging for water vapor.",
    )
    nud_uv: Optional[Flag] = Field(
        default=None,
        description="Turn on or off nudging for winds.",
    )
    nud_aero: Optional[Flag] = Field(
        default=None,
        description="Turn on or off nudging for aerosols.",
    )
    nud_sst: Optional[Flag] = Field(
        default=None,
        description="Turn on or off nudging for ocean potential temperature.",
    )
    nud_sss: Optional[Flag] = Field(
        default=None,
        description="Turn on or off nudging for ocean salinity.",
    )
    nud_ouv: Optional[Flag] = Field(
        default=None,
        description="Turn on or off nudging for ocean currents.",
    )
    nud_sfh: Optional[Flag] = Field(
        default=None,
        description="Turn on or off nudging for ocean surface height.",
    )
    # TODO
    nud_hrs: Optional[int] = Field(
        default=None,
        description="E-folding time for far-field nudging.",
    )
    # TODO
    nud_period: Optional[int] = Field(
        default=None,
        description="Limits the period (in mins) to nudge the atmosphere or ocean with the scale-selective filter. Actual nudging period is the minimum of nud_period and the period of data in the host model.",
    )
    # TODO
    kbotdav: Optional[int] = Field(
        default=None,
        description="Lowest level for atmosphere nudging. -ve value specifies a pressure level with -1000 for 1000 hPa, etc.",
    )
    # TODO
    ktopdav: Optional[int] = Field(
        default=None,
        description="Highest level for atmosphere nudging. -ve value specifies a pressure level with -1 for 1 hPa, etc.",
    )
    # TODO
    ktopmlo: Optional[int] = Field(
        default=None,
        description="Highest level for ocean nudging. -ve value specifies a depth in sigma values with -1 being 0.001 sigma level.",
    )
    # TODO
    kbotmlo: Optional[int] = Field(
        default=None,
        description="Lowest level for ocean nudging. -ve value specifies a depth in sigma values with -1000 being 1 sigma level.",
    )
    # TODO
    sigramplow: Optional[float] = Field(
        default=None,
        description="Linear ramp rate to grow atmospheric nudging in sigma levels from kbotdav.",
    )
    # TODO
    sigramphigh: Optional[float] = Field(
        default=None,
        description="Linear ramp rate to grow atmospheric nudging in sigma levels from ktopdav.",
    )

    # Ensemble

    # TODO
    ensemble_mode: Optional[GlobpeaEnsembleMode] = Field(
        default=None,
        description="Mode for CCAM ensemble",
    )
    ensemble_period: Optional[int] = Field(
        default=None,
        description="Update period for ensemble members (mins). Default value is 720 mins.",
    )
    ensemble_rsfactor: Optional[float] = Field(
        default=None,
        description="Scale factor for ensemble perturbation. 1.=no-scaling. Default value is 0.1.",
    )

    # Oceans, lakes and rivers

    nmlo: Optional[GlobpeaNMLO] = Field(
        default=None,
        description="Options for ocean model.",
    )
    ol: Optional[int] = Field(
        default=None,
        description="Number of vertical levels for the ocean model.",
    )
    tss_sh: Optional[float] = Field(
        default=None,
        description="Sea Surface Temperature skin temperature enhancement factor.",
    )
    nriver: Optional[Flag] = Field(
        default=None,
        description="Turns on or off the river routing model.",
    )

    # Land, urban and carbon

    nsib: Optional[GlobpeaLandSurfaceModel] = Field(
        default=None,
        description="Selects the land-surface model.",
    )
    nurban: Optional[GlobpeaUrbanCanopyModel] = Field(
        default=None,
        description="Turns on or off the urban canopy model (aTEB).",
    )
    vmodmin: Optional[float] = Field(
        default=None,
        description="Minimum wind speed for calculating surface fluxes in m/s.",
    )
    # TODO
    nsigmf: Optional[int] = Field(
        default=None,
        description="Modifies soil behaviour with nsib=GlobpeaLandSurfaceModel.ORIGINAL or nsib=GlobpeaLandSurfaceModel.MODIS to essentially increase the heat capacity. Not recommended for GlobpeaRadiationModel=SEA_ESF.",
    )
    qgmin: Optional[float] = Field(
        default=None,
        description="Minimum water vapour mixing ratio.",
    )
    nmr: Optional[GlobpeaCloudOverlapMode] = Field(
        default=None,
        description="Cloud overlap mode.",
    )
    jalbfix: Optional[Flag] = Field(
        default=None,
        description="Modifies albedo with nsib=GlobpeaLandSurfaceModel.ORIGINAL or nsib=GlobpeaLandSurfaceModel.MODIS to increase the albedo over sandy soils. Not recommended for GlobpeaRadiationModel=SEA_ESF.",
    )

    # Radiation and aerosols

    nrad: Optional[GlobpeaRadiationModel] = Field(
        default=None,
        description="Radiation model.",
    )
    iaero: Optional[GlobpeaAerosolModel] = Field(
        default=None,
        description="Specifies aerosol model.",
    )
    process_rate_mode: Optional[GlobpeaProcessRateMode] = Field(
        default=None,
        description="Include additional cloud microphysics output.",
    )
    ch_dust: Optional[float] = Field(
        default=None,
        description="Transfer coefficient for natural sources of emissions, in kg*s2/m5.",
    )

    # Boundary layer turbulent mixing

    nvmix: Optional[GlobpeaBoundaryLayerTurbulenceModel] = Field(
        default=None,
        description="Boundary layer turbulence model.",
    )

    @model_validator(mode="after")
    def check_nvmix_edmf_if_max_flux(self) -> Self:
        if (
            self.nlocal == GlobpeaCounterGradientModel.MASS_FLUX
            and self.nvmix
            is not GlobpeaBoundaryLayerTurbulenceModel.EDMF_WITH_KE_CLOSURE
        ):
            raise ValueError(
                "nvmix must be EDMF_WITH_KE_CLOSURE if nlocal is MASS_FLUX"
            )
        return self

    nlocal: Optional[GlobpeaCounterGradientModel] = Field(
        default=None,
        description="Counter gradient model with nlocal=0 for off, nlocal=6 for diagnosed and nlocal=7 (with nvmix=EDMF_WITH_KE_CLOSURE) for mass-flux.",
    )

    # Station output

    # TODO
    mstn: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    nstn: Optional[int] = Field(
        default=None,
        description="Number of output stations.",
    )
    slon: Optional[list[float]] = Field(
        default=None,
        description="List of longitudes for station output.",
    )
    slat: Optional[list[float]] = Field(
        default=None,
        description="List of latitudes for station output.",
    )

    # File input/output

    localhist: Optional[bool] = Field(
        default=None,
        description="Allows CCAM to write output in parallel. localhist=True can lead to significant speed improvements for higher numbers of CPUs.",
    )
    unlimitedhist: Optional[bool] = Field(
        default=None,
        description="Use unlimited dimension for output file with unlimitedhist=True There can be some speed advantages for using unlimitedhist=False although visualizing the data can be difficult.",
    )
    synchist: Optional[bool] = Field(
        default=None,
        description="Flush output buffers after writing data with synchist=True, which can be useful for debugging.",
    )

    @model_validator(mode="after")
    def check_compression_range(self) -> Self:
        if self.compression is not None and (
            self.compression < 0 or self.compression > 9
        ):
            return ValueError("compression must be in the range [0-9]")
        return self

    compression: Optional[int] = Field(
        default=None,
        description="Compression level for output from 0 (no compression) to 9 (high compression). compression=1 is recommended.",
    )
    hp_output: Optional[GlobpeaOutputFilePrecision] = Field(
        default=None,
        description="Output file precision. Using hp_output=GlobpeaOutputFilePrecision.SHORT for short precision can halve the file size.",
    )
    pil_single: Optional[int] = Field(
        default=None,
        description="Size to subdivide input host data for parallel processing.",
    )
    chunk_time: Optional[int] = Field(
        default=None,
        description="Number of time-steps to include in a chunk for 2D output variables.",
    )


class GlobpeaNamelistConfigSkyin(CCAMRootConfig):
    """&skyin section of globpea config namelist. Options to modify the behaviour of radiation and aerosols."""

    # Radiation

    # TODO: set correct data types, defaults etc.

    mins_rad: Optional[int] = Field(
        default=None,
        description="Period to update radiation in mins.  Setting mins_rad=-1 will automatically select a value based on the grid resolution.",
    )
    # TODO
    qgmin: Optional[float] = Field(
        default=None,
        description="Minimum value of water vapor mixing ratio.",
    )
    # TODO
    sw_resolution: Optional[int] = Field(
        default=None,
        description="Selects number of radiation bands with sw_resolution=’high’ or sw_resolution=’low’.",
    )
    # TODO
    sw_diff_streams: Optional[int] = Field(
        default=None,
        description="Number of streams for diffuse radiation with 1 or 4 as valid options.",
    )
    # TODO
    liqradmethod: Optional[int] = Field(
        default=None,
        description="Method for calculating effective water droplet radius.  Currently the only valid option is 0 for Martin et al 1994.",
    )
    # TODO
    iceradmethod: Optional[int] = Field(
        default=None,
        description="Method for calculating effective ice droplet radius.  iceradmethod=0 for Lohmann et al 1999, iceradmethod=1 for Donner et al 1997, iceradmethod=2 for Fu 2007.",
    )
    # TODO
    bpyear: Optional[int] = Field(
        default=None,
        description="Modifies orbital parameters for paleoclimate simulations.  Valid options are 0, 6000 and 21000 years before present.",
    )

    # Aerosols

    # TODO: set correct data types, defaults etc.

    # TODO
    ch_dust: Optional[int] = Field(
        default=None,
        description="Scale factor for dust emission model.",
    )
    # TODO
    zvolcemi: Optional[int] = Field(
        default=None,
        description="Scale factor for volcanic emission model.",
    )
    # TODO
    so4radmethod: Optional[int] = Field(
        default=None,
        description="Turns on (so4radmethod=0) and off (so4radmethod=-1) SO4 aerosol direct effects.",
    )
    # TODO
    carbonradmethod: Optional[int] = Field(
        default=None,
        description="Turns on (carbonradmethod=0) and off (carbonradmethod=-1) carbonaceous aerosol direct effects.",
    )
    # TODO
    dustradmethod: Optional[int] = Field(
        default=None,
        description="Turns on (dustradmethod=0) and off (dustradmethod=-1) dust aerosol direct effects.",
    )
    # TODO
    seasaltradmethod: Optional[int] = Field(
        default=None,
        description="Turns on (seasaltradmethod=0) and off (seasaltradmethod=-1) sea-salt aerosol direct effects.",
    )
    # TODO
    aeroindir: Optional[int] = Field(
        default=None,
        description="Controls aerosol indirect effects with aeroindir=0 for SO4+Carb+Salt, aeroindir=1 for SO4 and aeroindir=2 for off.",
    )
    # TODO
    so4mtn: Optional[int] = Field(
        default=None,
        description="Mass to number conversion for SO4.  Modifies indirect effects.",
    )
    # TODO
    carbmtn: Optional[int] = Field(
        default=None,
        description="Mass to number conversion for carbonaceous aerosols.  Modifies indirect effects.",
    )
    # TODO
    saltsmallmtn: Optional[int] = Field(
        default=None,
        description="Mass to number conversion for sea-salt film mode.  Modifies direct effects.",
    )
    # TODO
    saltlagemtn: Optional[int] = Field(
        default=None,
        description="Mass to number conversion for sea-salt jet mode.  Modifies direct effects.",
    )


class GlobpeaNamelistConfigDatafile(CCAMRootConfig):
    """&datafile section of globpea config namelist. Specify input and output filenames."""

    # Initial conditions and output

    ifile: Annotated[
        Path,
        Field(
            description="Initial conditions in conformal cubic format.  Missing data can be diagnosed under some circumstances (e.g., soil temperatures).",
        ),
        Input,
    ]
    surf_00: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Optional input to replace soil data in conformal cubic format (overwrites soil data from ifile).  Typically used in NWP applications to use soil data from previous forecast.",
        ),
        Input,
    ]
    ofile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Output history file in conformal cubic format.  Can be used as a restart file, although data is compressed.",
        ),
        Output,
    ]
    restfile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Output restart file in conformal cubic format.  Saves model prognostic variables without compression for a subsequent restart.  Typically used at the end of each simulation month.",
        ),
        Output,
    ]
    surfile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="High frequency output file in conformal cubic format.  Saves model output for uas, vas, tas, ps, rnd and rnc.  Typically used to save model output every time-step.",
        ),
        Output,
    ]
    save_aerosols: Optional[bool] = Field(
        default=None,
        description="True to save various aerosol values.",
    )
    save_pbl: Optional[bool] = Field(
        default=None,
        description="True to save pbl information.",
    )
    save_cloud: Optional[bool] = Field(
        default=None,
        description="True to save cloud information (lo,mid,hi, …).",
    )
    save_land: Optional[bool] = Field(
        default=None,
        description="True to save information about land surface.",
    )
    save_maxmin: Optional[bool] = Field(
        default=None,
        description="True to save daily maximum/minimum values (such as tas, rnd24).",
    )
    save_ocean: Optional[bool] = Field(
        default=None,
        description="True to save ocean information.",
    )
    save_radiation: Optional[bool] = Field(
        default=None,
        description="True to save radiation parameters.",
    )
    save_urban: Optional[bool] = Field(
        default=None,
        description="True to save urban scheme values.",
    )
    save_carbon: Optional[bool] = Field(
        default=None,
        description="True to save parameters related to the land surface carbon scheme.",
    )
    save_river: Optional[bool] = Field(
        default=None,
        description="True to save river flow information.",
    )

    # Nudging and Sea Surface Temperature data

    mesonest: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Host dataset for nudging in conformal cubic format.",
        ),
        Input,
    ]
    sstfile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Monthly Sea Surface Temperature and Sea Ice.  Typically used for AMIP style experiments.",
        ),
        Input,
    ]

    # Vertical level data

    eigenv: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Specifies vertical levels.  CCAM recomputes eigenvectors are run-time.",
        ),
        Input,
    ]

    # Topography files

    topofile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Specifies surface geopotential height, land-sea mask and standard deviation of sub-grid orography heights.",
        ),
        Input,
    ]
    vegprev: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Optional input for specifying vegetation data for the previous month into the past for interpolation.",
        ),
        Input,
    ]
    vegfile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Specified vegetation data for the current month, including vegetation type, Leaf Area Index, soil texture, albedo, urban fraction and urban type.  Also optionally includes Plant Functional Type configuration data and urban category configuration data.",
        ),
        Input,
    ]
    vegnext: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Optional input for specifying vegetation data for the next month into the future for interpolation.",
        ),
        Input,
    ]
    vegnext2: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Optional input for specifying vegetation data for the next two months into the future for interpolation.",
        ),
        Input,
    ]
    bathfile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Optional input for specifying bathymetry and river routing data.",
        ),
        Input,
    ]

    # Radiation files

    radfile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Specifies greenhouse gas concentrations.",
        ),
        Input,
    ]
    o3file: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Specifies ozone concentrations.",
        ),
        Input,
    ]
    cnsdir: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Specifies location of radiation datafiles.",
        ),
        Input,
    ]

    # Aerosol files

    so4tfile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="For prognostic aerosols (iaero=2 or iaero=-2), specifies the aerosol emission data.  For prescribed aerosols (iaero=1), specifies the SO4 burden.",
        ),
        Input,
    ]
    oxidantfile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Specifies oxidant concentrations for the prognostic aerosol scheme.",
        ),
        Input,
    ]

    # Carbon cycle files

    casafile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Emission data for the carbon cycle model.",
        ),
        Input,
    ]
    phenfile: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Specifies plant phenology data for the CASA carbon cycle model.",
        ),
        Input,
    ]


class GlobpeaNamelistConfigKuo(CCAMRootConfig):
    """&kuonml section of globpea config namelist. Options to modify convection and cloud microphysics."""

    # Convection
    # TODO: set correct data types, defaults etc.

    # TODO
    nkuo: Optional[int] = Field(
        default=None,
        description="specifies the convection model.",
    )

    # Cloud microphysics
    # TODO: set correct data types, defaults etc.

    # TODO
    ncloud: Optional[int] = Field(
        default=None,
        description="specifies the model used for cloud microphysics.  Further details can be obtained from https://research.csiro.au/ccam/software-and-model-configuration/globpea-atmospheric-model/kuonml-convection-and-cloud-microphysics/ncloud/.",
    )
    # TODO
    ldr: Optional[int] = Field(
        default=None,
        description="1,2,3,4,5,11,22,33,55 for different snow fall speed.",
    )

    sig_ct: Optional[float] = Field(
        default=None,
        description="TODO",
    )
    rhcv: Optional[float] = Field(
        default=None,
        description="TODO",
    )
    rhmois: Optional[float] = Field(
        default=None,
        description="TODO",
    )
    convfact: Optional[float] = Field(
        default=None,
        description="TODO",
    )
    convtime: Optional[float] = Field(
        default=None,
        description="TODO",
    )
    alflnd: Optional[float] = Field(
        default=None,
        description="TODO",
    )
    alfsea: Optional[float] = Field(
        default=None,
        description="TODO",
    )
    fldown: Optional[float] = Field(
        default=None,
        description="TODO",
    )
    iterconv: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    ncvcloud: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    nevapcc: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    nuvconv: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    mbase: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    mdelay: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    methprec: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    nbase: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    detrain: Optional[float] = Field(
        default=None,
        description="TODO",
    )
    entrain: Optional[float] = Field(
        default=None,
        description="TODO",
    )
    methdetr: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    detrainx: Optional[float] = Field(
        default=None,
        description="TODO",
    )
    dsig2: Optional[float] = Field(
        default=None,
        description="TODO",
    )
    dsig4: Optional[float] = Field(
        default=None,
        description="TODO",
    )
    ksc: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    kscsea: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    sigkscb: Optional[float] = Field(
        default=None,
        description="TODO",
    )
    sigksct: Optional[float] = Field(
        default=None,
        description="TODO",
    )
    tied_con: Optional[float] = Field(
        default=None,
        description="TODO",
    )
    tied_over: Optional[float] = Field(
        default=None,
        description="TODO",
    )
    nclddia: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    nstab_cld: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    nrhcrit: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    sigcll: Optional[float] = Field(
        default=None,
        description="TODO",
    )
    nevapls: Optional[int] = Field(
        default=None,
        description="TODO",
    )
    acon: Optional[float] = Field(
        default=None,
        description="TODO",
    )
    bcon: Optional[float] = Field(
        default=None,
        description="TODO",
    )


class GlobpeaNamelistConfigTurb(CCAMRootConfig):
    """&turbnml section of globpea config namelist. Options to modify boundary layer turbulent mixing and gravity wave drag."""

    # Gravity wave drag
    ngwd: Optional[int] = Field(
        default=None,
        description="Coefficient to limit launching height.",
    )
    helim: Optional[float] = Field(
        default=None,
        description="Maximum launching height.",
    )
    fc2: Optional[float] = Field(
        default=None,
        description="Coefficient for calculating Froude number.",
    )
    sigbot_gwd: Optional[float] = Field(
        default=None,
        description="Lowest sigma level for gravity wave drag.",
    )
    alphaj: Optional[float] = Field(
        default=None,
        description="Coefficient for Chouinard et al model.",
    )

    # Boundary layer eddy diffusivity

    # TODO
    buoymeth: Optional[int] = Field(
        default=None,
        description="Method used for calculating buoyancy.  buoymeth=0 for Durran and Klempt 1982, buoymeth=1 for Marquet and Geleyn 2012, buoymeth=2 for dry convection.",
    )
    # TODO
    stabmeth: Optional[int] = Field(
        default=None,
        description="– Method for calculating stability.  stabmeth=0 for Beljarrs and Holtslag 1991.  stabmeth=1 for Luhar correction.",
    )
    # TODO
    cm0: Optional[int] = Field(
        default=None,
        description="ce0, ce1, ce2, ce3 – Coefficients for k-e turbulence closure model.",
    )
    # TODO
    cq: Optional[int] = Field(
        default=None,
        description="Mixing enhancement to compensate for the absence of a counter gradient term.",
    )
    # TODO
    maxdts: Optional[int] = Field(
        default=None,
        description="Maximum time-step for the k-e model.",
    )
    mintke: Optional[float] = Field(
        default=None,
        description="Minimum value of turbulent kinetic energy.",
    )
    mineps: Optional[float] = Field(
        default=None,
        description="Minimum value of eddy dissipation.",
    )
    minl: Optional[float] = Field(
        default=None,
        description="Minimum length scale.",
    )
    maxl: Optional[float] = Field(
        default=None,
        description="Maximum length scale",
    )

    # Boundary layer mass flux
    # TODO: set correct data types, defaults etc.

    # TODO
    be: Optional[int] = Field(
        default=None,
        description="Coefficient for surface boundary condition .",
    )
    ent0: Optional[float] = Field(
        default=None,
        description="Constant to define the entrainment parameterisation.",
    )
    ent1: Optional[float] = Field(
        default=None,
        description="Constant to define the entrainment parameterisation.",
    )
    # TODO
    entc0: Optional[int] = Field(
        default=None,
        description="dtrc0 – Entrainment and detrainment rates for saturated air.",
    )
    m0: Optional[float] = Field(
        default=None,
        description="Mass flux amplitude constant.",
    )
    b1: Optional[float] = Field(
        default=None,
        description="Updraft entrainment and buoyancy coefficient, along with b2.",
    )
    b2: Optional[float] = Field(
        default=None,
        description="Updraft entrainment and buoyancy coefficient, along with b1.",
    )
    qcmf: Optional[float] = Field(
        default=None,
        description="Critical mixing ratio for liquid water before autoconversion.",
    )


class GlobpeaNamelistConfigLand(CCAMRootConfig):
    """&landnml section of globpea config namelist. Options to modify land-surface, urban and carbon cycle."""

    # TODO: set correct data types, defaults etc.
    # TODO
    proglai: Optional[int] = Field(
        default=None,
        description="Method for calculation LAI.  proglai=-1 for piece-wise linear interpolation (requires 4 input months), proglai=0 for PWCB interpolation (requires 3 input months) and proglai=1 for prognostic LAI.",
    )
    # TODO
    ccycle: Optional[int] = Field(
        default=None,
        description="Carbon cycle model.  ccycle=0 for off and ccycle=3 for C-N-P cycle.",
    )


class GlobpeaNamelistConfigMlo(CCAMRootConfig):
    """&mlonml section of globpea config namelist. Options to modify oceans, lakes, rivers and sea-ice."""

    # Ocean dynamics
    # TODO: set correct data types, defaults etc.

    # TODO
    mlodiff: Optional[int] = Field(
        default=None,
        description="Modifies horizontal diffusion with mlodiff=0 for T,U,V&S and mlodiff=1 for T&S.",
    )
    # TODO
    ocnsmag: Optional[int] = Field(
        default=None,
        description="Coefficient for Smagorinsky closure.",
    )
    # TODO
    ocneps: Optional[int] = Field(
        default=None,
        description="Off-centring term for ocean dynamics (-1 is fully explicit, 0 is half explicit and half implicit and 1 is fully implicit).",
    )
    # TODO
    usetide: Optional[int] = Field(
        default=None,
        description="Include tidal forcing with usetide=0 for off and usetide=1 for on.",
    )
    # TODO
    zomode: Optional[int] = Field(
        default=None,
        description="Roughness length calculation over water with 0=Charnock and 2=Beljaars.",
    )
    # TODO
    zoseaice: Optional[int] = Field(
        default=None,
        description="Roughness length for sea-ice in meters.",
    )
    # TODO
    factchseaice: Optional[int] = Field(
        default=None,
        description="Ratio of roughness length between momentum and heat for sea-ice.",
    )
    # TODO
    minwater: Optional[int] = Field(
        default=None,
        description="Minimum amount of water allowed in the column.",
    )
    # TODO
    mxd: Optional[int] = Field(
        default=None,
        description="Maximum depth of the water column.",
    )
    # TODO
    mindep: Optional[int] = Field(
        default=None,
        description="Maximum depth of the first model level.",
    )
    # TODO
    mlofix: Optional[int] = Field(
        default=None,
        description="Conservation method.",
    )

    # River routing
    # TODO: set correct data types, defaults etc.

    # TODO
    rivermd: Optional[int] = Field(
        default=None,
        description="River routing method (rivermd=0 for Miller and rivermd=1 for Manning).",
    )
    # TODO
    basinmd: Optional[int] = Field(
        default=None,
        description="River routing method for inland depressions (basinmd=0 for drain into soil).",
    )
    # TODO
    rivercoeff: Optional[int] = Field(
        default=None,
        description="River routing roughness coefficient.",
    )


class GlobpeaNamelistConfigTrfiles(CCAMRootConfig):
    """&trfiles section of globpea config namelist. Options for specifying user-defined tracers."""

    tracerlist: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Input tracer configuration file. See https://research.csiro.au/ccam/software-and-model-configuration/globpea-atmospheric-model/trfiles-tracers/tracerlist/ for more details.",
        ),
        Input,
    ]


class GlobpeaNamelistConfig(CCAMNamelistConfig):
    """Configuration for the globpea executable's configuration namelist."""

    # Set the default of nml_path, inherited from CCAMNamelistConfig, to 'input', which is globpea's default
    nml_path: Path = Field(
        default=Path("input"),
        description="Path to the namelist file to be read by globpea",
    )

    defaults: GlobpeaNamelistConfigDefaults = Field(
        default_factory=GlobpeaNamelistConfigDefaults,
        description="defaults section of the globpea namelist",
    )
    cardin: GlobpeaNamelistConfigCardin = Field(
        description="cardin section of the globpea namelist",
    )
    skyin: GlobpeaNamelistConfigSkyin = Field(
        default_factory=GlobpeaNamelistConfigSkyin,
        description="skyin section of the globpea namelist",
    )
    datafile: GlobpeaNamelistConfigDatafile = Field(
        default_factory=GlobpeaNamelistConfigDatafile,
        description="datafile section of the globpea namelist",
    )
    kuonml: GlobpeaNamelistConfigKuo = Field(
        default_factory=GlobpeaNamelistConfigKuo,
        description="kuonml section of the globpea namelist",
    )
    turbnml: Optional[GlobpeaNamelistConfigTurb] = Field(
        default=None,
        description="turbnml section of the globpea namelist",
    )
    landnml: Optional[GlobpeaNamelistConfigLand] = Field(
        default=None,
        description="landnml section of the globpea namelist",
    )
    mlonml: Optional[GlobpeaNamelistConfigMlo] = Field(
        default=None,
        description="mlonml section of the globpea namelist",
    )
    trfiles: Optional[GlobpeaNamelistConfigTrfiles] = Field(
        default=None,
        description="trfiles section of the globpea namelist",
    )


class GlobpeaConfig(CCAMExeConfig):
    """Configuration for the globpea executable, the main CCAM model.
    Global Prognostic Equations version A"""

    model_type: Literal["globpea"] = "globpea"

    workflow_step_description: Optional[str] = Field(
        default="Run the CCAM model",
    )

    input: GlobpeaNamelistConfig = Field(
        default_factory=GlobpeaNamelistConfig,
        description="globpea configuration as a namelist",
    )

    def __call__(
        self, runtime
    ):  # runtime is a ModelRun, which can't be imported due to circular dependency
        self.input.write_nml_file(Path(runtime.staging_dir))

    def bash_invocation(self) -> str:
        # The default is to read from 'input', so don't specify it on the command-line if this is the case
        args = f'-c "{self.input.nml_path}"' if self.input.nml_path != "input" else ""
        return self.bash_prettify_invocation(f"run_mpi_cmd globpea {args}")
