"""Tests for patient-level dataset splitting."""

import pandas as pd
import pytest

from data_prep.manifest import assign_patient_splits, validate_manifest


def make_example_manifest() -> pd.DataFrame:
    records = []

    for patient_number in range(16):
        patient_id = f"patient-{patient_number:03d}"
        grade = patient_number % 4

        for vertebra in ("T4", "T5"):
            records.append(
                {
                    "patient_id": patient_id,
                    "scan_id": f"scan-{patient_number:03d}",
                    "vertebra": vertebra,
                    "genant_grade": grade,
                    "crop_path": f"crops/{patient_id}/{vertebra}.npy",
                    "source_dataset": "example",
                    "split": "",
                    "preprocessing_version": "v1",
                    "source_license": "example-license",
                }
            )

    return pd.DataFrame(records)


def test_patient_split_has_no_leakage() -> None:
    result = assign_patient_splits(make_example_manifest())

    splits_per_patient = result.groupby("patient_id")["split"].nunique()
    assert splits_per_patient.max() == 1
    assert set(result["split"]) == {"train", "validation", "test"}


def test_split_is_repeatable() -> None:
    first = assign_patient_splits(make_example_manifest(), seed=42)
    second = assign_patient_splits(make_example_manifest(), seed=42)

    assert first["split"].tolist() == second["split"].tolist()


def test_invalid_grade_is_rejected() -> None:
    manifest = make_example_manifest()
    manifest.loc[0, "genant_grade"] = 5

    with pytest.raises(ValueError, match="Invalid Genant grades"):
        assign_patient_splits(manifest)


def test_invalid_vertebra_is_rejected() -> None:
    manifest = make_example_manifest()
    manifest.loc[0, "vertebra"] = "C2"

    with pytest.raises(ValueError, match="Invalid vertebral levels"):
        assign_patient_splits(manifest)


def test_completed_manifest_is_valid() -> None:
    result = assign_patient_splits(make_example_manifest())
    validate_manifest(result)
