# DICOM Radiation Dose Analyzer

## Project Overview

The DICOM Radiation Dose Analyzer is a desktop application built with Python, Tkinter, and ttkbootstrap for exploring DICOM images and reviewing dose-related metadata. It uses pydicom's built-in sample files, so no separate imaging dataset is needed to try the application.

The project brings together DICOM file loading, image windowing, dose-tag inspection, anonymization, and export tools in a desktop interface. Dose values are shown only when the loaded DICOM file contains the relevant tags.

## Features

- Browse and load DICOM files, including pydicom's built-in sample files
- View image data with windowing and contrast adjustments
- Scroll through multi-frame studies such as `emri_small.dcm`
- Inspect dose-related metadata available in the loaded dataset
- Blank identifying tags with the anonymization tools
- Export images and studies to PNG, JPEG, PDF, MP4, or DICOM formats
- Use a modular code structure that separates the GUI from loading, processing, analysis, anonymization, and export logic

## Technologies Used

- Python 3
- Tkinter and ttkbootstrap (desktop GUI)
- pydicom (DICOM reading and sample data)
- Image-processing and export libraries listed in `requirements.txt`

## Project Structure

```text
main.py                  Application entry point
src/
  dicom_loader.py        Find and read DICOM files
  image_processing.py    Window and adjust image contrast
  dose_analysis.py       Extract dose-related tags from a dataset
  anonymizer.py          Blank identifying tags
  exporters.py           Export PNG, JPEG, PDF, MP4, and DICOM files
  gui.py                 GUI controls and application wiring
requirements.txt         Python dependencies
```

## Getting Started

1. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Start the application:

   ```bash
   python main.py
   ```

## Usage

1. Launch the app with `main.py`.
2. Select a DICOM file from the available file list or sample-file dropdown.
3. Adjust the image windowing and contrast controls to explore the image.
4. For multi-frame files, scroll through frames and use video export where available.
5. Review any dose-related metadata present in the selected dataset.
6. Use the anonymization or export options as needed.

## Dose Metadata Notes

The analyzer reports dose-related tags that are present in the loaded DICOM dataset. CTDIvol and DLP values are often recorded in a separate Radiation Dose Structured Report (RDSR), rather than on each image slice. Many of pydicom's small built-in sample files do not include these values, so seeing “no dose info found” with a sample file is expected.

Select `emri_small.dcm` to try multi-frame scrolling and video export. Most other sample files contain a single frame.

## Future Improvements

- Add support for importing and linking separate RDSR files to image studies
- Expand dose reporting for additional DICOM dose attributes and structured reports
- Add batch analysis and export for multiple studies
- Improve study and series browsing for larger datasets
- Add configurable export presets and reporting options
