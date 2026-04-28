from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field

from rompy_ccam import CCAMExeConfig, Input, Output


class CasafieldConfig(CCAMExeConfig):
    """Configuration options to be given to the casafield executable.

    CASAFIELD is used to create input files for the CASA-CNP carbon cycle model available with CCAM. In addition to simulating the terrestrial carbon cycle, this option also allows the CABLE land-surface scheme to run with a prognostic Leaf Area Index (LAI) and the Populations-Order-Physiology (POP) model.
    """

    model_type: Literal["casafield"] = "casafield"

    topofile: Path = Field(
        description="Input topography file created by terread.",
    )

    input: Annotated[
        Path,
        Field(
            description="The casaNP_gridinfo_1dx1d.nc file for carbon cycle emissions.",
        ),
        Input,
    ]

    output: Annotated[
        Path,
        Field(
            description="Output carbon cycle emissions on the cubic grid (to be read by CCAM).",
        ),
        Output,
    ]

    def bash_invocation(self) -> str:
        args = [
            f"-t {self.topofile}",
            f"-i {self.input}",
            f"-o {self.output}",
        ]
        return self.bash_prettify_invocation(f'run_cmd casafield {" ".join(args)}')
