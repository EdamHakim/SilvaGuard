import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silvaguard.settings')
django.setup()

from satellite_data.models import VegetationAnalysis, AreaOfInterest

print("=== Vegetation Analysis Tile URLs ===")
analyses = VegetationAnalysis.objects.all()
print(f"Total analyses: {analyses.count()}\n")

for analysis in analyses:
    print(f"Analysis ID: {analysis.id}")
    print(f"  Forest Cover: {analysis.forest_cover_percentage:.2f}%")
    print(f"  Heatmap Path: {analysis.heatmap_file_path}")
    print(f"  AOI: {analysis.processed_image.satellite_image.aoi.name}")
    print()

print("\n=== Testing API Response ===")
from satellite_data.views import api_get_map_data
from django.test import RequestFactory
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

factory = RequestFactory()
request = factory.get('/satellite/api/map-data/')
request.user = user

response = api_get_map_data(request)
import json
data = json.loads(response.content)

print(f"Features count: {len(data['features'])}")
for feature in data['features']:
    if feature['properties']['type'] == 'AOI':
        print(f"\nAOI Feature:")
        print(f"  Name: {feature['properties']['name']}")
        print(f"  Tile URL: {feature['properties'].get('tile_url', 'MISSING')[:80]}")
