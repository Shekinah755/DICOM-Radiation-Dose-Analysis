"""
dicom_loader.py
----------------
Everything to do with GETTING dicom files into the program.
Nothing in here draws anything or touches the GUI - its only job is:
"find files, read them, hand back a dataset."
"""

import os
import pydicom
from pydicom.data import get_testdata_files


def get_sample_files():
    """Scan pydicom's own built-in sample folder and return a dict of
    {short filename: full path} for every sample file that actually
    contains image data (some samples are reports with no pixels)."""
    sample_paths = get_testdata_files("*.dcm")
    sample_files = {}
    for p in sample_paths:
        try:
            ds = pydicom.dcmread(p, stop_before_pixels=False)
            if "PixelData" in ds:
                sample_files[os.path.basename(p)] = p
        except Exception:
            pass  # skip any file pydicom can't read
    return sample_files


def load_dicom(path):
    """Read one DICOM file from disk and return the pydicom dataset."""
    return pydicom.dcmread(path)


def get_num_frames(ds):
    """How many frames/slices this single file contains. Most files
    have 1; a few (like emri_small.dcm) have several stacked inside."""
    return int(getattr(ds, "NumberOfFrames", 1))
