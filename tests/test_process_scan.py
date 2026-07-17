"""Tests for scan-to-crop processing."""

from pathlib import Path

import nibabel as nib
import numpy as np
import pytest

from data_prep.process_scan import process_verse_scan


def create_scan(tmp_path: Path) -> tuple[Path, Path]:
    ct = np.full((24, 24, 24), -1000.0, dtype=np.float32)
    mask = np.zeros(ct.shape, dtype=np.int16)

    mask[7:17, 7:17, 7:17] = 11
    ct[mask == 11] = 400.0

    ct_path = tmp_path / "ct.nii.gz"
    mask_path = tmp_path / "mask.nii.gz"
    affine = np.eye(4)

    nib.save(nib.Nifti1Image(ct, affine), str(ct_path))
    nib.save(nib.Nifti1Image(mask, affine), str(mask_path))
    return ct_path, mask_path


def test_scan_creates_crop_and_manifest(tmp_path: Path) -> None:
    ct_path, mask_path = create_scan(tmp_path)

    manifest, rejections = process_verse_scan(
        ct_path,
        mask_path,
        patient_id="sub-001",
        scan_id="scan-001",
        grades={"T4": 2, "T5": 1},
        output_directory=tmp_path / "crops",
    )

    assert len(manifest) == 1
    assert manifest.iloc[0]["genant_grade"] == 2
    assert len(rejections) == 1

    crop_path = tmp_path / "crops" / manifest.iloc[0]["crop_path"]
    crop = np.load(crop_path, allow_pickle=False)
    assert crop.shape == (64, 64, 64)


def test_invalid_grade_is_rejected(tmp_path: Path) -> None:
    ct_path, mask_path = create_scan(tmp_path)

    with pytest.raises(ValueError, match="Invalid Genant grade"):
        process_verse_scan(
            ct_path,
            mask_path,
            "sub-001",
            "scan-001",
            {"T4": 8},
            tmp_path / "crops",
        )


def test_unsafe_patient_id_is_rejected(tmp_path: Path) -> None:
    ct_path, mask_path = create_scan(tmp_path)

    with pytest.raises(ValueError, match="Unsafe patient_id"):
        process_verse_scan(
            ct_path,
            mask_path,
            "../unsafe",
            "scan-001",
            {"T4": 0},
            tmp_path / "crops",
        )
