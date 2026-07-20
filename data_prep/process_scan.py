"""Convert one labeled VerSe scan into individual vertebra crops."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Final

import numpy as np
import pandas as pd

from data_prep.crop import extract_vertebra_crop
from data_prep.nifti_io import load_nifti_pair
from data_prep.preprocessing import CONFIG

LABEL_PATH: Final = Path(__file__).resolve().parents[1] / "configs" / "vertebra_labels.json"
SAFE_ID: Final = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

MANIFEST_COLUMNS: Final = [
    "patient_id",
    "scan_id",
    "vertebra",
    "genant_grade",
    "crop_path",
    "source_dataset",
    "split",
    "preprocessing_version",
    "source_license",
]
REJECTION_COLUMNS: Final = [
    "patient_id",
    "scan_id",
    "vertebra",
    "reason",
]


def process_verse_scan(
    ct_path: str | Path,
    mask_path: str | Path,
    patient_id: str,
    scan_id: str,
    grades: dict[str, int],
    output_directory: str | Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create crops, a manifest, and a rejection report for one scan."""
    for field_name, value in {"patient_id": patient_id, "scan_id": scan_id}.items():
        if not isinstance(value, str) or SAFE_ID.fullmatch(value) is None:
            raise ValueError(f"Unsafe {field_name}: {value}")

    with LABEL_PATH.open("r", encoding="utf-8") as label_file:
        label_map = json.load(label_file)["verse_multilabel"]

    pair = load_nifti_pair(ct_path, mask_path)
    output_root = Path(output_directory)
    patient_directory = output_root / patient_id
    patient_directory.mkdir(parents=True, exist_ok=True)

    manifest_rows = []
    rejection_rows = []

    for vertebra, grade in grades.items():
        if vertebra not in CONFIG["vertebrae"]:
            raise ValueError(f"Unsupported vertebra: {vertebra}")

        if not isinstance(grade, (int, np.integer)) or int(grade) not in {0, 1, 2, 3}:
            raise ValueError(f"Invalid Genant grade for {vertebra}: {grade}")

        label_value = int(label_map[vertebra])

        if not np.any(pair.segmentation_mask == label_value):
            rejection_rows.append(
                {
                    "patient_id": patient_id,
                    "scan_id": scan_id,
                    "vertebra": vertebra,
                    "reason": "missing_mask_label",
                }
            )
            continue

        crop = extract_vertebra_crop(
            pair.ct_volume,
            pair.segmentation_mask,
            label_value=label_value,
            spacing_mm=pair.spacing_mm,
        )

        relative_path = Path(patient_id) / f"{scan_id}_{vertebra}.npy"
        np.save(output_root / relative_path, crop, allow_pickle=False)

        manifest_rows.append(
            {
                "patient_id": patient_id,
                "scan_id": scan_id,
                "vertebra": vertebra,
                "genant_grade": int(grade),
                "crop_path": relative_path.as_posix(),
                "source_dataset": "verse19_loeffler",
                "split": "",
                "preprocessing_version": CONFIG["preprocessing_version"],
                "source_license": "CC BY-SA 4.0",
            }
        )

    # Build with explicit columns so an empty result (no valid vertebrae, or
    # no rejections) still has the correct schema instead of a column-less
    # DataFrame that breaks downstream validation and concatenation.
    manifest = pd.DataFrame(manifest_rows, columns=MANIFEST_COLUMNS)
    rejections = pd.DataFrame(rejection_rows, columns=REJECTION_COLUMNS)

    return manifest, rejections
