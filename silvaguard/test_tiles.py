import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silvaguard.settings')

import django
django.setup()

from satellite_data.models import SatelliteImage
from satellite_data.analysis import VegetationAnalyzer

print("Testing Tile URL Generation")
print("="*50)

analyzer = VegetationAnalyzer()
img = SatelliteImage.objects.exclude(gee_id__isnull=True).exclude(gee_id='').first()

if img and img.gee_id:
    print(f"Testing with image: {img.gee_id}")
    try:
        tile_url = analyzer.get_gee_tile_url(img.gee_id)
        print(f"\nGenerated Tile URL:")
        if tile_url:
            print(f"✅ SUCCESS: {tile_url[:100]}...")
        else:
            print("❌ EMPTY - No URL returned")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ No satellite images found with gee_id")
    print(f"Total images: {SatelliteImage.objects.count()}")
    print(f"Images with gee_id: {SatelliteImage.objects.exclude(gee_id__isnull=True).exclude(gee_id='').count()}")
