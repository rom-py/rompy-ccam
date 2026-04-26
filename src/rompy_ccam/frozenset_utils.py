"""Helper functions for frozensets."""

from pathlib import Path
from typing import Any
from functools import reduce
from operator import or_


def frozenset_list_union(lst: list[frozenset[Any]]) -> frozenset[Any]:
    return reduce(or_, lst, frozenset())


def frozenset_format_as_file_list(s: frozenset[Path]) -> str:
    return "nothing" if not s else ", ".join(str(p) for p in sorted(s, key=str))
