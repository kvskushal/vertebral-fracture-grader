"""Tests for the dataset registry."""

from data_prep.dataset_registry import load_dataset_registry


def test_dataset_registry_is_valid() -> None:
    registry = load_dataset_registry()
    assert len(registry["datasets"]) == 4


def test_primary_dataset_has_genant_grades() -> None:
    registry = load_dataset_registry()
    datasets = {dataset["id"]: dataset for dataset in registry["datasets"]}

    primary = datasets["verse19_loeffler"]
    assert primary["has_genant_grades"] is True
    assert "primary_grading" in primary["roles"]


def test_large_dataset_is_deferred() -> None:
    registry = load_dataset_registry()
    datasets = {dataset["id"]: dataset for dataset in registry["datasets"]}

    assert datasets["ctspine1k"]["access_status"] == "deferred"
