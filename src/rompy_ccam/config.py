"""CCAM Rompy config."""

import os
import logging
from pathlib import Path
from typing import Literal
from pydantic import Field

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
DEFAULT_CCAM_INSTALL: Path = Path("$HOME") / "ccaminstall"


class CCAMConfig(CCAMBaseConfig):
    """CCAM config class."""

    model_type: Literal["ccam"] = Field(
        default="ccam",
        description="Model type discriminator",
    )

    workflow: CCAMBaseConfig

    run_script: Path = Path("run.sh")

    default_nproc: int = Field(default=36)

    ccam_install: Path = Field(DEFAULT_CCAM_INSTALL)

    def generate_run_script(self) -> str:
        """Generate the run script to run this configuration after the workspace has been generated."""
        return f"""#!/usr/bin/env bash

# bash safe mode
set -euo pipefail

# show us what commands are being called
set -x

NPROC=${{MPIRUN_NPROC:-{self.default_nproc}}}
CCAM_INSTALL=${{CCAM_INSTALL:-"{self.ccam_install}"}}
CCAM_BIN="${{CCAM_INSTALL/bin}}"

PATH="${{CCAM_BIN}}:$PATH"

run_mpi_cmd() {{
    if [[ "$NPROC" -eq 1 ]]; then
        eval "$@"
    else
        eval "mpirun --oversubscribe -np $NPROC $@"
    fi
}}

# igbpveg and cdfvidar use OMP, so they run faster with these:
export OMP_NUM_THREADS=$NPROC
export OMP_STACKSIZE=1024m

# Execute in the directory in which this script is located
cd -- "$(dirname -- "${{BASH_SOURCE[0]}}")"

{self.workflow.bash_invocation()}
"""

    def write_run_script(self, staging_dir: Path) -> None:
        """Generate and write the run script to run this configuration after the workspace has been generated."""
        with open(staging_dir / self.run_script, "w") as f:
            f.write(self.generate_run_script())

        os.chmod(staging_dir / self.run_script, 0o755)

    def __call__(
        self, runtime
    ) -> dict:  # runtime is a ModelRun, which can't be imported due to circularity
        """Callable where data and config are interfaced and CMD is rendered."""
        self.workflow(runtime)

        self.write_run_script(Path(runtime.staging_dir))
        return self
