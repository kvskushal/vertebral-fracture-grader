"""Create three-view quality-control previews of vertebra crops."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


def save_crop_preview(
    crop: np.ndarray,
    output_path: str | Path,
    title: str = "Vertebra crop",
) -> Path:
    """Save sagittal, coronal, and axial center slices as one PNG."""
    array = np.asarray(crop, dtype=np.float32)

    if array.ndim != 3:
        raise ValueError("A preview requires a three-dimensional crop.")

    if not np.isfinite(array).all():
        raise ValueError("Crop contains NaN or infinite values.")

    if array.min() < 0.0 or array.max() > 1.0:
        raise ValueError("Crop must be normalized to the range 0 through 1.")

    center_x, center_y, center_z = (size // 2 for size in array.shape)

    views = [
        ("Sagittal", array[center_x, :, :].T),
        ("Coronal", array[:, center_y, :].T),
        ("Axial", array[:, :, center_z].T),
    ]

    figure, axes = plt.subplots(1, 3, figsize=(9, 3))

    for axis, (view_name, image) in zip(axes, views, strict=True):
        axis.imshow(
            image,
            cmap="gray",
            origin="lower",
            vmin=0.0,
            vmax=1.0,
        )
        axis.set_title(view_name)
        axis.axis("off")

    figure.suptitle(title)
    figure.tight_layout()

    preview_path = Path(output_path)
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(preview_path, dpi=150, bbox_inches="tight")
    plt.close(figure)

    return preview_path
