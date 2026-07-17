"""End-to-end test for loading, cropping, splitting, and visualization."""

from pathlib import Path

import nibabel as nib
import numpy as np

from data_prep.manifest import assign_patient_splits, validate_manifest
from data_prep.process_scan import process_verse_scan
from data_prep.visualize_crop import save_crop_preview


def test_small_end_to_end_pipeline(tmp_path: Path) -> None:
    ct = np.full((24, 24, 24), -1000.0, dtype=np.float32)
    mask = np.zeros(ct.shape, dtype=np.int16)

    mask[7:17, 7:17, 7:17] = 11
    ct[mask == 11] = 400.0

    ct_path = tmp_path / "ct.nii.gz"
    mask_path = tmp_path / "mask.nii.gz"
    affine = np.eye(4)

    nib.save(nib.Nifti1Image(ct, affine), str(ct_path))
    nib.save(nib.Nifti1Image(mask, affine), str(mask_path))

    crop_directory = tmp_path / "crops"
    manifest, rejections = process_verse_scan(
        ct_path,
        mask_path,
        patient_id="patient-001",
        scan_id="scan-001",
        grades={"T4": 2},
        output_directory=crop_directory,
    )

    assert rejections.empty
    assert len(manifest) == 1

    split_manifest = assign_patient_splits(manifest)
    validate_manifest(split_manifest)
    assert split_manifest.iloc[0]["split"] == "train"

    crop_path = crop_directory / manifest.iloc[0]["crop_path"]
    crop = np.load(crop_path, allow_pickle=False)

    preview_path = save_crop_preview(
        crop,
        tmp_path / "qc" / "patient-001_T4.png",
    )

    assert crop.shape == (64, 64, 64)
    assert preview_path.is_file()
