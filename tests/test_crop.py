"""Tests for fixed-size vertebral crop extraction."""

import numpy as np
import pytest

from data_prep.crop import extract_vertebra_crop, resample_to_shape


def make_fake_ct_and_mask() -> tuple[np.ndarray, np.ndarray]:
    ct_volume = np.full((32, 40, 48), -1000.0, dtype=np.float32)
    mask = np.zeros(ct_volume.shape, dtype=np.int16)

    mask[10:20, 12:28, 15:35] = 11
    ct_volume[mask == 11] = 400.0
    return ct_volume, mask


def test_crop_has_required_shape_and_range() -> None:
    ct_volume, mask = make_fake_ct_and_mask()

    crop = extract_vertebra_crop(
        ct_volume,
        mask,
        label_value=11,
        spacing_mm=(1.0, 1.0, 1.0),
        padding_mm=2.0,
    )

    assert crop.shape == (64, 64, 64)
    assert crop.dtype == np.float32
    assert crop.min() >= 0.0
    assert crop.max() <= 1.0
    assert np.isclose(crop.max(), 0.5, atol=0.01)


def test_missing_label_is_rejected() -> None:
    ct_volume, mask = make_fake_ct_and_mask()

    with pytest.raises(ValueError, match="was not found"):
        extract_vertebra_crop(
            ct_volume,
            mask,
            label_value=23,
            spacing_mm=(1.0, 1.0, 1.0),
        )


def test_mismatched_shapes_are_rejected() -> None:
    ct_volume, mask = make_fake_ct_and_mask()

    with pytest.raises(ValueError, match="matching shapes"):
        extract_vertebra_crop(
            ct_volume,
            mask[:-1],
            label_value=11,
            spacing_mm=(1.0, 1.0, 1.0),
        )


def test_invalid_spacing_is_rejected() -> None:
    ct_volume, mask = make_fake_ct_and_mask()

    with pytest.raises(ValueError, match="finite and positive"):
        extract_vertebra_crop(
            ct_volume,
            mask,
            label_value=11,
            spacing_mm=(1.0, 0.0, 1.0),
        )


def test_resampling_is_exact() -> None:
    volume = np.zeros((13, 17, 19), dtype=np.float32)
    resized = resample_to_shape(volume)

    assert resized.shape == (64, 64, 64)
