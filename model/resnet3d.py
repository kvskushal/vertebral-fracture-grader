"""A compact 3D ResNet-18-style classifier for Genant grades."""

from __future__ import annotations

from collections.abc import Sequence

import torch
from torch import nn

NUM_GENANT_GRADES = 4
EXPECTED_INPUT_SHAPE = (1, 64, 64, 64)


def _normalization(channels: int) -> nn.GroupNorm:
    """Create GroupNorm that remains stable with small 3D training batches."""
    for groups in (8, 4, 2, 1):
        if channels % groups == 0:
            return nn.GroupNorm(groups, channels)

    raise ValueError(f"Cannot select GroupNorm groups for {channels} channels.")


def _conv3x3(
    in_channels: int,
    out_channels: int,
    stride: int = 1,
) -> nn.Conv3d:
    """Return a padded 3D convolution that preserves size at stride one."""
    return nn.Conv3d(
        in_channels,
        out_channels,
        kernel_size=3,
        stride=stride,
        padding=1,
        bias=False,
    )


class BasicBlock3D(nn.Module):
    """Two-convolution residual block used by the 3D ResNet-18 backbone."""

    expansion = 1

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        stride: int = 1,
    ) -> None:
        super().__init__()

        self.conv1 = _conv3x3(in_channels, out_channels, stride)
        self.norm1 = _normalization(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = _conv3x3(out_channels, out_channels)
        self.norm2 = _normalization(out_channels)

        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv3d(
                    in_channels,
                    out_channels,
                    kernel_size=1,
                    stride=stride,
                    bias=False,
                ),
                _normalization(out_channels),
            )
        else:
            self.shortcut = nn.Identity()

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        """Apply the residual block."""
        identity = self.shortcut(inputs)

        output = self.conv1(inputs)
        output = self.norm1(output)
        output = self.relu(output)
        output = self.conv2(output)
        output = self.norm2(output)

        output = output + identity
        return self.relu(output)


class VertebraResNet3D(nn.Module):
    """Classify one normalized 64-cubed vertebra crop into grades 0-3."""

    def __init__(
        self,
        *,
        layers: Sequence[int] = (2, 2, 2, 2),
        base_channels: int = 32,
        num_classes: int = NUM_GENANT_GRADES,
        dropout: float = 0.2,
    ) -> None:
        super().__init__()

        if tuple(layers) != (2, 2, 2, 2):
            raise ValueError(
                "The Step 6C baseline requires ResNet-18 layers "
                "(2, 2, 2, 2)."
            )

        if base_channels <= 0:
            raise ValueError("base_channels must be positive.")

        if num_classes != NUM_GENANT_GRADES:
            raise ValueError(
                "The classifier must output four Genant-grade logits."
            )

        if not 0.0 <= dropout < 1.0:
            raise ValueError(
                "dropout must be at least 0 and less than 1."
            )

        self.in_channels = base_channels

        self.stem = nn.Sequential(
            nn.Conv3d(
                1,
                base_channels,
                kernel_size=7,
                stride=2,
                padding=3,
                bias=False,
            ),
            _normalization(base_channels),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=3, stride=2, padding=1),
        )

        self.layer1 = self._make_layer(
            base_channels,
            blocks=layers[0],
            stride=1,
        )
        self.layer2 = self._make_layer(
            base_channels * 2,
            blocks=layers[1],
            stride=2,
        )
        self.layer3 = self._make_layer(
            base_channels * 4,
            blocks=layers[2],
            stride=2,
        )
        self.layer4 = self._make_layer(
            base_channels * 8,
            blocks=layers[3],
            stride=2,
        )

        self.pool = nn.AdaptiveAvgPool3d(output_size=1)
        self.dropout = nn.Dropout(p=dropout)
        self.classifier = nn.Linear(
            base_channels * 8,
            num_classes,
        )

        self._initialize_weights()

    def _make_layer(
        self,
        out_channels: int,
        *,
        blocks: int,
        stride: int,
    ) -> nn.Sequential:
        layers = [
            BasicBlock3D(
                self.in_channels,
                out_channels,
                stride,
            )
        ]

        self.in_channels = out_channels

        layers.extend(
            BasicBlock3D(self.in_channels, out_channels)
            for _ in range(1, blocks)
        )

        return nn.Sequential(*layers)

    def _initialize_weights(self) -> None:
        for module in self.modules():
            if isinstance(module, nn.Conv3d):
                nn.init.kaiming_normal_(
                    module.weight,
                    mode="fan_out",
                    nonlinearity="relu",
                )
            elif isinstance(module, nn.GroupNorm):
                nn.init.ones_(module.weight)
                nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Linear):
                nn.init.normal_(
                    module.weight,
                    mean=0.0,
                    std=0.01,
                )
                nn.init.zeros_(module.bias)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        """Return four raw logits, one for each Genant grade."""
        if inputs.ndim != 5:
            raise ValueError(
                "Expected input shape [batch, 1, 64, 64, 64], "
                f"but received {tuple(inputs.shape)}."
            )

        if tuple(inputs.shape[1:]) != EXPECTED_INPUT_SHAPE:
            raise ValueError(
                f"Expected each crop to have shape "
                f"{EXPECTED_INPUT_SHAPE}, but received "
                f"{tuple(inputs.shape[1:])}."
            )

        output = self.stem(inputs)
        output = self.layer1(output)
        output = self.layer2(output)
        output = self.layer3(output)
        output = self.layer4(output)
        output = self.pool(output)
        output = torch.flatten(output, start_dim=1)
        output = self.dropout(output)

        return self.classifier(output)


def build_resnet18_3d() -> VertebraResNet3D:
    """Build the fixed Step 6C baseline model."""
    return VertebraResNet3D()


def count_trainable_parameters(model: nn.Module) -> int:
    """Count parameters that will be updated during training."""
    return sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )
