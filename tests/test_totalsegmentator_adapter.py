"""Tests for the TotalSegmentator Stage A adapter."""

from pathlib import Path

import nibabel as nib
import numpy as np
import pytest

from localization.totalsegmentator_adapter import (
    build_totalsegmentator_command,
    merge_binary_vertebra_masks,
)


def save_image(path: Path, data: np.ndarray) -> None:
    nib.save(nib.Nifti1Image(data, np.eye(4)), str(path))


def test_command_requests_only_target_vertebrae(tmp_path: Path) -> None:
    command = build_totalsegmentator_command(
        tmp_path / "ct.nii.gz",
        tmp_path / "segmentations",
    )

    assert "--roi_subset" in command
    assert "vertebrae_T4" in command
    assert "vertebrae_T12" in command
    assert "vertebrae_L4" in command
    assert "--robust_crop" in command
    assert "--fast" not in command


def test_binary_masks_are_merged(tmp_path: Path) -> None:
    ct_path = tmp_path / "ct.nii.gz"
    segmentation_directory = tmp_path / "segmentations"
    output_path = tmp_path / "merged.nii.gz"
    segmentation_directory.mkdir()

    ct = np.zeros((16, 16, 16), dtype=np.float32)
    t4_mask = np.zeros(ct.shape, dtype=np.uint8)
    t5_mask = np.zeros(ct.shape, dtype=np.uint8)

    t4_mask[2:6, 3:8, 4:9] = 1
    t5_mask[9:13, 3:8, 4:9] = 1

    save_image(ct_path, ct)
    save_image(segmentation_directory / "vertebrae_T4.nii.gz", t4_mask)
    save_image(segmentation_directory / "vertebrae_T5.nii.gz", t5_mask)

    merge_binary_vertebra_masks(
        ct_path,
        segmentation_directory,
        output_path,
        vertebrae=("T4", "T5"),
    )

    merged = np.asarray(nib.load(str(output_path)).dataobj)
    assert set(np.unique(merged).astype(int)) == {0, 11, 12}


def test_missing_mask_is_rejected(tmp_path: Path) -> None:
    ct_path = tmp_path / "ct.nii.gz"
    save_image(ct_path, np.zeros((8, 8, 8), dtype=np.float32))

    with pytest.raises(FileNotFoundError, match="vertebrae_T4"):
        merge_binary_vertebra_masks(
            ct_path,
            tmp_path / "empty",
            tmp_path / "merged.nii.gz",
            vertebrae=("T4",),
        )


def test_invalid_device_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Device"):
        build_totalsegmentator_command(
            tmp_path / "ct.nii.gz",
            tmp_path / "segmentations",
            device="magic",
        )
