"""Tests for crop quality-control previews."""

from pathlib import Path

import numpy as np
import pytest

from data_prep.visualize_crop import save_crop_preview


def test_preview_is_created(tmp_path: Path) -> None:
    crop = np.zeros((64, 64, 64), dtype=np.float32)
    crop[20:44, 18:46, 22:42] = 0.5

    preview_path = save_crop_preview(
        crop,
        tmp_path / "qc" / "example.png",
        title="T12 grade 2",
    )

    assert preview_path.is_file()
    assert preview_path.stat().st_size > 0


def test_non_3d_crop_is_rejected(tmp_path: Path) -> None:
    crop = np.zeros((64, 64), dtype=np.float32)

    with pytest.raises(ValueError, match="three-dimensional"):
        save_crop_preview(crop, tmp_path / "bad.png")


def test_unnormalized_crop_is_rejected(tmp_path: Path) -> None:
    crop = np.full((64, 64, 64), 400.0, dtype=np.float32)

    with pytest.raises(ValueError, match="normalized"):
        save_crop_preview(crop, tmp_path / "bad.png")
