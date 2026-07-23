"""PyTorch dataset for processed vertebra crops."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset

from data_prep.manifest import validate_manifest
from data_prep.preprocessing import CONFIG

EXPECTED_SHAPE = tuple(CONFIG["crop_shape"])


class VertebraDataset(Dataset):
    """Load normalized vertebra crops and their Genant grades."""

    def __init__(
        self,
        manifest: pd.DataFrame,
        crop_root: str | Path,
        transform: Callable | None = None,
    ) -> None:
        validate_manifest(manifest)

        self.manifest = manifest.reset_index(drop=True).copy()
        self.crop_root = Path(crop_root).expanduser().resolve()
        self.transform = transform

        if not self.crop_root.is_dir():
            raise NotADirectoryError(f"Crop directory does not exist: {self.crop_root}")

    def __len__(self) -> int:
        return len(self.manifest)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        row = self.manifest.iloc[index]
        relative_path = Path(row["crop_path"])

        if relative_path.is_absolute():
            raise ValueError("crop_path must be relative to crop_root.")

        crop_path = (self.crop_root / relative_path).resolve()

        if not crop_path.is_relative_to(self.crop_root):
            raise ValueError("crop_path cannot leave crop_root.")

        if not crop_path.is_file():
            raise FileNotFoundError(f"Crop file does not exist: {crop_path}")

        crop = np.load(crop_path, allow_pickle=False)

        if crop.shape != EXPECTED_SHAPE:
            raise ValueError(
                f"Expected crop shape {EXPECTED_SHAPE}, but received {crop.shape}: {crop_path}"
            )

        if crop.dtype != np.float32:
            raise ValueError(f"Crop must use float32, but received {crop.dtype}: {crop_path}")

        if not np.isfinite(crop).all():
            raise ValueError(f"Crop contains NaN or infinity: {crop_path}")

        if crop.min() < 0.0 or crop.max() > 1.0:
            raise ValueError(f"Crop values must be normalized between 0 and 1: {crop_path}")

        crop_tensor = torch.from_numpy(np.array(crop, dtype=np.float32, copy=True)).unsqueeze(0)

        if self.transform is not None:
            crop_tensor = self.transform(crop_tensor)

        grade = int(row["genant_grade"])

        if grade not in {0, 1, 2, 3}:
            raise ValueError(f"Invalid Genant grade: {grade}")

        grade_tensor = torch.tensor(grade, dtype=torch.long)
        return crop_tensor, grade_tensor
