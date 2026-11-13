# DICOM Radiation Dose Analyzer

A desktop app (Tkinter + ttkbootstrap) built on pydicom's own built-in
sample DICOM files, so no external dataset is needed to try it.

## Run it

```bash
pip install -r requirements.txt
python main.py
```

## Project layout

```
main.py                 entry point - just starts the GUI
src/
  dicom_loader.py        find + read DICOM files
  image_processing.py    HU windowing / contrast (raw pixels -> viewable image)
  dose_analysis.py       pull dose-related tags out of a dataset
  anonymizer.py          blank identifying tags
  exporters.py           save as PNG / JPEG / PDF / MP4 / DICOM
  gui.py                 buttons, sliders, windows - wires everything together
```

Each module has one job, so if you want to change how windowing works
you only ever touch `image_processing.py`, not the GUI code - and vice
versa if you want to change a button's label.

## Notes

- Pick `emri_small.dcm` from the dropdown to see multi-frame
  scrolling and video export in action; most other sample files are
  single-frame.
- `dose_analysis.py` only reports tags that exist on the loaded file.
  Real CTDIvol/DLP values often live in a separate Radiation Dose
  Structured Report (RDSR), not on every image slice - pydicom's
  small sample files generally don't carry this data, so "no dose
  info found" is expected there.
