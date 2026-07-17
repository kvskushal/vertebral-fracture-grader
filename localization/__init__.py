"""Stage A localization using the open TotalSegmentator main task."""

from localization.totalsegmentator_adapter import (
    build_totalsegmentator_command,
    merge_binary_vertebra_masks,
)

__all__ = [
    "build_totalsegmentator_command",
    "merge_binary_vertebra_masks",
]
