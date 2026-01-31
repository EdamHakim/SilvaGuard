# SilvaGuard 🛰️🌲

**SilvaGuard** is a satellite-based vegetation monitoring system designed to analyze forest health using NDVI (Normalized Difference Vegetation Index). Built with Django, it processes multispectral satellite imagery to detect vegetation density, changes over time, and potential ecological risks.

## 🚀 The Idea

Forest ecosystems are vital for our planet, yet they face constant threats from deforestation, illegal logging, and climate change. **SilvaGuard** aims to provide an automated, scalable solution for monitoring these vast areas from space.

By leveraging **Sentinel-2** or similar satellite data, the system:
- **Preprocesses raw imagery:** Handles cloud masking and atmospheric correction.
- **Calculates NDVI:** precise calculation of vegetation indices to assess plant health.
- **Visualizes Data:** Provides map overlays and analytics for forestry management.

## ✨ Key Features (Prototype)
- **Image Preprocessing:** Automated pipeline to clean and prepare satellite bands.
- **NDVI Calculation:** Core algorithm to determine vegetation health (`(NIR - Red) / (NIR + Red)`).
- **Django Backend:** Robust framework for managing user access and data processing.
- **Scalable Architecture:** Designed to handle large geotiff datasets (currently using mocks for demonstration).

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/EdamHakim/SilvaGuard.git
cd SilvaGuard
```

### 2. Create Virtual Environment
**Windows:**
```bash
python -m venv env
.\env\Scripts\activate
```
**macOS/Linux:**
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` to access the application.