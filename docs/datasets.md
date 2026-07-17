# Dataset Plan

Last verified: 2026-07-17

## Safety and storage rules

- Do not commit CT scans, segmentation masks, patient information, or model checkpoints to Git.
- Download and process full datasets only in Google Colab.
- Keep only small 64x64x64 derived vertebra crops in approved cloud storage.
- Use patient-level identifiers to prevent the same patient from appearing in multiple splits.
- Record the source dataset for every derived crop.
- This repository is for research and education, not clinical diagnosis.

## Important dataset overlap

The Loffler 2020 fracture-grading paper points to the same OSF project used for
VerSe 2019. They must be treated as one underlying dataset, not two independent
patient collections.

## Dataset inventory

| Dataset | Provides | Genant grades | Intended use | Data license |
|---|---|---:|---|---|
| VerSe 2019 / Loffler | CT, vertebra masks, labels and fracture metadata | Yes | Primary grading and localization | CC BY-SA 4.0 |
| xVertSeg v1 | Lumbar CT, masks and fracture scores | Yes | Supplemental grading data | CC BY-NC-ND |
| VerSe 2020 | CT, vertebra masks and centroid labels | No confirmed grading labels | Optional localization robustness | CC BY-SA 4.0 |
| CTSpine1K | 1,005 CT volumes with vertebra segmentations | No | Optional localization robustness | CC BY-NC-SA 4.0 |
| VinDr-SpineXR | Two-dimensional spine X-rays | Not part of core CT labels | Excluded from the core pipeline | Check before optional use |

## Official sources

### VerSe 2019 and 2020

- Repository: https://github.com/anjany/verse
- VerSe 2019 OSF: https://osf.io/nqjyw/
- VerSe 2020 OSF: https://osf.io/t98fz/
- Official repository lists the dataset license as CC BY-SA 4.0.
- The repository code uses a separate MIT license.

### Loffler fracture-grading publication

- Paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC8082364/
- The paper describes 160 CT image series from 141 patients.
- It includes per-vertebra Genant grading metadata.
- The article is CC BY 4.0; the dataset license is recorded separately above.

### xVertSeg v1

- Official source: https://lit.fe.uni-lj.si/en/research/resources/xVertSeg/
- License: CC BY-NC-ND.
- The official download is divided into five archive parts.
- It cannot be used commercially or redistributed as a modified dataset.

### CTSpine1K

- Repository: https://github.com/MIRACLE-Center/CTSpine1K
- Contains 1,005 CT volumes from several source collections.
- License: CC BY-NC-SA 4.0.
- It has segmentation labels but no Genant fracture grades.

## Staged download plan

1. Start with VerSe 2019 / Loffler because it contains the primary Genant labels.
2. Add xVertSeg as supplemental graded data.
3. Process one archive or split at a time in Colab.
4. Delete temporary raw archives after the files are verified and converted.
5. Delay VerSe 2020 and CTSpine1K until the basic grading pipeline works.
6. Never upload raw medical images to GitHub.

## Required provenance for every training sample

Every derived crop must record:

- anonymized patient ID
- source dataset
- original scan ID
- vertebral level
- Genant grade
- crop file path
- patient-level split
- preprocessing version
- source license
