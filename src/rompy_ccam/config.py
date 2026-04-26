"""CCAM Rompy config."""

import logging
from pathlib import Path
from typing import Literal
from pydantic import Field

# from rompy.model import ModelRun
from rompy_ccam.rompy_ccam import CCAMBaseConfig

# from rompy_ccam.grid import CCAMGrid

logger = logging.getLogger(__name__)

HERE = Path(__file__).parent

# The following are based on run_ccam, and may be useful

# class CCAMDMode(StrEnum):
#     """The downscaling method to use in the CCAM simulation (dmode)."""
#     DMODE_NUDGING_GCM = "nudging_gcm" # spectral nudging for non-native CCAM hosts (e.g., ERA-Interim)
#     DMODE_SST_ONLY = "sst_only" # for SST-only foring (e.g., AMIP)
#     DMODE_NUDGING_CCAM = "nudging_ccam" # for spectral nudging with CCAM hosts
#     DMODE_SST_6HOUR = "sst_6hour" # for SST-only foring with sub-daily data
#     DMODE_GENERATE_VEG = "generate_veg" # for processing vegetation files (e.g., pre-processing of vegetation data when land-use changes are included)
#     DMODE_POSTPROCESS = "postprocess" # for only post-processing
#     DMODE_NUDGING_GCM_WITH_SST = "nudging_gcm_with_sst" # for spectral nudging of the atmosphere with user-defined SSTs

# class CMIPMode(StrEnum):
#     """Versions of the Coupled Model Intercomparison Project framework."""
#     CMIP5: "cmip5"
#     CMIP6: "cmip6"

# dmode: Optional[CCAMDMode] = Field(
#     default=None,
#     description="The downscaling method to use (if any)",
# )

# cmip: CMIPMode = Field(
#     default=CMIP6,
#     description="Which version of the CMIP framework to follow.",
# )

# rcp: RCP = Field(
#     default=

# class CCAMModelLevels(IntEnum):
#     """Number of model levels in the CCAM simulation (mlev)."""
#     MLEV_27 = 27
#     MLEV_35 = 35
#     MLEV_54 = 54
#     MLEV_72 = 72
#     MLEV_108 = 108
#     MLEV_144 = 144

# DEFAULT_MLEV: CCAMModelLevels = CCAMModelLevels.MLEV_54

# mlev: CCAMModelLevels = Field(
#     default=GlobpeaConfig.DEFAULT_MLEV,
#     description="Number of model levels (27, 35, 54, 72, 108 or 144)"
# )


class CCAMConfig(CCAMBaseConfig):
    """CCAM config class."""

    model_type: Literal["ccam"] = Field(
        default="ccam",
        description="Model type discriminator",
    )

    # We don't need to add `template` as we inherit it from BaseConfig (via CCAMBaseConfig)

    # grid: CCAMGrid = Field(
    #   description="The global grid domain",
    # )

    def __call__(self, *args, **kwargs) -> dict:
        """Callable where data and config are interfaced and CMD is rendered."""
        # staging_dir = runtime.staging_dir
        # Do something
        # Can get TimeRange from runtime.period
        # ret = {"staging_dir": staging_dir}
        return {}
