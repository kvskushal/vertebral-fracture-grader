# Google Colab Data Preparation

The local laptop does not have enough storage or GPU power for full CT
processing. Large-data work will run in Google Colab.

## Storage arrangement

### Temporary Colab storage

Use `/content/medical-work` for:

- downloaded archives;
- extracted raw CT files;
- temporary segmentation masks; and
- model caches.

These files disappear when the Colab session ends.

### Google Drive

Use the `vertebral-fracture-grader` folder in Google Drive for:

- anonymous 64x64x64 crops;
- manifests;
- rejection tables;
- quality-control previews;
- trained model checkpoints; and
- final evaluation results.

## Important rules

- Process one archive or dataset split at a time.
- Verify saved crops before deleting temporary files.
- Never push CT scans, crops, masks, or checkpoints to GitHub.
- Never place names or medical-record numbers in filenames.
- Stop if the CT and mask do not align.
- Inspect one complete scan before starting batch processing.
- Colab GPU access and session duration are not guaranteed.

## Notebook

The generated notebook is:

`notebooks/01_colab_data_prep.ipynb`

It initially leaves real segmentation disabled. The user must supply an
approved CT path and deliberately enable the segmentation cell.
