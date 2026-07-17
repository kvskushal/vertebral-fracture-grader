"""Extract fixed-size vertebral regions from CT volumes and segmentation masks."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Final

import numpy as np
from scipy.ndimage import zoom

from data_prep.preprocessing import CONFIG, TARGET_SHAPE, clip_and_normalize

DEFAULT_PADDING_MM: Final[float] = float(CONFIG["crop_padding_mm"])


def _validate_spacing(spacing_mm: Sequence[float]) -> np.ndarray:
    """Return validated voxel spacing as a three-number array."""
    spacing = np.asarray(spacing_mm, dtype=np.float32)

    if spacing.shape != (3,):
        raise ValueError("Voxel spacing must contain exactly three numbers.")

    if not np.isfinite(spacing).all() or np.any(spacing <= 0):
        raise ValueError("Every voxel-spacing value must be finite and positive.")

    return spacing


def _fit_exact_shape(array: np.ndarray, target_shape: tuple[int, int, int]) -> np.ndarray:
    """Center-crop or center-pad an array to remove rounding differences."""
    output = np.zeros(target_shape, dtype=array.dtype)
    source_slices = []
    destination_slices = []

    for current_size, target_size in zip(array.shape, target_shape, strict=True):
        if current_size >= target_size:
            source_start = (current_size - target_size) // 2
            source_slices.append(slice(source_start, source_start + target_size))
            destination_slices.append(slice(0, target_size))
        else:
            destination_start = (target_size - current_size) // 2
            source_slices.append(slice(0, current_size))
            destination_slices.append(slice(destination_start, destination_start + current_size))

    output[tuple(destination_slices)] = array[tuple(source_slices)]
    return output


def resample_to_shape(
    volume: np.ndarray,
    target_shape: tuple[int, int, int] = TARGET_SHAPE,
) -> np.ndarray:
    """Resize a three-dimensional volume to an exact target shape."""
    array = np.asarray(volume, dtype=np.float32)

    if array.ndim != 3:
        raise ValueError("Only three-dimensional volumes can be resized.")

    if len(target_shape) != 3 or any(size <= 0 for size in target_shape):
        raise ValueError("Target shape must contain three positive numbers.")

    scale_factors = tuple(
        target_size / current_size
        for target_size, current_size in zip(target_shape, array.shape, strict=True)
    )

    resized = zoom(
        array,
        zoom=scale_factors,
        order=1,
        mode="nearest",
        prefilter=False,
    )
    return _fit_exact_shape(resized, target_shape).astype(np.float32, copy=False)


def extract_vertebra_crop(
    ct_volume: np.ndarray,
    segmentation_mask: np.ndarray,
    label_value: int,
    spacing_mm: Sequence[float],
    padding_mm: float = DEFAULT_PADDING_MM,
    target_shape: tuple[int, int, int] = TARGET_SHAPE,
) -> np.ndarray:
    """Extract, normalize, and resize one labeled vertebra from a CT volume."""
    ct_array = np.asarray(ct_volume)
    mask_array = np.asarray(segmentation_mask)

    if ct_array.ndim != 3 or mask_array.ndim != 3:
        raise ValueError("CT volume and segmentation mask must both be 3-dimensional.")

    if ct_array.shape != mask_array.shape:
        raise ValueError("CT volume and segmentation mask must have matching shapes.")

    if padding_mm < 0:
        raise ValueError("Padding cannot be negative.")

    spacing = _validate_spacing(spacing_mm)
    vertebra_mask = mask_array == label_value
    coordinates = np.argwhere(vertebra_mask)

    if coordinates.size == 0:
        raise ValueError(f"Segmentation label {label_value} was not found.")

    padding_voxels = np.ceil(padding_mm / spacing).astype(int)
    minimum = np.maximum(coordinates.min(axis=0) - padding_voxels, 0)
    maximum = np.minimum(
        coordinates.max(axis=0) + 1 + padding_voxels,
        np.asarray(ct_array.shape),
    )

    crop_slices = tuple(
        slice(int(start), int(stop)) for start, stop in zip(minimum, maximum, strict=True)
    )
    raw_crop = ct_array[crop_slices]

    normalized_crop = clip_and_normalize(raw_crop)
    resized_crop = resample_to_shape(normalized_crop, target_shape)

    if resized_crop.shape != target_shape:
        raise RuntimeError("Crop resizing did not produce the required shape.")

    return resized_crop
