# 🌍 Astro Pi Post-Processing Scripts

This branch contains the scripts used to process the image and sensor data captured on the International Space Station (ISS) during the Astro Pi Mission Space Lab 2023. The code analyzes the health of Earth vegetation using NDVI (Normalized Difference Vegetation Index) and estimates ecological metrics like oxygen production and CO₂ removal.

---

## 🚀 Requirements

- Python 3.6–3.9 (❗️OpenCV bindings for `cv2` do **not** work with Python 3.11+)
- `opencv-python`
- `numpy`
- `pillow`
- `scipy`
- `matplotlib`

Install with:

```bash
pip install -r requirements.txt
````

---

## 🧪 Pre-launch Testing (Before Receiving Actual Data)

You can simulate the process using sample data.

### ✅ Steps:

1. Use the existing folder structure described in `folder_structure.txt`
   ⚠️ Remove all `.gitkeep` placeholders from empty folders.

2. Download sample NDVI-compatible images:
   [📦 Download from ESA](https://s3.eu-west-2.amazonaws.com/learning-resources-production/projects/astropi-ndvi/2cc9d1033d9c4f05388632e7912a4bb5531b3d94/en/resources/astropi-ndvi-en-resources.zip)
   Place them into the `images/` directory.

---

## 🛰️ Real Post-Processing Steps (After Flight)

1. Place the received `auto-classify` directory from the ISS into the project root.

2. **Convert raw RGB images to NDVI:**

```bash
cd 1-convert-to-ndvi
python3 convert_to_ndvi.py
cd ..
```

This will:

* Normalize contrast
* Compute NDVI using `(B - R) / (B + R)` approximation
* Apply `fastiecm` colormap
* Output to `images_ndvi/`

---

3. **Apply image mask (optional but recommended):**

Use transparent masks for visualization (e.g., panoramas), or blue masks for NDVI pixel counting.

```bash
cd 2-mask
python3 mask.py
cd ..
```

The masked output is saved in `images_masked/`.

---

4. **Run vegetation pixel classification and calculate O₂ & CO₂ estimates:**

```bash
cd 3-pixelcount
python3 pixelcount.py
cd ..
```

Each image is processed pixel-by-pixel using KDTree color matching. Output is written to:

* `data.csv`: includes percentages per class and estimated gas metrics
* `images_plain_colors/`: color-coded output for inspection

---

## 📊 Final Output

All final results are stored in `data.csv` in the following format:

| Image | Healthy% | Declining% | Unhealthy% | No plants% | O₂ (g) | CO₂ (g)  |
| ----- | -------- | ---------- | ---------- | ---------- | ------ | -------- |
| 1.jpg | 25.63    | 35.62      | 1.45       | 37.30      | 49772  | 68343800 |

---

## 🧠 Educational Value

This pipeline transforms simple image data into scientifically relevant ecological indicators, applying mathematics, coding, and environmental science to real-world satellite imagery.

---

## ✅ That's it!

Your results are ready in `data.csv`. Visualizations and analysis can be extended further in tools like Excel, Python, or Jupyter notebooks.