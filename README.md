# Astro Pi NDVI Capture & Classification (Main Branch)

This branch contains the flight code deployed on the International Space Station (ISS) during the 2023 ESA Astro Pi Mission Space Lab. Its primary function was to autonomously capture Earth imagery using a Pi Camera, classify lighting conditions (day/twilight/night), and store relevant metadata for further analysis on Earth.

## 🛰️ Purpose

To acquire high-quality images of Earth's surface suitable for vegetation analysis using the NDVI (Normalized Difference Vegetation Index), along with associated environmental and positional metadata.

## 🗂️ Main Features

- 📸 Automated image capture with GPS tagging
- 🔍 Real-time classification of lighting conditions using a Coral Edge TPU
- 🌡️ Logging of environmental data (temperature, humidity, pressure)
- 🧭 Logging of ISS attitude and sensor orientation data
- ⛔ Automatic filtering of night images to conserve storage
- 📦 CSV-based storage for both image metadata and sensor readings

## 🧠 Technologies Used

- Python 3
- PiCamera
- Sense HAT
- PyCoral (Edge TPU)
- CSV logging and image handling with PIL & OpenCV
- Skyfield for ISS location
- logzero for structured logging

## 📁 Folder Structure

```
.
├── model\_v2/             # Edge TPU model + labels
├── raw/                   # Unclassified raw images
├── auto-classify/         # Sorted images: day / twilight
├── data.csv               # Main metadata file
├── position.csv           # Orientation/position sensor data
├── events.log             # Debug logging

```

## 📌 Notes

- Runs for approximately 170 minutes (mission duration limit)
- Includes temperature-based logic for CPU thermal monitoring
- Automatically terminates if image data size exceeds 2.7GB

## 🔒 Disclaimer

This code was written for use within the constraints of the Astro Pi Mission and optimized for power, safety, and performance aboard the ISS.