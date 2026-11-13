"""
exporters.py
-------------
Everything whose job is "take something from the app and save it
somewhere" - PNG, JPEG, PDF, MP4 video, and the raw/anonymized DICOM
file itself.
"""

import numpy as np
from PIL import Image
import imageio

from src.image_processing import windowed_image


def save_png(ds, index, hu_min, hu_max, path):
    Image.fromarray(windowed_image(ds, index, hu_min, hu_max)).save(path)


def save_jpeg(ds, index, hu_min, hu_max, path):
    Image.fromarray(windowed_image(ds, index, hu_min, hu_max)) \
        .convert("RGB").save(path, quality=95)


def save_pdf(ds, index, hu_min, hu_max, path):
    Image.fromarray(windowed_image(ds, index, hu_min, hu_max)) \
        .convert("RGB").save(path, "PDF")


def save_video(ds, num_frames, hu_min, hu_max, path, fps=5):
    """Export every frame, in order, as an MP4. For a single-frame file
    this is just a 1-frame clip; a multi-frame file (e.g. emri_small.dcm)
    produces a real scroll-through video.

    windowed_image() returns a grayscale (single-channel) frame, but the
    MP4 encoder expects 3-channel color frames - feeding it grayscale
    directly can produce a file that "saves" without error but isn't a
    valid, playable video. np.stack([frame]*3, axis=-1) duplicates the
    single gray channel into R, G and B, which satisfies the encoder
    while still looking identical (gray, since R=G=B everywhere).

    macro_block_size=1 stops the ffmpeg writer from silently resizing
    frames to the nearest multiple of 16 pixels, which some players
    handle fine and others reject outright for small DICOM images."""
    if not path.lower().endswith(".mp4"):
        path += ".mp4"

    frames = []
    for i in range(num_frames):
        gray = windowed_image(ds, i, hu_min, hu_max)
        rgb = np.stack([gray, gray, gray], axis=-1)
        frames.append(rgb)

    # format="FFMPEG" forces imageio to use the video writer plugin.
    # Without this, imageio sometimes guesses wrong and hands the frames
    # to a completely different plugin (e.g. the DICOM/pydicom one),
    # which doesn't understand video-specific arguments like fps -which would
    #  cause  "Invalid keyword argument(s) for dcmwrite()" error.
    imageio.mimsave(path, frames, format="FFMPEG", fps=fps, macro_block_size=1)


def save_dicom(ds, path):
    """Write the dataset (raw or anonymized) to disk as a .dcm file."""
    ds.save_as(path)