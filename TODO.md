# SilvaGuard: Project TO-DO List 📝

## 🛠️ Infrastructure & Setup
- [x] Initial Django project structure.
- [x] Custom User model (`users.CustomUser`).
- [ ] Set up PostgreSQL for production-ready data storage.
- [ ] Configure Environment Variables for GEE and Secret Key.

## 🛰️ Satellite Data & Analysis
- [x] Core models for AOIs, Images, and Alerts.
- [/] Earth Engine (GEE) integration (`gee_utils.py`).
- [ ] Implement automated scheduling for fetching new satellite images.
- [ ] Enhance cloud masking using advanced algorithms.
- [ ] Refine deforestation detection logic in `detection.py`.

## 🖥️ UI & Dashboard
- [/] Dashboard structure in `home.html`.
- [ ] Integrate interactive map (Leaflet or Mapbox) with GEE tiles.
- [ ] Build AOI management interface (Add/Edit AOIs).
- [ ] Create detailed report view for individual alerts.
- [ ] Finalize Authentication templates (Login/Signup).

## 🚀 Future Goals
- [ ] Mobile-responsive dashboard.
- [ ] Email/SMS notification system for rapid alerts.
- [ ] Multi-spectral support for more indices (EVI, SAVI).
- [ ] Community feedback portal for ground truth validation.
