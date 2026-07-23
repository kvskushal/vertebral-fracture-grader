"""Tests for the vertebra training dataset."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch
from torch.utils.data import DataLoader

from model.dataset import VertebraDataset


def valid_manifest(crop_path: str = "sample_T4.npy") -> pd.DataFrame:
    """Create one valid synthetic manifest row."""
    return pd.DataFrame(
        [
            {
                "patient_id": "test-patient-001",
                "scan_id": "test-scan-001",
                "vertebra": "T4",
                "genant_grade": 2,
                "crop_path": crop_path,
                "source_dataset": "synthetic-test",
                "split": "train",
                "preprocessing_version": "v1_hu-200_1000_crop64_pad10mm",
                "source_license": "synthetic-test-only",
            }
        ]
    )


def test_dataset_loads_valid_crop(tmp_path: Path) -> None:
    crop = np.full((64, 64, 64), 0.5, dtype=np.float32)
    np.save(tmp_path / "sample_T4.npy", crop)

    dataset = VertebraDataset(valid_manifest(), tmp_path)
    crop_tensor, grade_tensor = dataset[0]

    assert crop_tensor.shape == (1, 64, 64, 64)
    assert crop_tensor.dtype == torch.float32
    assert grade_tensor.dtype == torch.long
    assert grade_tensor.item() == 2

    loader = DataLoader(dataset, batch_size=1)
    batch_crops, batch_grades = next(iter(loader))

    assert batch_crops.shape == (1, 1, 64, 64, 64)
    assert batch_grades.tolist() == [2]


def test_missing_crop_is_rejected(tmp_path: Path) -> None:
    dataset = VertebraDataset(valid_manifest(), tmp_path)

    with pytest.raises(FileNotFoundError, match="does not exist"):
        dataset[0]


def test_wrong_crop_shape_is_rejected(tmp_path: Path) -> None:
    crop = np.zeros((32, 32, 32), dtype=np.float32)
    np.save(tmp_path / "sample_T4.npy", crop)

    dataset = VertebraDataset(valid_manifest(), tmp_path)

    with pytest.raises(ValueError, match="Expected crop shape"):
        dataset[0]


def test_wrong_crop_dtype_is_rejected(tmp_path: Path) -> None:
    crop = np.zeros((64, 64, 64), dtype=np.float64)
    np.save(tmp_path / "sample_T4.npy", crop)

    dataset = VertebraDataset(valid_manifest(), tmp_path)

    with pytest.raises(ValueError, match="float32"):
        dataset[0]


def test_unnormalized_crop_is_rejected(tmp_path: Path) -> None:
    crop = np.full((64, 64, 64), 1.5, dtype=np.float32)
    np.save(tmp_path / "sample_T4.npy", crop)

    dataset = VertebraDataset(valid_manifest(), tmp_path)

    with pytest.raises(ValueError, match="normalized"):
        dataset[0]


def test_absolute_crop_path_is_rejected(tmp_path: Path) -> None:
    absolute_path = str((tmp_path / "sample_T4.npy").resolve())
    dataset = VertebraDataset(valid_manifest(absolute_path), tmp_path)

    with pytest.raises(ValueError, match="must be relative"):
        dataset[0]
