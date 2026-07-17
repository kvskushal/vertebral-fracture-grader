# Crop Quality Control

Every model learns from the crop files it receives. Incorrect crops can teach
the model incorrect information even when their grades are correct.

## Preview

The preview displays the center of a 64x64x64 crop from three directions:

- sagittal: viewed from the side;
- coronal: viewed from the front;
- axial: viewed from above or below.

## Human inspection checklist

Check that:

- the intended vertebra is visible;
- the vertebral body is near the center;
- the entire vertebra is included;
- the crop is not empty;
- neighboring anatomy does not fill most of the image;
- the image is not flipped or badly stretched;
- the mask did not select the wrong vertebral level; and
- severe fractures have not been cropped away.

Inspect every grade-2 and grade-3 sample. Also inspect a random selection of
grade-0 and grade-1 samples from every source dataset.

A failed sample must be recorded in the rejection report and excluded from
training until corrected.

## Privacy

Quality-control PNG files still contain derived medical-image information.
Store them in the ignored `qc` directory and never upload them to GitHub.
