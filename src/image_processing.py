"""
image_processing.py
---------------------
Turns raw DICOM pixel data into a normal, viewable grayscale image.

Pipeline:
    raw pixels -> Rescale Slope/Intercept -> true Hounsfield Units
               -> clip to HU window -> scale to 0-255
"""

import numpy as np


def get_frame_array(ds, index):
    """Return the raw pixel array for one frame. If the file has more
    than one frame stacked inside it, index into that stack."""
    arr = ds.pixel_array
    if int(getattr(ds, "NumberOfFrames", 1)) > 1:
        return arr[index]
    return arr


def windowed_image(ds, index, hu_min, hu_max):
    """Convert one frame into a 0-255 grayscale image using the given
    HU window (min/max). This is the contrast-adjustment step."""
    img = get_frame_array(ds, index).astype(float)

    slope = float(getattr(ds, "RescaleSlope", 1))
    intercept = float(getattr(ds, "RescaleIntercept", 0))
    img = img * slope + intercept           # convert to true Hounsfield Units

    img = np.clip(img, hu_min, hu_max)       # throw away anything outside the window
    rng = (hu_max - hu_min) or 1             # avoid divide-by-zero
    img = (img - hu_min) / rng * 255         # rescale to 0-255

    if getattr(ds, "PhotometricInterpretation", "") == "MONOCHROME1":
        img = 255 - img                      # some files store brightness inverted

    return img.astype(np.uint8)
