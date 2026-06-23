#!/usr/bin/env python3
from datetime import datetime, timedelta
from pathlib import Path

from rompy.core.time import TimeRange
from rompy.model import ModelRun

from rompy_ccam import CCAMConfig, Flag
from rompy_ccam.ccam_workflow import CCAMInitialWorkflow
from rompy_ccam.ccam.globpea import (
    GlobpeaConfig,
    GlobpeaDynamics,
    GlobpeaHorizontalDiffusion,
    GlobpeaMassFixer,
    GlobpeaNamelistConfigTurb,
    GlobpeaNamelistConfigLand,
    GlobpeaHorizontalDiffusionTerms,
    GlobpeaNamelistConfigSkyin,
    GlobpeaNamip,
    GlobpeaQGFix,
    GlobpeaNamelistConfig,
    GlobpeaNamelistConfigCardin,
    GlobpeaNamelistConfigKuo,
    GlobpeaGridresRecommendedTimestep,
    GlobpeaNamelistConfigDatafile,
    GlobpeaLineCatalogForm,
    GlobpeaContinuumForm,
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
    # Pcc2HistNamelistConfigHistnl,
    # Pcc2HistNamelistConfig,
    # Pcc2HistNamelistConfigInput,
)


def main():
    """Run a simple workflow"""
    start = datetime(2026, 5, 14)
    end = datetime(2026, 5, 15)
    centre_lon = 148.238
    centre_lat = -34.77
    interval: timedelta = 6  # 6-hourly time step
    times = TimeRange(start=start, end=end, interval=interval, include_end=False)
    run_time_seconds = int((end - start).total_seconds())
    resolution_km = 25.0
    count = 48
    dt = GlobpeaGridresRecommendedTimestep(resolution_km)
    vertical_levels = 27
    datadir = Path(__file__).resolve().parent / "data"
    vegindir = datadir / "ccam_veg_topo"
    raddir = datadir / "ccam_radiation"

    terread = TerreadConfig(
        input=TerreadNamelistConfig(
            topnml=TerreadNamelistConfigTop(
                il=count,
                rlong0=centre_lon,
                rlat0=centre_lat,
                schmidt=(count * resolution_km) / (112.0 * 90.0),
                do1km=False,
                do250=False,
                # TODO: DataBlob etc?
                filepath10km=datadir,  # topo2 is the file it will look for, or failing that, topo2.nc
            ),
        ),
    )

    igbpveg = IgbpvegConfig(
        input=IgbpvegNamelistConfig(
            vegnml=IgbpvegNamelistConfigVeg(
                month=start.month,
                # Set the input topofile to terread's output topofile
                topofile=terread.input.topnml.fileout,
                landtypeout=Path("veg.nc"),
                veginput=vegindir / "gigbp2_0ll.img",
                laiinput=vegindir / f"slai{start.month:02}.img",
                soilinput=vegindir / "usda4.img",
                albvisinput=vegindir / "salbvis223.img",
                albnirinput=vegindir / "salbnir223.img",
            ),
        ),
    )

    cdfvidar = CdfvidarConfig(
        input=CdfvidarNamelistConfig(
            gnml=CdfvidarNamelistConfigG(
                kl=vertical_levels,
                # Set the input topofile to terread's output topofile
                zsfil=terread.input.topnml.fileout,
                inf=(
                    Path(__file__).resolve().parent
                    / "data"
                    / "pressure_and_surface_temp.nc"
                ),
            ),
        ),
    )

    globpea = GlobpeaConfig(
        input=GlobpeaNamelistConfig(
            cardin=GlobpeaNamelistConfigCardin(
                # date and runlength
                kdate_s=start.date(),
                dt=dt,
                nwt=((end - start).total_seconds()) / dt,
                ntau=run_time_seconds / dt,
                # TODO: see which of these we can leave out of this example
                nmaxpr=999999,
                newtop=1,
                nrungcm=-1,
                namip=GlobpeaNamip.NO_INPUT_DATA,
                rescrn=Flag.ON,
                # zo_clearing=1.,
                qg_fix=GlobpeaQGFix.REMOVE_NEGATIVE_MOISTURE,
                # nhstest=0,
                # dynamical core
                epsp=0.1,
                epsu=0.1,
                epsh=1.0,
                precon=-10000,
                restol=2.0e-7,
                nh=GlobpeaDynamics.NON_HYDROSTATIC,
                knh=9,
                # maxcolour=3,
                nstagu=1,
                khor=0,
                nhorps=GlobpeaHorizontalDiffusionTerms.T_QG_TKE,
                nhorjlm=GlobpeaHorizontalDiffusion.SMAGORINSKY,
                # nhor=-151,
                mh_bs=3,
                # ntvd=3,
                # mass fixer
                mfix_qg=1,
                mfix=GlobpeaMassFixer.SURFACE_PRESSURE_4,
                mfix_aero=1,
                # mfix_tr=0,
                # nudging
                nbd=0,
                mbd=0,
                # ocean, lakes and rivers
                tss_sh=0.3,
                # charnock=-2.0,
                # land, urban and carbon
                nsib=7,
                nurban=1,
                vmodmin=0.1,
                nsigmf=0,
                jalbfix=0,
                # radiation and aerosols
                nrad=5,
                # amipo3=False,
                # boundary layer
                nvmix=6,
                nlocal=7,
                # station
                mstn=0,
                nstn=0,
                # file
                synchist=False,
                compression=1,
                # io_in=1,
                # fnproc_bcast_max=24,
            ),
            skyin=GlobpeaNamelistConfigSkyin(
                mins_rad=-1,
                qgmin=1.0e-20,
                siglow=0.76,
                sigmid=0.44,
                linecatalog_form=GlobpeaLineCatalogForm.HITRAN_2012,
                continuum_form=GlobpeaContinuumForm.MT_CKD2_5,
                do_co2_10um=True,
                do_quench=False,
                remain_rayleigh_bug=False,
                use_rad_year=False,
                liqradmethod=0,
                iceradmethod=5,
            ),
            kuonml=GlobpeaNamelistConfigKuo(
                nkuo=21,
                iterconv=3,
                ksc=0,
                kscsea=0,
                mdelay=0,
                alflnd=1.10,
                alfsea=1.10,
                convfact=1.05,
                convtime=-3030.60,
                detrain=0.15,
                detrainx=0.0,
                dsig4=1.0,
                entrain=-0.5,
                fldown=-0.3,
                mbase=1,
                nbase=3,
                methdetr=-1,
                methprec=5,
                ncvcloud=0,
                nevapcc=0,
                nuvconv=-3,
                rhcv=0.0,
                rhmois=0.0,
                tied_con=0.0,
                tied_over=2626.0,
                ldr=1,
                nstab_cld=0,
                nrhcrit=10,
                sigcll=0.95,
                dsig2=0.1,
                # kscmom=0,
                sig_ct=1.0,
                sigkscb=0.95,
                sigksct=0.8,
                # tied_rh=0.0,
                nclddia=-4,
                # nmr=1,
                nevapls=0,
                ncloud=101,
                # tiedtke_form=1,
                acon=0.0,
                bcon=0.02,
                # rcrit_l=0.825,
                # rcrit_s=0.825,
                # lin_aerosolmode=1,
                # lin_adv=1,
                # qlg_max=1.0e-3,
                # qfg_max=1.0e-3,
            ),
            turbnml=GlobpeaNamelistConfigTurb(
                buoymeth=1,
                # tkemeth=1,
                mintke=1.5e-4,
                mineps=1.0e-6,
                minl=5.0,
                maxl=500.0,
                qcmf=1.0e-4,
                # ezmin=10.0,
                ent0=0.5,
                ent1=0.0,
                # ent_min=0.001,
                be=1.0,
                b1=2.0,
                b2=0.3333,
                m0=0.1,
                # tke_timeave_length=0.0,
                # wg_tau=3.0,
                # wg_prob=0.5,
                # dvmodmin=0.01,
                # amxlsq=9.0,
                ngwd=-20,
                helim=1600.0,
                fc2=-0.5,
                sigbot_gwd=1.0,
                alphaj=0.025,
            ),
            landnml=GlobpeaNamelistConfigLand(
                proglai=0,
                # progvcmax=0,
                ccycle=0,
                # soil_struc=0,
                # fwsoil_switch=3,
                # cable_pop=0,
                # gs_switch=1,
                # cable_potev=1,
                # cable_litter=0,
                # ateb_intairtmeth=1,
                # ateb_intmassmeth=2,
                # ateb_zoroof=0.05,
                # ateb_zocanyon=0.05,
            ),
            datafile=GlobpeaNamelistConfigDatafile(
                # Set the initial conditions to cdfvidar's output
                ifile=cdfvidar.input.gnml.vfil,
                # Set the input topofile to terread's output topofile
                topofile=terread.input.topnml.fileout,
                # Set the input vegetation file to igbpveg's output vegetation file
                vegfile=igbpveg.input.vegnml.landtypeout,
                # TODO: check which of these is required
                cnsdir=raddir,
                radfile=raddir / "co2_data.27-10",
                eigenv=raddir / "eigenv27-10.300",
                o3file=raddir / "pp.Ozone_CMIP5_ACC_SPARC_2020-2029_RCP4.5_T3M_O3.nc",
                # ofile="rawoutput.nc",
                # restfile="Restart.nc",
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
