"""Tests for CT preprocessing."""

import numpy as np
import pytest

from data_prep.preprocessing import TARGET_SHAPE, clip_and_normalize


def test_preprocessing_values() -> None:
    volume = np.array([-500.0, -200.0, 400.0, 1000.0, 1200.0]).reshape(1, 1, 5)
    result = clip_and_normalize(volume)

    expected = np.array([0.0, 0.0, 0.5, 1.0, 1.0]).reshape(1, 1, 5)
    np.testing.assert_allclose(result, expected)
    assert result.dtype == np.float32


def test_wrong_number_of_dimensions() -> None:
    with pytest.raises(ValueError, match="3-dimensional"):
        clip_and_normalize(np.zeros((64, 64), dtype=np.float32))


def test_target_shape() -> None:
    assert TARGET_SHAPE == (64, 64, 64)
