import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silvaguard.settings')

import django
django.setup()

from satellite_data.models import AreaOfInterest, VegetationAnalysis, DeforestationAlert
import json

print("=== FINAL MAP DATA VERIFICATION ===\n")

# 1. Check AOIs
aois = AreaOfInterest.objects.all()
print(f"Areas of Interest: {aois.count()}")
for aoi in aois:
    print(f"  - {aoi.name} at ({aoi.latitude}, {aoi.longitude})")

# 2. Check Analyses
print(f"\nVegetation Analyses: {VegetationAnalysis.objects.count()}")
real_analyses = VegetationAnalysis.objects.exclude(heatmap_file_path='demo').exclude(heatmap_file_path='GEE_LAYER')
print(f"  - With valid Tile URLs: {real_analyses.count()}")

for analysis in real_analyses:
    print(f"\n  Analysis #{analysis.id}:")
    print(f"    Forest Cover: {analysis.forest_cover_percentage:.2f}%")
    print(f"    Tile URL: {analysis.heatmap_file_path[:80]}...")

# 3. Check Alerts
alerts = DeforestationAlert.objects.all()
print(f"\nDeforestation Alerts: {alerts.count()}")
for alert in alerts:
    print(f"  - {alert.aoi.name}: {alert.forest_loss_hectares:.1f} ha lost")

# 4. Simulate API Response
print("\n=== SIMULATED MAP API RESPONSE ===")
features = []

for aoi in aois:
    latest_analysis = VegetationAnalysis.objects.filter(
        processed_image__satellite_image__aoi=aoi
    ).exclude(heatmap_file_path='demo').exclude(heatmap_file_path='GEE_LAYER').order_by('-analysis_date').first()
    
    tile_url = latest_analysis.heatmap_file_path if latest_analysis else ""
    
    features.append({
        "type": "AOI",
        "name": aoi.name,
        "coordinates": [aoi.longitude, aoi.latitude],
        "tile_url": tile_url[:50] + "..." if len(tile_url) > 50 else tile_url,
        "forest_cover": f"{latest_analysis.forest_cover_percentage:.2f}%" if latest_analysis else "N/A"
    })

for alert in alerts:
    features.append({
        "type": "Alert",
        "location": alert.aoi.name,
        "coordinates": [alert.aoi.longitude, alert.aoi.latitude],
        "loss": f"{alert.forest_loss_hectares:.1f} ha"
    })

print(json.dumps(features, indent=2))

print("\n=== STATUS ===")
if real_analyses.count() > 0:
    print("✅ Map should display GEE forest overlays")
else:
    print("❌ No valid tile URLs found - map will show markers only")

if alerts.count() > 0:
    print("✅ Deforestation alerts will be shown")
else:
    print("⚠️  No alerts detected yet")
