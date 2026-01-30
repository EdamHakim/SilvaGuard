import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "silvaguard.settings")
django.setup()

from satellite_data.models import SatelliteImage, AreaOfInterest

def verify():
    aoi_count = AreaOfInterest.objects.count()
    img_count = SatelliteImage.objects.count()
    
    with open("verification_result.txt", "w") as f:
        f.write(f"AOIs: {aoi_count}\n")
        f.write(f"Images: {img_count}\n")
        
        if img_count > 0:
            last_img = SatelliteImage.objects.first()
            f.write(f"Last Image GEE ID: {last_img.gee_id}\n")
            f.write(f"Date: {last_img.acquisition_date}\n")

if __name__ == "__main__":
    verify()
