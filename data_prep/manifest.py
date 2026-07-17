"""Validate crop manifests and create patient-level dataset splits."""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd

from data_prep.preprocessing import CONFIG

ALLOWED_VERTEBRAE: Final = set(CONFIG["vertebrae"])
ALLOWED_GRADES: Final = {0, 1, 2, 3}
ALLOWED_SPLITS: Final = {"train", "validation", "test"}

BASE_COLUMNS: Final = {
    "patient_id",
    "scan_id",
    "vertebra",
    "genant_grade",
    "crop_path",
    "source_dataset",
    "preprocessing_version",
    "source_license",
}
REQUIRED_COLUMNS: Final = BASE_COLUMNS | {"split"}


def _validate_basic_manifest(frame: pd.DataFrame) -> None:
    """Validate fields that are required before assigning a split."""
    missing = BASE_COLUMNS.difference(frame.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"Manifest is missing columns: {missing_text}")

    if frame.empty:
        raise ValueError("Manifest cannot be empty.")

    if frame[list(BASE_COLUMNS)].isnull().any().any():
        raise ValueError("Manifest contains missing values.")

    valid_patient_ids = frame["patient_id"].map(
        lambda value: isinstance(value, str) and bool(value.strip())
    )
    if not valid_patient_ids.all():
        raise ValueError("Every patient_id must be a non-empty anonymous string.")

    if not pd.api.types.is_integer_dtype(frame["genant_grade"]):
        raise ValueError("Genant grades must be stored as integers.")

    invalid_grades = set(frame["genant_grade"]).difference(ALLOWED_GRADES)
    if invalid_grades:
        raise ValueError(f"Invalid Genant grades: {sorted(invalid_grades)}")

    invalid_vertebrae = set(frame["vertebra"]).difference(ALLOWED_VERTEBRAE)
    if invalid_vertebrae:
        raise ValueError(f"Invalid vertebral levels: {sorted(invalid_vertebrae)}")


def validate_manifest(frame: pd.DataFrame) -> None:
    """Validate a completed training manifest."""
    _validate_basic_manifest(frame)

    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"Manifest is missing columns: {missing_text}")

    invalid_splits = set(frame["split"]).difference(ALLOWED_SPLITS)
    if invalid_splits:
        raise ValueError(f"Invalid split names: {sorted(invalid_splits)}")

    split_counts = frame.groupby("patient_id")["split"].nunique()
    leaking_patients = split_counts[split_counts > 1].index.tolist()
    if leaking_patients:
        raise ValueError(f"Patients appear in multiple splits: {leaking_patients}")


def _split_counts(
    number_of_patients: int, val_fraction: float, test_fraction: float
) -> tuple[int, int, int]:
    """Choose train, validation, and test counts for one severity group."""
    if number_of_patients == 1:
        return 1, 0, 0

    if number_of_patients == 2:
        return 1, 0, 1

    validation_count = max(1, round(number_of_patients * val_fraction))
    test_count = max(1, round(number_of_patients * test_fraction))

    if validation_count + test_count >= number_of_patients:
        validation_count = 1
        test_count = 1

    train_count = number_of_patients - validation_count - test_count
    return train_count, validation_count, test_count


def assign_patient_splits(
    frame: pd.DataFrame,
    train_fraction: float = 0.70,
    val_fraction: float = 0.15,
    test_fraction: float = 0.15,
    seed: int = 42,
) -> pd.DataFrame:
    """Assign each patient to exactly one split, stratified by maximum grade."""
    _validate_basic_manifest(frame)

    fraction_sum = train_fraction + val_fraction + test_fraction
    if not np.isclose(fraction_sum, 1.0):
        raise ValueError("Train, validation, and test fractions must add to 1.")

    result = frame.copy()
    patient_grades = result.groupby("patient_id")["genant_grade"].max()
    assignments: dict[str, str] = {}

    for grade, grade_group in patient_grades.groupby(patient_grades):
        patient_ids = sorted(grade_group.index.tolist())
        generator = np.random.default_rng(seed + int(grade))
        generator.shuffle(patient_ids)

        train_count, validation_count, _ = _split_counts(
            len(patient_ids), val_fraction, test_fraction
        )
        validation_end = train_count + validation_count

        for patient_id in patient_ids[:train_count]:
            assignments[patient_id] = "train"

        for patient_id in patient_ids[train_count:validation_end]:
            assignments[patient_id] = "validation"

        for patient_id in patient_ids[validation_end:]:
            assignments[patient_id] = "test"

    result["split"] = result["patient_id"].map(assignments)
    validate_manifest(result)
    return result
