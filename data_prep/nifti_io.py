"""Safe loading and alignment checks for NIfTI CT and mask files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import nibabel as nib
import numpy as np


@dataclass(frozen=True)
class NiftiPair:
    """An aligned CT volume, segmentation mask, and physical metadata."""

    ct_volume: np.ndarray
    segmentation_mask: np.ndarray
    spacing_mm: tuple[float, float, float]
    affine: np.ndarray


def _load_canonical_image(path: Path) -> nib.Nifti1Image:
    """Load one NIfTI image and convert it to a standard orientation."""
    if not path.is_file():
        raise FileNotFoundError(f"NIfTI file does not exist: {path}")

    image = nib.load(str(path))

    if len(image.shape) != 3:
        raise ValueError(f"NIfTI image must be 3-dimensional: {path}")

    return nib.as_closest_canonical(image)


def load_nifti_pair(
    ct_path: str | Path,
    mask_path: str | Path,
    affine_tolerance: float = 0.001,
) -> NiftiPair:
    """Load a CT and mask only when their voxel grids correctly match."""
    ct_image = _load_canonical_image(Path(ct_path))
    mask_image = _load_canonical_image(Path(mask_path))

    if ct_image.shape != mask_image.shape:
        raise ValueError(f"CT and mask shapes differ: {ct_image.shape} versus {mask_image.shape}.")

    if not np.allclose(
        ct_image.affine,
        mask_image.affine,
        rtol=0.0,
        atol=affine_tolerance,
    ):
        raise ValueError("CT and mask physical coordinates do not match.")

    ct_volume = np.asarray(ct_image.dataobj, dtype=np.float32)
    raw_mask = np.asarray(mask_image.dataobj)

    if not np.isfinite(ct_volume).all():
        raise ValueError("CT volume contains NaN or infinite values.")

    if not np.isfinite(raw_mask).all():
        raise ValueError("Segmentation mask contains NaN or infinite values.")

    rounded_mask = np.rint(raw_mask)
    if not np.allclose(raw_mask, rounded_mask, rtol=0.0, atol=0.0001):
        raise ValueError("Segmentation mask contains non-integer label values.")

    spacing_values = np.asarray(ct_image.header.get_zooms()[:3], dtype=np.float32)
    if not np.isfinite(spacing_values).all() or np.any(spacing_values <= 0):
        raise ValueError("NIfTI voxel spacing must be finite and positive.")

    spacing_mm = tuple(float(value) for value in spacing_values)

    return NiftiPair(
        ct_volume=ct_volume,
        segmentation_mask=rounded_mask.astype(np.int16),
        spacing_mm=spacing_mm,
        affine=np.asarray(ct_image.affine, dtype=np.float64),
    )
