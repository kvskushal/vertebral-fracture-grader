"""Load and validate the dataset provenance registry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REGISTRY_PATH = Path(__file__).with_name("dataset_registry.json")
REQUIRED_FIELDS = {
    "id",
    "name",
    "official_url",
    "license",
    "roles",
    "has_genant_grades",
    "download_policy",
    "access_status",
    "priority",
    "notes",
}


def load_dataset_registry(path: Path | None = None) -> dict[str, Any]:
    """Load the dataset registry from JSON."""
    registry_path = path or REGISTRY_PATH
    with registry_path.open("r", encoding="utf-8") as registry_file:
        registry = json.load(registry_file)

    validate_dataset_registry(registry)
    return registry


def validate_dataset_registry(registry: dict[str, Any]) -> None:
    """Check that dataset records contain required provenance information."""
    datasets = registry.get("datasets")

    if not isinstance(datasets, list) or not datasets:
        raise ValueError("The registry must contain a non-empty datasets list.")

    dataset_ids: list[str] = []

    for dataset in datasets:
        missing = REQUIRED_FIELDS.difference(dataset)
        if missing:
            missing_text = ", ".join(sorted(missing))
            raise ValueError(f"Dataset record is missing: {missing_text}")

        dataset_ids.append(dataset["id"])

        if dataset["download_policy"] != "colab_only":
            raise ValueError("Full medical datasets must use the colab_only policy.")

    if len(dataset_ids) != len(set(dataset_ids)):
        raise ValueError("Dataset IDs must be unique.")
