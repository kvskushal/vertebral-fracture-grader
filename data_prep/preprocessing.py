"""Shared preprocessing for training and inference."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Final

import numpy as np

CONFIG_PATH: Final = Path(__file__).resolve().parents[1] / "configs" / "preprocessing.json"

with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
    CONFIG: Final = json.load(config_file)

HU_MIN: Final[float] = float(CONFIG["hu_clip_min"])
HU_MAX: Final[float] = float(CONFIG["hu_clip_max"])
TARGET_SHAPE: Final[tuple[int, int, int]] = tuple(CONFIG["crop_shape"])


def clip_and_normalize(volume: np.ndarray) -> np.ndarray:
    """Clip a 3D CT volume to the bone window and normalize it to 0-1."""
    array = np.asarray(volume, dtype=np.float32)

    if array.ndim != 3:
        raise ValueError(
            f"Expected a 3-dimensional CT volume, but received {array.ndim} dimensions."
        )

    if not np.isfinite(array).all():
        raise ValueError("CT volume contains NaN or infinite values.")

    clipped = np.clip(array, HU_MIN, HU_MAX)
    normalized = (clipped - HU_MIN) / (HU_MAX - HU_MIN)
    return normalized.astype(np.float32, copy=False)
