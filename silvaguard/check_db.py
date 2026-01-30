import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silvaguard.settings')

import django
django.setup()

from satellite_data.models import VegetationAnalysis, SatelliteImage

print("=== Database Status ===")
print(f"Satellite Images: {SatelliteImage.objects.count()}")
print(f"  - With GEE ID: {SatelliteImage.objects.exclude(gee_id__isnull=True).count()}")
print(f"Vegetation Analyses: {VegetationAnalysis.objects.count()}")

print("\n=== Analysis Records ===")
for analysis in VegetationAnalysis.objects.all():
    print(f"\nID: {analysis.id}")
    print(f"  Forest Cover: {analysis.forest_cover_percentage:.2f}%")
    url = analysis.heatmap_file_path
    if url and url.startswith('https://'):
        print(f"  Tile URL: {url[:80]}...")
    else:
        print(f"  Tile URL: {url}")
