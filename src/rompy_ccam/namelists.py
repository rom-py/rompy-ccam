"""Mixin for a config representing a namelist."""

from typing import (
    Any,
    Optional,
    Annotated,
)
from pathlib import Path

import f90nml
from pydantic import Field

from rompy_ccam import CCAMConfig, Output


def nml_prepare_dict(d: dict) -> dict:
    """
    Prepare a pydantic model_dump() for export to .nml.

    This will recursively convert any Paths to strings, and remove any fields whose optional value is None.

    This will return a new dict, with the original being unchanged.
    """
    n: dict[Any, Any] = {}
    for key, value in d.items():
        if isinstance(value, dict):
            # Recurse into this nested dict
            n[key] = nml_prepare_dict(value)
        elif isinstance(value, Path):
            # Convert this Path into a string
            n[key] = str(value)
        elif value is not None:
            # Add this value to the new dict
            n[key] = value
    return n


class CCAMNamelistConfig(CCAMConfig):
    """A config that is intended to be exported as a namelist (.nml) file."""

    nml_path: Annotated[
        Optional[Path],
        Field(
            default=None,
            description="Optional path of the namelist (.nml) file to create.",
        ),
        Output,
    ]

    def write_nml_file(self, force=False, sort=False):
        if self.nml_path is None:
            raise ValueError("nml_path must be defined before calling write_nml_file()")

        dump = self.model_dump(
            mode="json",  # the output will only contain JSON serializable types (e.g. convert Path to string)
            exclude={
                "nml_path",
                "model_type",
                "checkout",
                "template",
            },  # Don't include our own nml_path field or pydantic fields that don't belong in the .nml
            by_alias=True,  # Use any serialization_aliases set on fields within the model
            exclude_none=True,  # Exclude field whose value is None
            # TODO: exclude empty list values as well somehow
        )
        nml = dump
        # nml = nml_prepare_dict(dump)
        f90nml.write(nml, self.nml_path, force=force, sort=sort),
