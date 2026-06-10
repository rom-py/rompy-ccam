import sys

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
from typing import Literal, Optional
from pathlib import Path

from pydantic import Field, model_validator

from .pydantic import (
    fields_satisfying,
    field_is_type_with_tag,
    field_is_optional_type_with_tag,
    fields_with_type_satisfying,
    type_is_subclass,
    type_is_optional_subclass,
)
from .rompy_ccam import CCAMBaseConfig, CCAMExeConfig
from .fileio_config import (
    find_paths_with_tag,
    Input,
    Output,
    FileInputConfig,
    FileOutputConfig,
)
from .frozenset_utils import frozenset_format_as_file_list

from .ccam.globpea import GlobpeaConfig
from .ccam.terread import TerreadConfig
from .ccam.igbpveg import IgbpvegConfig
from .ccam.cdfvidar import CdfvidarConfig
from .ccam.aeroemiss import AeroemissConfig
from .ccam.ocnbath import OcnbathConfig
from .ccam.pcc2hist import Pcc2HistConfig
from .ccam.casafield import CasafieldConfig


class CCAMWorkflow(CCAMBaseConfig):
    """A fixed sequence of CCAM execution; a typical use of CCAM."""

    model_type: Literal["ccam-workflow"] = Field(
        default="ccam-workflow",
        description="Model type discriminator",
    )

    terread: Optional[TerreadConfig] = Field(
        default_factory=TerreadConfig,
        description="First, terread creates a 'topout' file which is basically the topograph. This defines the user grid based on centre lat/lon, grid size and resolution.",
    )

    igbpveg: Optional[IgbpvegConfig] = Field(
        default_factory=IgbpvegConfig,
        description="igbpveg creates a vegetation map, reading terread's 'topout' as input.",
    )

    cdfvidar: Optional[CdfvidarConfig] = Field(
        default=None,
        description="cdfvidar creates initial conditions, reading 'topout' as input. This is required on the first pass, but can be skipped when downscaling (nesting).",
    )

    aeroemiss: Optional[AeroemissConfig] = Field(
        default=None,
        description="Create aerosol emissions for CCAM. Be sure to set globpea's aerosol input file (globpea.input.datafile.so4tfile) to aeroemiss's output file (aeroemiss.output), etc.",
    )

    ocnbath: Optional[OcnbathConfig] = Field(
        default=None,
        description="Calculate ocean/lake bathymetry and also determine river routing. Be sure to set globpea's input bathymetry file (globpea.input.datafile.bathfile) to ocnbath's output file (ocnbath.input.ocnml.bathout), etc.",
    )

    casafield: Optional[CasafieldConfig] = Field(
        default=None,
        description="Create input files for the CASA-CNP carbon cycle model. Be sure to set globpea's input carbon cycle file (globpea.input.datafile.casafile) to casafield's output (casafield.output), etc.",
    )

    globpea: Optional[GlobpeaConfig] = Field(
        default=None,
        description="globpea uses all the topography, initial conditions, vegetation etc. to run the simulation.",
    )

    # pcc2hist post-processes the output from globpea, usually converting back into a lat/lon grid.
    # pcc2hist may be run multiple times, depending on what output is required.
    pcc2hists: list[Pcc2HistConfig]

    next: Optional["CCAMNestedWorkflow"] = Field(
        default=None,
        description="Further CCAM workflows to run after this one. This is intended for running nested, or downscaled workflows.",
    )

    @property
    def input_files(self) -> frozenset[Path]:
        """What files does this config expect to be present in the filesystem when it runs?"""
        # We aim to return the input files from all steps in the workflow, minus those files which were
        # created by previous steps in the workflow. This gives us the list of files which must be
        # available *before* the workflow runs.
        inputs_we_didnt_create: frozenset[Path] = frozenset()
        outputs_so_far: frozenset[Path] = frozenset()
        for step in self.executable_steps():
            inputs_we_didnt_create |= step.input_files - outputs_so_far
            outputs_so_far |= step.output_files
        return inputs_we_didnt_create

    @property
    def output_files(self) -> frozenset[Path]:
        """What files does running this config produce?"""
        # The definition we inherit from FileOutputConfigAuto doesn't work for `next`, because it is annotated
        # with a string, i.e. "CCAMNestedWorkflow", not the actual type CCAMNestedWorkflow
        return super().output_files | (
            self.next.output_files if self.next is not None else frozenset()
        )

    def executable_steps(self) -> list[CCAMExeConfig]:
        """List all the CCAMExeConfigs that this class calls directly."""
        return [
            step
            for step in (
                [
                    self.terread,
                    self.igbpveg,
                    self.cdfvidar,
                    self.aeroemiss,
                    self.ocnbath,
                    self.casafield,
                    self.globpea,
                ]
                + self.pcc2hists
            )
            if step is not None
        ] + (self.next.executable_steps() if self.next is not None else [])

    @model_validator(mode="after")
    def check_no_file_conflicts(self) -> Self:
        """Check that no two of the executable steps of this workflow produce the same output files."""
        output_files_so_far = frozenset()
        for step in self.executable_steps():
            conflicting_output_files: frozenset[Path] = (
                output_files_so_far & step.output_files
            )
            if conflicting_output_files:
                raise ValueError(
                    f"Different steps of this workflow would create/overwrite these files: {frozenset_format_as_file_list(conflicting_output_files)}:\nThe *second* step which created these files was: {step}"
                )
            output_files_so_far = output_files_so_far | step.output_files
        return self


class CCAMNestedWorkflow(CCAMWorkflow):
    """A CCAM nested, or downscaled workflow."""

    model_type: Literal["ccam-nested-workflow"] = Field(
        default="ccam-nested-workflow",
        description="Model type discriminator",
    )

    # cdfvidar is not necessary in an initial workflow (TODO: should it be optional though?)
    cdfvidar: None = Field(
        default=None,
        description="cdfvidar is not necessary in a nested workflow.",
    )


class CCAMInitialWorkflow(CCAMWorkflow):
    """A CCAM initial, or top-level workflow."""

    model_type: Literal["ccam-initial-workflow"] = Field(
        default="ccam-initial-workflow",
        description="Model type discriminator",
    )

    # override parent's terread to make it non-optional
    terread: TerreadConfig = Field(
        default_factory=TerreadConfig,
        description="First, terread creates a 'topout' file which is basically the topograph. This defines the user grid based on centre lat/lon, grid size and resolution.",
    )

    # override parent's igbpveg to make it non-optional
    igbpveg: IgbpvegConfig = Field(
        default_factory=IgbpvegConfig,
        description="igbpveg creates a vegetation map, reading terread's 'topout' as input.",
    )

    # override parent's cdfvidar to make it non-optional
    cdfvidar: CdfvidarConfig = Field(
        default_factory=CdfvidarConfig,
        description="cdfvidar creates initial conditions, reading 'topout' as input.",
    )

    # override parent's globpea to make it non-optional
    globpea: GlobpeaConfig = Field(
        default=None,
        description="globpea uses all the topography, initial conditions, vegetation etc. to run the simulation.",
    )
