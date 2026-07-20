# Vertebral Fracture Grader: Design Document

Status: Approved

---

## 1. Objective

Build a research system that receives a non-contrast CT volume and returns
a Genant grade from 0 through 3 for every detected vertebra from T4
through L4.

Genant grades:

| Grade | Meaning | Height loss |
|---|---|---:|
| 0 | Normal | Less than 20% |
| 1 | Mild | 20% to less than 25% |
| 2 | Moderate | 25% to less than 40% |
| 3 | Severe | At least 40% |

The system is for research and testing. It is not a medical device and
must not be used to make clinical decisions without additional validation
and regulatory approval.

---

## 2. Input and output

### Complete system input

A non-contrast CT volume supplied as:

- A NIfTI file, or
- A directory containing one DICOM CT series

The currently implemented preprocessing handles NIfTI pairs (CT volume
plus segmentation mask). DICOM-directory support is planned but not yet
implemented end-to-end.

### Complete system output

The inference function will return one record for each vertebra:

```python
[
    {
        "vertebra": "T12",
        "genant_grade": 0,
        "confidence": 0.97,
        "status": "ok"
    },
    {
        "vertebra": "L1",
        "genant_grade": 2,
        "confidence": 0.91,
        "status": "ok"
    }
]
```

The public API signature is:

```python
def grade_vertebrae(ct_volume_path: str) -> list[dict]:
    ...
```

---

## 3. System architecture

```text
Non-contrast CT volume
        |
        v
Stage A: vertebra localization and labeling
        |
        v
T4-L4 masks / regions of interest
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

### Stage A — localization and labeling

Chosen approach: use the open `total` task from TotalSegmentator rather
than training a new nnU-Net immediately.

Reasons:

- The user has no local NVIDIA GPU, ruling out practical local
  segmentation-model training.
- TotalSegmentator gives named vertebral masks out of the box.
- It reduces the amount of custom segmentation training needed before the
  grading model can be tested end to end.
- The main `total` task is Apache-2.0 licensed.

Command design decisions:

- Request only T4–L4 with `--roi_subset`.
- Use normal resolution; do not use `--fast`, because compression
  morphology matters for fracture grading.
- Use `--robust_crop` to reduce cut-off segmentations.
- Request `--report` for reproducibility.
- Use separate named binary masks (`vertebrae_T4.nii.gz`, etc.) rather
  than relying on version-sensitive multilabel indices.
- Merge binary masks into the stable VerSe-style numerical labels expected
  by the cropper (T4–T12: labels 11–19; L1–L4: labels 20–23).

Training scans that already include correct VerSe masks do not need
TotalSegmentator masks. TotalSegmentator is mainly for inference and for
datasets without appropriate labels.

Before batch use, TotalSegmentator must be validated on one real scan:
visually inspect the T4–L4 masks and check for mislabeled or partial
vertebrae.

### Stage B — grading classifier

Planned approach: a 3D CNN, beginning with a 3D ResNet-18-style baseline.

Do not use an RNN. CT is spatial 3D data, not sequential data.

The final loss must understand that the grades are ordered. Predicting
grade 0 for a true grade 3 must be penalized more than predicting grade 2
for a true grade 3.

Stage B tensor contract:

```text
Input shape:     [B, 1, 64, 64, 64]
Single item:     [1, 1, 64, 64, 64]
Input dtype:     float32
Input range:     [0, 1]
Output:          4 logits corresponding to grades 0, 1, 2, 3
Predicted grade: argmax(logits)
```

### Class imbalance

Grade 0 will dominate the dataset. Planned mitigation:

- class-weighted loss or a focal-loss component;
- oversampling fractured vertebrae;
- reporting per-grade metrics, not only overall accuracy.

---

## 4. Preprocessing contract

Training and inference must call the same preprocessing implementation
and configuration.

- HU clip: `[-200, 1000]`.
- Normalize clipped values to `[0, 1]`.
- Crop shape: `64 x 64 x 64`.
- Crop padding: `10 mm`.
- Target vertebrae: T4–T12 and L1–L4 (13 total).
- Version string: `v1_hu-200_1000_crop64_pad10mm`.

---

## 5. Data plan

### Primary graded data

1. **VerSe 2019 / Löffler fracture-grading dataset** — same underlying OSF
   project; do not count it twice. Primary grading and localization
   source. CT, vertebra masks/labels, and per-vertebra Genant metadata.
   License: CC BY-SA 4.0. OSF: https://osf.io/nqjyw/
2. **xVertSeg v1** — supplemental lumbar CT, masks, and fracture scores.
   License: CC BY-NC-ND. Official source:
   https://lit.fe.uni-lj.si/en/research/resources/xVertSeg/. The archive is
   divided into five parts.

### Optional localization robustness data (deferred)

3. **VerSe 2020** — segmentation/centroid labels; no confirmed Genant
   labels in the project registry. CC BY-SA 4.0.
4. **CTSpine1K** — 1,005 CT volumes and vertebral segmentations; no Genant
   grades. CC BY-NC-SA 4.0. Large; deferred.

### Excluded from the core pipeline

- **VinDr-SpineXR** is 2D X-ray data, while the required core model is 3D
  CT. It is optional and currently excluded.

### Data rules

- Do not put medical images or derived crops in GitHub.
- Preserve anonymous public-dataset identifiers only.
- Every sample must record source dataset, scan ID, patient ID, vertebral
  level, grade, preprocessing version, crop path, split, and source
  license.
- Split by patient, not vertebra.
- Do not include names, dates of birth, MRNs, or addresses anywhere in
  derived data.

---

## 6. Training plan

- Framework: PyTorch + MONAI on Google Colab.
- Baseline network: a 3D ResNet-18-style model (not yet implemented).
- Optimizer: AdamW.
- Initial learning rate: `3e-4`.
- Scheduler: cosine decay.
- Planned maximum: 150 epochs, with checkpoints/early stopping as
  appropriate.
- The initial baseline may use weighted cross-entropy so the pipeline can
  be tested end to end.
- The final model must use an ordinal-aware objective (CORAL, CORN, or a
  grading loss) and class-imbalance handling.
- Suggested augmentation: flips, small rotations, light elastic
  deformation, intensity jitter.
- Fixed random seed.
- Patient-level splits only; never split by individual vertebra.

---

## 7. Evaluation plan

- Primary metric: quadratic-weighted Cohen's kappa.
- 4x4 confusion matrix.
- Binary fracture detection (grade 0 vs grade >=1): sensitivity,
  specificity, ROC-AUC.
- Clinically actionable threshold (grade >=2): sensitivity target
  >=0.85.
- Implement a simple morphometric height-loss baseline, computed from the
  original mask geometry and voxel spacing (not from the resampled 64³
  crop), and compare it against the CNN.
- Report results at patient-level held-out testing, with no leakage.

---

## 8. Export plan

- Export the final trained classifier as TorchScript.
- Document the exact I/O contract.
- Produce `grade_vertebrae(ct_volume_path: str) -> list[dict]`.
- Include an evaluation report, dataset provenance/licenses, reproduction
  commands, and cleanup instructions.

---

## 9. Environment and compute

- Local laptop: Windows PowerShell, Python 3.10, no NVIDIA GPU
  (Intel Iris Xe only), limited free disk space (~20 GB).
- Do not install PyTorch, MONAI, or TotalSegmentator locally.
- Use Google Colab for GPU work, dataset processing, and training.
- Use temporary Colab storage for raw archives and masks; these do not
  persist across sessions.
- Use Google Drive only for anonymous derived crops, manifests, selected
  checkpoints, QC images, and final results.
- Process one archive or split at a time and delete verified temporary raw
  files to control local and Colab storage.

---

## 10. Out of scope for the initial version

- Cervical vertebrae (C1–C7) and sacral vertebrae are not graded.
- DICOM-series input is a target but not yet implemented.
- Clinical deployment, regulatory submission, and integration with
  hospital systems are explicitly out of scope for this research
  prototype.
