"""Tests for the generated Colab notebook."""

import json
from pathlib import Path


def test_colab_notebook_contains_required_steps() -> None:
    notebook_path = Path("notebooks/01_colab_data_prep.ipynb")
    assert notebook_path.is_file()

    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    code_text = "\n".join(
        "".join(cell["source"]) for cell in notebook["cells"] if cell["cell_type"] == "code"
    )

    assert "nvidia-smi" in code_text
    assert "drive.mount" in code_text
    assert "build_totalsegmentator_command" in code_text
    assert "RUN_SEGMENTATION = False" in code_text
