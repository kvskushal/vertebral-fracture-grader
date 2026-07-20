# Vertebral Fracture Grader

A research pipeline that takes a non-contrast CT volume and predicts a
[Genant semi-quantitative fracture grade](#genant-grading-standard) (0–3)
for each thoracolumbar vertebra from **T4 through L4**.

> **Research and educational prototype only.** This is **not** a medical
> device and must not be used for clinical decisions without external
> clinical validation, regulatory review, and appropriate oversight.

---

## What it does

The system runs in two stages:

```
Non-contrast CT volume
        |
        v
Stage A: vertebra localization and labeling  (TotalSegmentator "total" task)
        |
        v
T4–L4 masks / regions of interest
        |
        v
Preprocessing and 64 x 64 x 64 crops
        |
        v
Stage B: 3D CNN ordinal classifier
        |
        v
Grade 0, 1, 2, or 3 per vertebra + confidence
```

The intended public inference API is:

```python
def grade_vertebrae(ct_volume_path: str) -> list[dict]:
    # Each result:
    # {"vertebra": "L1", "genant_grade": 2, "confidence": 0.91, "status": "ok"}
    ...
```

---

## Genant grading standard

| Grade | Meaning  | Vertebral height loss    |
| ----: | -------- | ------------------------ |
|     0 | Normal   | less than 20%            |
|     1 | Mild     | 20% to less than 25%     |
|     2 | Moderate | 25% to less than 40%     |
|     3 | Severe   | at least 40%             |

Grade boundaries are treated as: grade 1 = `>=20% and <25%`,
grade 2 = `>=25% and <40%`, grade 3 = `>=40%`.

---

## Project status

This project is being built in stages. The **data-preparation pipeline is
complete and tested**; the **modeling and evaluation stages are not yet
built**.

| Step | Description | Status |
| ---- | ----------- | ------ |
| 1 | Project and GitHub setup | ✅ Complete |
| 2 | Literature review and design | ✅ Written (docs being cleaned up) |
| 3 | Lightweight local Python environment | ✅ Complete |
| 4 | Dataset registry, provenance, patient-level splitting | ✅ Complete |
| 5 | NIfTI loading, crop generation, QC, TotalSegmentator adapter, Colab prep | ✅ Complete |
| 6 | Model training (dataset loader → model → baseline → ordinal loss) | 🚧 Not started in repo |
| 7 | Evaluation and morphometric baseline | ⬜ Not started |
| 8 | TorchScript export, inference API, final report, cleanup | ⬜ Not started |

What currently exists in this repository is the full pre-training path:
dataset registry and licensing plan, patient-level manifest validation and
splitting, NIfTI loading with affine/shape checks, HU clipping and
normalization, fixed-size crop extraction, crop quality-control previews, the
TotalSegmentator command builder and mask merger, and a generated Colab
data-preparation notebook — all with unit tests.

The `model/`, `inference/` directories currently contain only placeholders.
No trained weights, evaluation results, or inference API exist yet.

---

## Repository layout

```
configs/            Preprocessing constants and vertebra label maps (JSON)
data_prep/          NIfTI I/O, preprocessing, cropping, manifest, QC, registry
localization/       Stage A — TotalSegmentator adapter (command + mask merge)
model/              Stage B — 3D CNN (placeholder; not yet implemented)
inference/          Final grade_vertebrae() API (placeholder)
notebooks/          Generated Colab notebook for data preparation
scripts/            Helper scripts (e.g. notebook generation)
docs/               Design doc, literature review, and per-module docs
tests/              Pytest suite covering the pre-training path
requirements/       local-dev, local-lock, and Colab dependency lists
```

---

## Preprocessing contract

Training and inference must use the same preprocessing implementation and
configuration (`configs/preprocessing.json`,
version `v1_hu-200_1000_crop64_pad10mm`):

- HU clip: `[-200, 1000]`
- Normalize clipped values to `[0, 1]`
- Crop shape: `64 x 64 x 64`, padding `10 mm`
- Target vertebrae: T4–T12 and L1–L4 (13 total)

Stage B tensor contract:

```
Input shape:     [B, 1, 64, 64, 64]   (float32, range [0, 1])
Output:          4 logits for grades 0, 1, 2, 3
Predicted grade: argmax(logits)
```

---

## Setup (local development)

The laptop this was built on has no NVIDIA GPU, so **local work is limited to
source code and small tests**. GPU work (dataset processing and training)
happens on Google Colab. Do **not** install PyTorch, MONAI, or
TotalSegmentator locally.

```powershell
# From the project root, in Windows PowerShell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements/local-dev.txt
```

Run the checks:

```powershell
ruff check .
pytest
```

`requirements/local-lock.txt` records exact pinned versions for a reproducible
local environment.

## Setup (Colab, for GPU work)

Data preparation and training run on Colab with a GPU runtime. See
[`docs/colab-data-prep.md`](docs/colab-data-prep.md) and
[`notebooks/01_colab_data_prep.ipynb`](notebooks/01_colab_data_prep.ipynb).
Colab dependencies are in `requirements/colab.txt`.

---

## Data and privacy

Medical images and derived crops are **never** committed to this repository
(see `.gitignore`). Datasets are downloaded into temporary Colab storage or
approved Google Drive storage.

| Dataset | Role | License |
| ------- | ---- | ------- |
| VerSe 2019 / Löffler | Primary grading + localization | CC BY-SA 4.0 |
| xVertSeg v1 | Supplemental lumbar CT + fracture scores | CC BY-NC-ND |
| VerSe 2020 | Optional localization robustness | CC BY-SA 4.0 |
| CTSpine1K | Deferred (segmentation only, no grades) | CC BY-NC-SA 4.0 |

Rules: split by **patient**, never by vertebra; store only anonymous public
dataset identifiers; never include names, dates of birth, MRNs, or addresses.
See [`docs/datasets.md`](docs/datasets.md) for provenance and the registry.

---

## Documentation

- [`docs/design.md`](docs/design.md) — approved system design
- [`docs/literature_review.md`](docs/literature_review.md) — background and prior work
- [`docs/datasets.md`](docs/datasets.md) — dataset provenance and licensing
- [`docs/nifti-loading.md`](docs/nifti-loading.md), [`docs/cropping.md`](docs/cropping.md), [`docs/scan-processing.md`](docs/scan-processing.md), [`docs/quality-control.md`](docs/quality-control.md), [`docs/localization.md`](docs/localization.md), [`docs/manifest.md`](docs/manifest.md) — per-module notes

---

## License

Source code license: to be finalized. Dataset licenses are listed above and
must be respected independently of the code license.
