"""Tests for the 3D ResNet Genant-grade classifier."""

import pytest
import torch

from model import (
    NUM_GENANT_GRADES,
    VertebraResNet3D,
    build_resnet18_3d,
    count_trainable_parameters,
)


def test_resnet_accepts_crop_batch_and_returns_four_logits() -> None:
    model = build_resnet18_3d()
    model.eval()

    crops = torch.rand(2, 1, 64, 64, 64)

    with torch.inference_mode():
        logits = model(crops)

    assert logits.shape == (2, NUM_GENANT_GRADES)
    assert torch.isfinite(logits).all()


def test_resnet_has_expected_parameter_scale() -> None:
    parameter_count = count_trainable_parameters(
        build_resnet18_3d()
    )

    assert 8_000_000 < parameter_count < 9_000_000


@pytest.mark.parametrize(
    "bad_shape",
    [
        (1, 64, 64, 64),
        (2, 3, 64, 64, 64),
        (2, 1, 32, 64, 64),
    ],
)
def test_resnet_rejects_wrong_input_shape(
    bad_shape: tuple[int, ...],
) -> None:
    model = build_resnet18_3d()
    crops = torch.rand(bad_shape)

    with pytest.raises(ValueError, match="Expected"):
        model(crops)


def test_resnet_rejects_non_four_class_configuration() -> None:
    with pytest.raises(
        ValueError,
        match="four Genant-grade logits",
    ):
        VertebraResNet3D(num_classes=3)
