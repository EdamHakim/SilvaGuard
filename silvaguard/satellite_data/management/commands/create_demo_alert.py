from django.core.management.base import BaseCommand
from satellite_data.models import AreaOfInterest, DeforestationAlert, VegetationAnalysis, ProcessedImage, SatelliteImage
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Creates a demo deforestation alert for visualization'

    def handle(self, *args, **options):
        aoi = AreaOfInterest.objects.first()
        if not aoi:
            self.stdout.write(self.style.ERROR("No AOI found. Create one first."))
            return

        self.stdout.write(f"Creating demo alert for AOI: {aoi.name}")
        
        # Determine satellite image (create fake one if needed or use existing)
        # We need 2 analysis records
        
        # 1. Create Analysis "Before"
        img1, _ = SatelliteImage.objects.get_or_create(
             image_id="DEMO_IMG_BEFORE",
             defaults={'aoi': aoi, 'acquisition_date': timezone.now() - timezone.timedelta(days=30), 'cloud_coverage': 0.0}
        )
        proc1, _ = ProcessedImage.objects.get_or_create(satellite_image=img1, defaults={'processed_file_path': 'demo'})
        ana1, _ = VegetationAnalysis.objects.get_or_create(
            processed_image=proc1,
            defaults={'mean_ndvi': 0.8, 'forest_cover_percentage': 80.0, 'heatmap_file_path': 'demo'}
        )
        
        # 2. Create Analysis "After" (Loss)
        img2, _ = SatelliteImage.objects.get_or_create(
             image_id="DEMO_IMG_AFTER",
             defaults={'aoi': aoi, 'acquisition_date': timezone.now(), 'cloud_coverage': 0.0}
        )
        proc2, _ = ProcessedImage.objects.get_or_create(satellite_image=img2, defaults={'processed_file_path': 'demo'})
        ana2, _ = VegetationAnalysis.objects.get_or_create(
            processed_image=proc2,
            defaults={'mean_ndvi': 0.4, 'forest_cover_percentage': 50.0, 'heatmap_file_path': 'demo'}
        )

        # 3. Create Alert
        Alert = DeforestationAlert.objects.create(
            aoi=aoi,
            analysis_before=ana1,
            analysis_after=ana2,
            forest_loss_hectares=150.5,
            loss_percentage=37.5
        )
        
        self.stdout.write(self.style.SUCCESS(f"Created Alert: {Alert}"))
