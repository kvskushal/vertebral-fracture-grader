"""Build TotalSegmentator commands and combine its binary vertebra masks."""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Final

import nibabel as nib
import numpy as np

from data_prep.preprocessing import CONFIG

LABEL_CONFIG_PATH: Final = Path(__file__).resolve().parents[1] / "configs" / "vertebra_labels.json"
TARGET_VERTEBRAE: Final = tuple(CONFIG["vertebrae"])
VALID_DEVICE: Final = re.compile(r"^(cpu|gpu|gpu:[0-9]+)$")


def _class_name(vertebra: str) -> str:
    """Convert T4 or L1 into a TotalSegmentator class name."""
    if vertebra not in TARGET_VERTEBRAE:
        raise ValueError(f"Unsupported vertebra: {vertebra}")

    return f"vertebrae_{vertebra}"


def build_totalsegmentator_command(
    ct_path: str | Path,
    output_directory: str | Path,
    device: str = "gpu",
    vertebrae: Sequence[str] = TARGET_VERTEBRAE,
) -> list[str]:
    """Build the high-resolution TotalSegmentator Stage A command."""
    if VALID_DEVICE.fullmatch(device) is None:
        raise ValueError("Device must be cpu, gpu, or gpu followed by a number.")

    output_path = Path(output_directory)
    classes = [_class_name(vertebra) for vertebra in vertebrae]

    return [
        "TotalSegmentator",
        "-i",
        str(Path(ct_path)),
        "-o",
        str(output_path),
        "--task",
        "total",
        "--device",
        device,
        "--roi_subset",
        *classes,
        "--robust_crop",
        "--report",
        str(output_path / "totalsegmentator-report.json"),
    ]


def _load_label_configuration() -> tuple[dict[str, int], dict[str, str]]:
    """Load VerSe labels and TotalSegmentator output filenames."""
    with LABEL_CONFIG_PATH.open("r", encoding="utf-8") as label_file:
        configuration = json.load(label_file)

    verse_labels = {
        vertebra: int(value) for vertebra, value in configuration["verse_multilabel"].items()
    }
    output_files = configuration["totalsegmentator_binary_files"]
    return verse_labels, output_files


def merge_binary_vertebra_masks(
    ct_path: str | Path,
    segmentation_directory: str | Path,
    output_mask_path: str | Path,
    vertebrae: Sequence[str] = TARGET_VERTEBRAE,
    affine_tolerance: float = 0.001,
) -> Path:
    """Merge separate TotalSegmentator masks into one VerSe-style mask."""
    ct_file = Path(ct_path)
    if not ct_file.is_file():
        raise FileNotFoundError(f"CT file does not exist: {ct_file}")

    ct_image = nib.as_closest_canonical(nib.load(str(ct_file)))
    if len(ct_image.shape) != 3:
        raise ValueError("CT image must be three-dimensional.")

    verse_labels, output_files = _load_label_configuration()
    segmentation_root = Path(segmentation_directory)
    merged_mask = np.zeros(ct_image.shape, dtype=np.int16)
    missing_files = []

    for vertebra in vertebrae:
        _class_name(vertebra)
        mask_path = segmentation_root / output_files[vertebra]

        if not mask_path.is_file():
            missing_files.append(mask_path.name)
            continue

        mask_image = nib.as_closest_canonical(nib.load(str(mask_path)))

        if mask_image.shape != ct_image.shape:
            raise ValueError(f"Mask shape does not match CT: {mask_path.name}")

        if not np.allclose(
            mask_image.affine,
            ct_image.affine,
            rtol=0.0,
            atol=affine_tolerance,
        ):
            raise ValueError(f"Mask coordinates do not match CT: {mask_path.name}")

        raw_mask = np.asarray(mask_image.dataobj)
        rounded_mask = np.rint(raw_mask)

        if not np.allclose(raw_mask, rounded_mask, rtol=0.0, atol=0.0001):
            raise ValueError(f"Mask contains fractional values: {mask_path.name}")

        unique_values = set(np.unique(rounded_mask).astype(int))
        if not unique_values.issubset({0, 1}):
            raise ValueError(f"Expected a binary mask: {mask_path.name}")

        selected_voxels = rounded_mask == 1

        if np.any(merged_mask[selected_voxels] != 0):
            raise ValueError(f"Vertebra masks overlap: {mask_path.name}")

        merged_mask[selected_voxels] = verse_labels[vertebra]

    if missing_files:
        missing_text = ", ".join(missing_files)
        raise FileNotFoundError(f"Missing TotalSegmentator masks: {missing_text}")

    output_path = Path(output_mask_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    merged_image = nib.Nifti1Image(
        merged_mask,
        np.asarray(ct_image.affine),
    )
    nib.save(merged_image, str(output_path))
    return output_path
