# SilvaGuard 🛰️🌲

**SilvaGuard** is a satellite-based vegetation monitoring system designed to analyze forest health using NDVI (Normalized Difference Vegetation Index). Built with Django, it processes multispectral satellite imagery to detect vegetation density, changes over time, and potential ecological risks.

## 🚀 The Idea

Forest ecosystems are vital for our planet, yet they face constant threats from deforestation, illegal logging, and climate change. **SilvaGuard** aims to provide an automated, scalable solution for monitoring these vast areas from space.

By leveraging **Sentinel-2** or similar satellite data, the system:
- **Preprocesses raw imagery:** Handles cloud masking and atmospheric correction.
- **Calculates NDVI:** precise calculation of vegetation indices to assess plant health.
- **Visualizes Data:** Provides map overlays and analytics for forestry management.

- **Scalable Architecture:** Designed to handle large geotiff datasets (currently using mocks for demonstration).

---

## 📽️ Project Information
- **Vision:** [Project_Idea.md](Project_Idea.md)
- **Technical Progress:** [TODO.md](TODO.md)

---

## 🗺️ Roadmap

### Phase 1: Foundation (Current)
- [x] Django project & Custom User app.
- [x] Satellite data models & GEE utilities.
- [/] Initial dashboard UI layout (`home.html`).

### Phase 2: Core Intelligence (Next)
- [ ] Interactive Leaflet/GEE Map integration.
- [ ] Automated image fetchers (Celery/Crontab).
- [ ] Deforestation detection algorithm refinement.

### Phase 3: Engagement & Scale
- [ ] User notification system (Alerts).
- [ ] Mobile-responsive optimizations.
- [ ] Exportable reports for organizations.

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