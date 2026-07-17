"""Tests for safe NIfTI loading."""

from pathlib import Path

import nibabel as nib
import numpy as np
import pytest

from data_prep.nifti_io import load_nifti_pair


def save_nifti(path: Path, data: np.ndarray, affine: np.ndarray) -> None:
    image = nib.Nifti1Image(data, affine)
    nib.save(image, str(path))


def test_matching_ct_and_mask_load_successfully(tmp_path: Path) -> None:
    affine = np.diag([1.0, 1.5, 2.0, 1.0])
    ct_data = np.full((8, 9, 10), 400.0, dtype=np.float32)
    mask_data = np.zeros((8, 9, 10), dtype=np.int16)
    mask_data[2:6, 2:7, 3:8] = 11

    ct_path = tmp_path / "ct.nii.gz"
    mask_path = tmp_path / "mask.nii.gz"
    save_nifti(ct_path, ct_data, affine)
    save_nifti(mask_path, mask_data, affine)

    pair = load_nifti_pair(ct_path, mask_path)

    assert pair.ct_volume.shape == (8, 9, 10)
    assert pair.segmentation_mask.dtype == np.int16
    assert pair.spacing_mm == pytest.approx((1.0, 1.5, 2.0))


def test_different_shapes_are_rejected(tmp_path: Path) -> None:
    affine = np.eye(4)
    ct_path = tmp_path / "ct.nii.gz"
    mask_path = tmp_path / "mask.nii.gz"

    save_nifti(ct_path, np.zeros((8, 8, 8), dtype=np.float32), affine)
    save_nifti(mask_path, np.zeros((7, 8, 8), dtype=np.int16), affine)

    with pytest.raises(ValueError, match="shapes differ"):
        load_nifti_pair(ct_path, mask_path)


def test_different_coordinates_are_rejected(tmp_path: Path) -> None:
    ct_affine = np.eye(4)
    mask_affine = np.eye(4)
    mask_affine[0, 3] = 5.0

    ct_path = tmp_path / "ct.nii.gz"
    mask_path = tmp_path / "mask.nii.gz"

    save_nifti(ct_path, np.zeros((8, 8, 8), dtype=np.float32), ct_affine)
    save_nifti(mask_path, np.zeros((8, 8, 8), dtype=np.int16), mask_affine)

    with pytest.raises(ValueError, match="physical coordinates"):
        load_nifti_pair(ct_path, mask_path)


def test_fractional_mask_labels_are_rejected(tmp_path: Path) -> None:
    affine = np.eye(4)
    ct_path = tmp_path / "ct.nii.gz"
    mask_path = tmp_path / "mask.nii.gz"

    ct_data = np.zeros((8, 8, 8), dtype=np.float32)
    mask_data = np.zeros((8, 8, 8), dtype=np.float32)
    mask_data[3, 3, 3] = 1.5

    save_nifti(ct_path, ct_data, affine)
    save_nifti(mask_path, mask_data, affine)

    with pytest.raises(ValueError, match="non-integer"):
        load_nifti_pair(ct_path, mask_path)


def test_missing_file_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_nifti_pair(
            tmp_path / "missing-ct.nii.gz",
            tmp_path / "missing-mask.nii.gz",
        )
