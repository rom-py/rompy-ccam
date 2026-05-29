from datetime import datetime, timedelta

from rompy.core.time import TimeRange
from rompy.model import ModelRun

from rompy_ccam import CCAMConfig, CCAMWorkflowSequence, DEFAULT_CCAM_INSTALL
from rompy_ccam.default_workflow import CCAMDefaultWorkflow
from rompy_ccam.ccam.globpea import (
    GlobpeaConfig,
    GlobpeaNamelistConfig,
    GlobpeaNamelistConfigCardin,
    GlobpeaLeapMode,
    GlobpeaGridresRecommendedTimestep,
    GlobpeaNamelistConfigTurb,
    GlobpeaNamelistConfigSkyin,
    GlobpeaNamelistConfigDatafile,
    GlobpeaNamelistConfigKuo,
)
from rompy_ccam.ccam.terread import (
    TerreadConfig,
    TerreadNamelistConfig,
    TerreadNamelistConfigTop,
)
from rompy_ccam.ccam.igbpveg import (
    IgbpvegNamelistConfigVeg,
    IgbpvegNamelistConfig,
    IgbpvegConfig,
    IgbpvegOutputMode,
)
from rompy_ccam.ccam.cdfvidar import (
    CdfvidarConfig,
    CdfvidarNamelistConfig,
    CdfvidarNamelistConfigG,
)
from rompy_ccam.ccam.pcc2hist import (
    Pcc2HistConfig,
    Pcc2HistNamelistConfigHistnl,
    Pcc2HistNamelistConfig,
    Pcc2HistNamelistConfigInput,
)


def main():
    """Run a simple workflow"""
    start = datetime(2026, 5, 29)
    end = datetime(2026, 6, 2)
    interval: timedelta = 1  # hourly time step
    times = TimeRange(start=start, end=end, interval=interval, include_end=False)
    run_time_seconds = int((end - start).total_seconds())
    resolution_km = 25.0
    dt = GlobpeaGridresRecommendedTimestep(resolution_km)

    terread = TerreadConfig()
    igbpveg = IgbpvegConfig()
    cdfvidar = CdfvidarConfig()

    globpea = GlobpeaConfig(
        input=GlobpeaNamelistConfig(
            cardin=GlobpeaNamelistConfigCardin(
                kdate_s=start.date(),
                dt=dt,
                ntau=run_time_seconds / dt,
            ),
        ),
    )
    pcc2hist = Pcc2HistConfig()

    workflow = CCAMDefaultWorkflow(
        terread=terread,
        igbpveg=igbpveg,
        cdfvidar=cdfvidar,
        globpea=globpea,
        pcc2hist=pcc2hist,
    )
    ccamConfig = CCAMConfig(workflow=workflow)

    # Create a model run
    generate_workspace = ModelRun(
        run_id="basic_workflow",
        period=times,
        output_dir="./output",
        delete_existing=True,
        config=ccamConfig,
    )

    # Create the workspace
    generate_workspace()

    # 1. Run with local backend using custom command
    # logger.info("Running model with local backend...")
    # local_config = LocalConfig(
    # timeout=3600,  # 1 hour timeout
    # command="srun -n 8 ~/ccaminstall/bin/globpea > prnew.ccam"
    # )
    # success = model.run(backend=local_config)

    # if not success:
    # logger.error("Model run failed")
    # return


if __name__ == "__main__":
    main()
