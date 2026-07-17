# Vertebra Crop Generation

## Purpose

The classifier receives one vertebra at a time instead of an entire CT scan.

For each vertebra from T4 through L4, the cropper:

1. finds its segmentation label;
2. adds 10 mm of surrounding context;
3. clips intensities to -200 through 1000 HU;
4. normalizes intensities to 0 through 1; and
5. resizes the result to 64x64x64.

## Supported mask formats

### VerSe masks

VerSe stores several vertebrae in one labeled mask. The numerical label map is
stored in `configs/vertebra_labels.json`.

### TotalSegmentator masks

The main TotalSegmentator task can create an individual binary NIfTI file for
each vertebra. The project uses named files such as `vertebrae_T4.nii.gz`
instead of relying on version-dependent multilabel indices.

TotalSegmentator will be installed and executed in Google Colab, not on the
local laptop.

## Important checks

Before cropping a real scan:

- Convert the CT and mask to the same canonical orientation.
- Confirm that their shapes and physical coordinates match.
- Visually inspect sample masks overlaid on the CT.
- Reject missing, partial, mislabeled, or badly segmented vertebrae.
- Keep a rejection reason in the sample manifest.
