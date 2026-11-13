"""
dose_analysis.py
------------------
Pulls radiation-dose-related tags out of a DICOM dataset.

Note: CTDIvol and DLP are not guaranteed to exist on every CT slice -
in real scanners this information is often stored separately in a
Radiation Dose Structured Report (RDSR). This module just reports
whatever is present on the dataset it's given.
"""

DOSE_TAG_LABELS = {
    "CTDIvol": "CTDIvol (mGy)",
    "DLP": "DLP (mGy.cm)",
    "Exposure": "Exposure (mAs)",
    "KVP": "KVP",
    "XRayTubeCurrent": "X-Ray Tube Current (mA)",
    "ExposureTime": "Exposure Time (ms)",
}


def extract_dose_info(ds):
    """Return a dict of {label: value} for whichever dose tags exist on
    this dataset. Returns an empty dict if none were found - the caller
    decides how to display that ('no dose info found')."""
    dose_data = {}
    for tag, label in DOSE_TAG_LABELS.items():
        if hasattr(ds, tag):
            dose_data[label] = getattr(ds, tag)
    return dose_data


def extract_all_metadata(ds):
    """Loop through every single data element in the file (not just a
    hand-picked list) and return it as rows of (tag, name, VR, value),
    ready to display in a scrollable table.

    Wrapped defensively: a handful of pydicom's own sample files use
    older/retired encodings (e.g. the *_big_endian.dcm variants) that
    current pydicom versions can't fully decode. Rather than silently
    returning only the first couple of tags with no explanation, this
    adds a visible note so it's clear the file itself is the issue, not
    this function."""
    rows = []
    try:
        for elem in ds:
            try:
                if elem.VR == "SQ":  # a "sequence" tag holds nested items, not a plain value
                    value = f"<sequence, {len(elem.value)} item(s)>"
                else:
                    value = str(elem.value)
                rows.append((str(elem.tag), elem.name, elem.VR, value))
            except Exception:
                rows.append(("?", "?", "?", "<unable to read this element>"))
    except Exception as e:
        rows.append(("-", "-", "-", f"<stopped early - file encoding not fully supported: {e}>"))

    if len(rows) <= 1:
        rows.append((
            "-", "-", "-",
            "<Only one tag could be read. This usually means the file uses an "
            "encoding pydicom can't fully decode (e.g. the *_big_endian.dcm "
            "sample files). Try a different sample file instead.>",
        ))
    return rows


def extract_general_info(ds, filename, current_index, num_frames):
    """Return a dict of general (non-dose) facts about the dataset,
    used by the 'Show Info' button."""
    return {
        "File": filename,
        "Patient": getattr(ds, "PatientName", "?"),
        "Modality": getattr(ds, "Modality", "?"),
        "Rows x Cols": f"{ds.Rows} x {ds.Columns}",
        "Frames": num_frames,
        "Current frame": f"{current_index + 1} / {num_frames}",
    }