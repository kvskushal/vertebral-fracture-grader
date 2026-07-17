# NIfTI Loading and Alignment

A NIfTI file contains a three-dimensional image plus information describing its
physical position, direction, and voxel size.

## Why alignment checks matter

A CT and its segmentation mask can have the same number of pixels but still
point in different physical directions. Cropping them without checking could
produce the wrong vertebra.

Before cropping, the loader:

1. confirms that both files exist;
2. confirms that both files are three-dimensional;
3. converts both images to a standard canonical orientation;
4. compares their shapes;
5. compares their physical-coordinate matrices;
6. checks for invalid numerical values;
7. confirms that mask labels are integers; and
8. reads the physical voxel spacing.

If any check fails, that scan must be investigated instead of silently used.
