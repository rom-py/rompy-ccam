# """CCAM Rompy grid."""

# import logging
# from pathlib import Path
# from typing import Literal
# from pydantic import Field

# from rompy.core.grid import BaseGrid
# from rompy.core.types import Coordinate

# logger = logging.getLogger(__name__)

# HERE = Path(__file__).parent

# class CCAMGrid(BaseGrid):
#     """CCAM grid class.
#     """

#     model_type: Literal["ccam"] = Field(
#         default="ccam",
#         description="Model type discriminator",
#     )

#     def DEFAULT_MIDPOINT() -> Coordinate:
#         return Coordinate(lon=0.0, lat=0.0)

#     midpoint: Coordinate = Field(
#         default_factory=CCAMGrid.DEFAULT_MIDPOINT,
#         description="The midpoint of the domain",
#     )

#     DEFAULT_GRIDSIZE: int = 96

#     gridsize: int = Field(
#         default=CCAMGrid.DEFAULT_GRIDSIZE,
#         description="Cubic grid size (e.g., 48, 72, 96, 144, 192, 288, 384, 576, 768, 1152, 1536, etc.)",
#     )

#     def DEFAULT_GRIDRES(gridsize: int) -> float:
#         return 112.0 * 90.0 / gridsize

#     gridres: Optional[float] = Field(
#         default=None,
#         description="Required resolution (km) of domain (None=global)",
#     )

#     @model_validator(mode="after")
#     def set_default_gridres(this) -> Self:
#         """Set the grid resolution to global if none was given."""
#         # This is done as a validator because it depends on gridsize
#         if this.gridres is None:
#             this.gridres = CCAMGrid.DEFAULT_GRIDRES(this.gridsize)
#         return this
