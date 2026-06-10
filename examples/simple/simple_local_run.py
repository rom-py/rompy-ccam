#!/usr/bin/env python3
from datetime import datetime, timedelta
from pathlib import Path

from rompy.core.time import TimeRange
from rompy.model import ModelRun

from rompy_ccam import CCAMConfig
from rompy_ccam.ccam_workflow import CCAMInitialWorkflow
from rompy_ccam.ccam.globpea import (
    GlobpeaConfig,
    GlobpeaNamelistConfig,
    GlobpeaNamelistConfigCardin,
    GlobpeaGridresRecommendedTimestep,
    GlobpeaNamelistConfigDatafile,
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
    end = datetime(2026, 5, 30)
    centre_lon = 148.238
    centre_lat = -34.77
    interval: timedelta = 6  # 6-hourly time step
    times = TimeRange(start=start, end=end, interval=interval, include_end=False)
    run_time_seconds = int((end - start).total_seconds())
    resolution_km = 25.0
    count = 48
    dt = GlobpeaGridresRecommendedTimestep(resolution_km)

    terread = TerreadConfig(
        input=TerreadNamelistConfig(
            topnml=TerreadNamelistConfigTop(
                il=count,
                rlong0=centre_lon,
                rlat0=centre_lat,
                do1km=False,
                do250=False,
                filepath10km=Path(__file__).resolve().parent / "data",
            ),
        ),
    )

    igbpveg = IgbpvegConfig(
        input=IgbpvegNamelistConfig(
            vegnml=IgbpvegNamelistConfigVeg(
                # Set the input topofile to terread's output topofile
                topofile=terread.input.topnml.fileout,
                landtypeout=Path("veg.nc"),
            ),
        ),
    )

    cdfvidar = CdfvidarConfig(
        input=CdfvidarNamelistConfig(
            gnml=CdfvidarNamelistConfigG(
                # Set the input topofile to terread's output topofile
                zsfil=terread.input.topnml.fileout,
                t_file=Path("TODO"),
            ),
        ),
    )

    globpea = GlobpeaConfig(
        input=GlobpeaNamelistConfig(
            cardin=GlobpeaNamelistConfigCardin(
                kdate_s=start.date(),
                dt=dt,
                ntau=run_time_seconds / dt,
            ),
            datafile=GlobpeaNamelistConfigDatafile(
                # Set the input topofile to terread's output topofile
                topofile=terread.input.topnml.fileout,
                # Set the input vegetation file to igbpveg's output vegetation file
                vegfile=igbpveg.input.vegnml.landtypeout,
            ),
        ),
    )

    pcc2hist = Pcc2HistConfig()

    workflow = CCAMInitialWorkflow(
        terread=terread,
        igbpveg=igbpveg,
        cdfvidar=cdfvidar,
        globpea=globpea,
        pcc2hists=[pcc2hist],
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
    # timeout = 3600,  # 1 hour timeout
    # command = "srun -n 8 ~/ccaminstall/bin/globpea > prnew.ccam"
    # )
    # success = model.run(backend = local_config)

    # if not success:
    # logger.error("Model run failed")
    # return


if __name__ == "__main__":
    main()
