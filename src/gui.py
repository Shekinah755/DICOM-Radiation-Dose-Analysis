"""
gui.py
-------
The interface only: buttons, sliders, labels, windows, pop-ups.
It does NOT contain any DICOM processing logic itself - every button
just calls a function from one of the other modules and displays the
result.
"""

import tkinter as tk
from PIL import Image, ImageTk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox

from src.dicom_loader import get_sample_files, load_dicom, get_num_frames
from src.image_processing import windowed_image
from src.dose_analysis import extract_dose_info, extract_general_info, extract_all_metadata
from src.anonymizer import anonymize_dicom
from src.exporters import save_png, save_jpeg, save_pdf, save_video, save_dicom


def run_app():
    # ---------------- State that belongs to this running app ----------------
    sample_files = get_sample_files()   # {display name: full path}
    state = {
        "selected_ds": None,
        "num_frames": 1,
        "current_index": 0,
        "hu_min": -200,
        "hu_max": 400,
    }

    # ---------------- Event handlers ----------------

    def load_selected_file(event=None):
        name = file_combo.get()
        if not name:
            return
        ds = load_dicom(sample_files[name])
        state["selected_ds"] = ds
        state["num_frames"] = get_num_frames(ds)
        state["current_index"] = 0
        slice_slider.configure(to=max(state["num_frames"] - 1, 0))
        slice_slider.set(0)
        update_image()

    def update_image():
        ds = state["selected_ds"]
        if ds is None:
            return
        arr = windowed_image(ds, state["current_index"], state["hu_min"], state["hu_max"])
        pil_img = Image.fromarray(arr).resize((500, 500))
        tk_img = ImageTk.PhotoImage(pil_img)
        image_label.configure(image=tk_img)
        image_label.image = tk_img  # keep a reference so it isn't garbage collected

    def on_slice_change(value):
        state["current_index"] = int(float(value))
        update_image()

    def apply_contrast(event=None):
        """Reads the Min/Max sliders and redraws. Called by the Apply
        button, AND automatically when you release either slider, so
        you don't have to click Apply every time."""
        try:
            new_min = int(min_slider.get())
            new_max = int(max_slider.get())
            if new_min >= new_max:
                messagebox.showerror("Error", "Min must be less than Max.")
                return
            state["hu_min"], state["hu_max"] = new_min, new_max
            update_image()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def make_clickable(scale, on_change):
        """Fix ttk.Scale's default behavior (click only nudges one step).
        This makes clicking anywhere on the slider track jump straight
        to that position, like most slider UIs people expect."""
        def jump_to_click(event):
            widget = event.widget
            track_width = widget.winfo_width()
            if track_width <= 1:
                return
            frm = float(widget.cget("from"))
            to = float(widget.cget("to"))
            ratio = min(max(event.x / track_width, 0), 1)  # clamp 0-1
            new_value = frm + ratio * (to - frm)
            widget.set(new_value)
            on_change(new_value)
        scale.bind("<Button-1>", jump_to_click)

    def show_info():
        ds = state["selected_ds"]
        if ds is None:
            messagebox.showinfo("Info", "No DICOM selected yet.")
            return
        open_metadata_window(ds, file_combo.get())

    def open_metadata_window(ds, filename):
        """Shows EVERY tag in the file (not a preselected few) in a
        scrollable table, since a full DICOM header can have 50+ fields
        and won't fit in a simple message box."""
        win = tk.Toplevel(app)
        win.title(f"Full metadata - {filename}")
        win.geometry("800x600")

        summary = extract_general_info(ds, filename, state["current_index"], state["num_frames"])
        summary_text = "   |   ".join(f"{k}: {v}" for k, v in summary.items())
        ttk.Label(win, text=summary_text, wraplength=780).pack(pady=5)

        columns = ("tag", "name", "vr", "value")
        tree = ttk.Treeview(win, columns=columns, show="headings")
        for col, width in zip(columns, (110, 220, 50, 380)):
            tree.heading(col, text=col.upper())
            tree.column(col, width=width, anchor="w")

        vsb = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        for tag, name, vr, value in extract_all_metadata(ds):
            tree.insert("", "end", values=(tag, name, vr, value))

    def show_dose_info():
        ds = state["selected_ds"]
        if ds is None:
            messagebox.showinfo("Dose Info", "No DICOM selected yet.")
            return
        dose = extract_dose_info(ds)
        if not dose:
            text = "No dose-related tags found in this file."
        else:
            text = "\n".join(f"{k}: {v}" for k, v in dose.items())
        messagebox.showinfo("Radiation Dose Info", text)

    def anonymize():
        ds = state["selected_ds"]
        if ds is None:
            messagebox.showinfo("Anonymize", "No DICOM selected yet.")
            return
        anonymize_dicom(ds)
        messagebox.showinfo(
            "Anonymize",
            "Loaded file anonymized in memory.\nUse 'Save Anonymized DICOM' to write it to disk.",
        )

    def handle_save_dicom():
        ds = state["selected_ds"]
        if ds is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".dcm", filetypes=[("DICOM", "*.dcm")])
        if not path:
            return
        save_dicom(ds, path)
        messagebox.showinfo("Saved", f"Saved to {path}")

    def handle_save_png():
        ds = state["selected_ds"]
        if ds is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if not path:
            return
        save_png(ds, state["current_index"], state["hu_min"], state["hu_max"], path)
        messagebox.showinfo("Saved", f"Saved to {path}")

    def handle_save_jpeg():
        ds = state["selected_ds"]
        if ds is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg")])
        if not path:
            return
        save_jpeg(ds, state["current_index"], state["hu_min"], state["hu_max"], path)
        messagebox.showinfo("Saved", f"Saved to {path}")

    def handle_save_pdf():
        ds = state["selected_ds"]
        if ds is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not path:
            return
        save_pdf(ds, state["current_index"], state["hu_min"], state["hu_max"], path)
        messagebox.showinfo("Saved", f"Saved to {path}")

    def handle_save_video():
        ds = state["selected_ds"]
        if ds is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4", "*.mp4")])
        if not path:
            return
        try:
            save_video(ds, state["num_frames"], state["hu_min"], state["hu_max"], path)
            messagebox.showinfo("Saved", f"Saved video to {path}")
        except Exception as e:

            messagebox.showerror(
                "Video export failed",
                f"{e}\n\nIf this mentions ffmpeg, run:\npip install imageio-ffmpeg",
            )

    # ---------------- Build the window ----------------

    app = ttk.Window(themename="superhero")
    app.title("DICOM Radiation Dose Analyzer (pydicom sample data)")
    app.geometry("950x880")  # fallback size if maximizing isn't supported below
    try:
        app.state("zoomed")  # start maximized (Windows); harmless no-op elsewhere
    except Exception:
        pass

    # --- Scrollable container ---
    # Everything below goes inside `content` (not directly in `app`), so
    # if the total content is taller than the window, you can scroll to
    # reach the rest instead of it being cut off.
    #
    # A plain tk.Canvas doesn't know about ttkbootstrap's dark theme, so
    # we read the theme's own background color and apply it manually -
    # otherwise the canvas shows as plain white wherever content doesn't
    # cover it.
    theme_bg = app.style.colors.bg
    canvas = tk.Canvas(app, highlightthickness=0, bg=theme_bg)
    scrollbar = ttk.Scrollbar(app, orient="vertical", command=canvas.yview)
    content = ttk.Frame(canvas)

    content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Placing the content frame inside the canvas, and remembering the
    # id this returns so we can resize it below.
    content_window = canvas.create_window((0, 0), window=content, anchor="n")

    def stretch_content_to_canvas_width(event):
        """Whenever the window is resized, make the content frame exactly
        as wide as the canvas - this is what removes the empty strip of
        unthemed space you were seeing on the right."""
        canvas.itemconfig(content_window, width=event.width)

    canvas.bind("<Configure>", stretch_content_to_canvas_width)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    # --- Widgets (all placed inside `content`, not `app`) ---

    ttk.Label(content, text="DICOM Radiation Dose Analyzer", font="Poppins 22 bold").pack(pady=10)

    ttk.Label(content, text="Choose a pydicom sample file:").pack()
    file_combo = ttk.Combobox(content, values=sorted(sample_files.keys()), width=50, state="readonly")
    file_combo.pack(pady=5)
    file_combo.bind("<<ComboboxSelected>>", load_selected_file)

    btn_frame = ttk.Frame(content)
    btn_frame.pack(pady=5)
    ttk.Button(btn_frame, text="Show Info", command=show_info, bootstyle="info").grid(row=0, column=0, padx=5)
    ttk.Button(btn_frame, text="Dose Info", command=show_dose_info, bootstyle="info").grid(row=0, column=1, padx=5)
    ttk.Button(btn_frame, text="Anonymize", command=anonymize, bootstyle="warning").grid(row=0, column=2, padx=5)

    image_label = ttk.Label(content)
    image_label.pack(pady=10)

    ttk.Label(content, text="Frame / Slice").pack()
    slice_slider = ttk.Scale(content, from_=0, to=0, orient=HORIZONTAL, command=on_slice_change, length=400)
    slice_slider.pack(pady=5)
    make_clickable(slice_slider, lambda v: on_slice_change(v))

    ttk.Label(content, text="HU Min").pack()
    min_slider = ttk.Scale(content, from_=-1000, to=1000, orient=HORIZONTAL, length=400)
    min_slider.set(state["hu_min"])
    min_slider.pack(pady=5)
    min_slider.bind("<ButtonRelease-1>", apply_contrast)   # auto-apply on release
    make_clickable(min_slider, lambda v: None)

    ttk.Label(content, text="HU Max").pack()
    max_slider = ttk.Scale(content, from_=-1000, to=3000, orient=HORIZONTAL, length=400)
    max_slider.set(state["hu_max"])
    max_slider.pack(pady=5)
    max_slider.bind("<ButtonRelease-1>", apply_contrast)   # auto-apply on release
    make_clickable(max_slider, lambda v: None)

    ttk.Button(content, text="Apply", command=apply_contrast, bootstyle="success").pack(pady=10)

    save_frame = ttk.Frame(content)
    save_frame.pack(pady=10)
    ttk.Button(save_frame, text="Save PNG", command=handle_save_png).grid(row=0, column=0, padx=5)
    ttk.Button(save_frame, text="Save JPEG", command=handle_save_jpeg).grid(row=0, column=1, padx=5)
    ttk.Button(save_frame, text="Save PDF", command=handle_save_pdf).grid(row=0, column=2, padx=5)
    ttk.Button(save_frame, text="Save Video (MP4)", command=handle_save_video).grid(row=0, column=3, padx=5)
    ttk.Button(save_frame, text="Save Anonymized DICOM", command=handle_save_dicom).grid(row=0, column=4, padx=5)

    app.mainloop()