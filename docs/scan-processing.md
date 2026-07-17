# Scan-to-Crop Processing

This stage combines a CT, a matching VerSe segmentation mask, and Genant labels.

For each labeled vertebra, it creates:

- one normalized 64x64x64 NumPy crop;
- one anonymous manifest row; or
- one rejection row explaining why the crop was not produced.

Derived crop files contain medical-image information and must not be uploaded
to GitHub.
