# Stage A Localization

Stage A finds and labels vertebrae T4 through L4.

## Tool

The project uses the open `total` task from TotalSegmentator. The main task is
available under Apache 2.0.

TotalSegmentator is not installed on the local laptop. It will run on a Colab
GPU when real scans are processed.

## Command design

The adapter requests only T4 through L4.

It uses:

- normal resolution rather than `--fast`;
- `--roi_subset` to reduce memory and runtime;
- `--robust_crop` to reduce cut-off masks;
- `--report` to record processing information; and
- separate binary masks instead of version-dependent class numbers.

## Validation

Before combining the masks, the adapter verifies:

- every requested mask exists;
- every mask matches the CT shape;
- physical coordinates match;
- mask values are binary; and
- masks do not overlap.

This is a research pipeline and is not a medical device.
