# Training Manifest

The manifest is a CSV table containing one row for every vertebra crop.

## Required columns

| Column | Meaning |
|---|---|
| patient_id | Anonymous dataset-specific patient code |
| scan_id | Anonymous scan code |
| vertebra | Vertebral level from T4 through L4 |
| genant_grade | Grade 0, 1, 2, or 3 |
| crop_path | Location of the derived 64x64x64 crop |
| source_dataset | Dataset from which the sample came |
| split | train, validation, or test |
| preprocessing_version | Version of the preprocessing rules |
| source_license | License inherited from the source dataset |

## Privacy rules

- Never place a person's name, date of birth, medical-record number, or address in the manifest.
- Use only the anonymous identifiers supplied by the public dataset.
- Do not upload raw CT scans or derived medical-image crops to GitHub.
- The manifest may be committed only when it contains anonymous public-dataset identifiers.
- Store actual crops in the Colab working directory or approved cloud storage.

## Patient-level splitting

All vertebrae belonging to one patient must receive the same split.

For example, if patient `verse019` has T10, T11, T12, and L1 crops, all four
must be placed in training, validation, or testing together.

The project uses these target proportions:

- Training: 70 percent
- Validation: 15 percent
- Testing: 15 percent

The split is stratified using each patient's highest Genant grade. This helps
keep fracture severities represented across the three groups.
