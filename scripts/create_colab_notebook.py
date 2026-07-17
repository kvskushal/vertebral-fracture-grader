"""Generate the Google Colab data-preparation notebook."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path


def source_lines(text: str) -> list[str]:
    """Convert a block of text into notebook source lines."""
    cleaned = textwrap.dedent(text).strip()
    return [f"{line}\n" for line in cleaned.splitlines()]


def markdown_cell(text: str) -> dict:
    """Create one markdown notebook cell."""
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source_lines(text),
    }


def code_cell(text: str) -> dict:
    """Create one code notebook cell."""
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source_lines(text),
    }


cells = [
    markdown_cell(
        """
        # Vertebral Fracture Grader: Colab Data Preparation

        This notebook prepares T4-L4 vertebra crops for a research model.

        It is not a medical device and must not be used for clinical decisions.

        Raw CT archives remain in temporary Colab storage. Only anonymous,
        derived crops and manifests are saved to Google Drive.
        """
    ),
    code_cell(
        """
        import platform
        import subprocess
        import sys

        print("Python:", sys.version)
        print("System:", platform.platform())
        subprocess.run(["nvidia-smi"], check=False)
        """
    ),
    code_cell(
        """
        import os
        from pathlib import Path

        REPOSITORY_URL = "https://github.com/kvskushal/vertebral-fracture-grader.git"
        REPOSITORY_DIRECTORY = Path("/content/vertebral-fracture-grader")

        if REPOSITORY_DIRECTORY.exists():
            subprocess.run(
                ["git", "-C", str(REPOSITORY_DIRECTORY), "pull", "--ff-only"],
                check=True,
            )
        else:
            subprocess.run(
                ["git", "clone", REPOSITORY_URL, str(REPOSITORY_DIRECTORY)],
                check=True,
            )

        os.chdir(REPOSITORY_DIRECTORY)
        print("Repository:", Path.cwd())
        """
    ),
    code_cell(
        """
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                "requirements/colab.txt",
            ],
            check=True,
        )

        subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            check=True,
        )
        """
    ),
    code_cell(
        """
        from google.colab import drive

        drive.mount("/content/drive")

        TEMPORARY_WORK = Path("/content/medical-work")
        RAW_DIRECTORY = TEMPORARY_WORK / "raw"
        SEGMENTATION_DIRECTORY = TEMPORARY_WORK / "segmentations"

        DRIVE_OUTPUT = Path(
            "/content/drive/MyDrive/vertebral-fracture-grader"
        )
        CROP_DIRECTORY = DRIVE_OUTPUT / "crops"
        MANIFEST_DIRECTORY = DRIVE_OUTPUT / "manifests"
        QC_DIRECTORY = DRIVE_OUTPUT / "qc"

        for directory in (
            RAW_DIRECTORY,
            SEGMENTATION_DIRECTORY,
            CROP_DIRECTORY,
            MANIFEST_DIRECTORY,
            QC_DIRECTORY,
        ):
            directory.mkdir(parents=True, exist_ok=True)

        print("Temporary raw data:", RAW_DIRECTORY)
        print("Saved derived data:", DRIVE_OUTPUT)
        """
    ),
    code_cell(
        """
        from localization.totalsegmentator_adapter import (
            build_totalsegmentator_command,
        )

        RUN_SEGMENTATION = False
        CT_PATH = RAW_DIRECTORY / "replace-with-real-scan.nii.gz"
        SCAN_SEGMENTATION_DIRECTORY = SEGMENTATION_DIRECTORY / "example-scan"

        if RUN_SEGMENTATION:
            if not CT_PATH.is_file():
                raise FileNotFoundError(CT_PATH)

            command = build_totalsegmentator_command(
                CT_PATH,
                SCAN_SEGMENTATION_DIRECTORY,
                device="gpu",
            )
            print("Running:", " ".join(command))
            subprocess.run(command, check=True)
        else:
            print(
                "Segmentation is disabled. Set CT_PATH and then change "
                "RUN_SEGMENTATION to True."
            )
        """
    ),
    code_cell(
        """
        # Run this only after the Stage A segmentation cell succeeds.

        from localization.totalsegmentator_adapter import (
            merge_binary_vertebra_masks,
        )

        MERGED_MASK_PATH = (
            SEGMENTATION_DIRECTORY / "example-scan-merged.nii.gz"
        )

        if RUN_SEGMENTATION:
            merge_binary_vertebra_masks(
                CT_PATH,
                SCAN_SEGMENTATION_DIRECTORY,
                MERGED_MASK_PATH,
            )
            print("Merged mask:", MERGED_MASK_PATH)
        """
    ),
    markdown_cell(
        """
        ## Next action

        1. Download one approved public dataset split into temporary storage.
        2. Select one scan.
        3. Set `CT_PATH`.
        4. Change `RUN_SEGMENTATION` to `True`.
        5. Inspect the segmentation and crop preview.
        6. Do not begin full processing until the one-scan test passes.
        """
    ),
]

notebook = {
    "cells": cells,
    "metadata": {
        "accelerator": "GPU",
        "colab": {
            "name": "01_colab_data_prep.ipynb",
            "provenance": [],
        },
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

output_path = Path("notebooks/01_colab_data_prep.ipynb")
output_path.write_text(
    json.dumps(notebook, indent=2),
    encoding="utf-8",
)
print(f"Created {output_path}")
