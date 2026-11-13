"""
anonymizer.py
--------------
Blanks out identifying fields on a DICOM dataset. Works on the dataset
in memory only - the GUI/exporters decide when to actually save it.
"""

TAGS_TO_CLEAR = [
    "PatientName", "PatientID", "PatientBirthDate", "PatientSex",
    "PatientAddress", "InstitutionName", "ReferringPhysicianName",
    "PerformingPhysicianName", "OperatorsName", "StudyDate", "AccessionNumber",
]


def anonymize_dicom(ds):
    """Clear identifying tags (if present) and strip private/vendor
    tags, which can also carry identifying info. Mutates ds in place
    and returns it for convenience."""
    for tag in TAGS_TO_CLEAR:
        if tag in ds:
            ds.data_element(tag).value = ""
    ds.remove_private_tags()
    return ds
