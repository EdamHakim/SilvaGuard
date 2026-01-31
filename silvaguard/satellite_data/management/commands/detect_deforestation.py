from django.core.management.base import BaseCommand
from satellite_data.models import AreaOfInterest, VegetationAnalysis, DeforestationAlert
from satellite_data.detection import DeforestationDetector
from satellite_data.analysis import VegetationAnalyzer
import numpy as np

class Command(BaseCommand):
    help = 'Detects deforestation by comparing vegetation analysis results over time'

    def handle(self, *args, **options):
        detector = DeforestationDetector()
        analyzer = VegetationAnalyzer()

        aois = AreaOfInterest.objects.all()
        
        if not aois.exists():
            self.stdout.write(self.style.WARNING("No AOIs found."))
            return

        for aoi in aois:
            self.stdout.write(f"Checking AOI: {aoi.name}...")
            
            # Get all analysis results sorted by date
            analyses = VegetationAnalysis.objects.filter(
                processed_image__satellite_image__aoi=aoi
            ).order_by('processed_image__satellite_image__acquisition_date')
            
            count = analyses.count()
            if count < 2:
                self.stdout.write(f"  - Not enough data points ({count}). Need at least 2.")
                continue
                
            # Real GEE Logic: Compare latest with previous
            latest = analyses.last()
            previous = analyses[count - 2]
            
            img_before = previous.processed_image.satellite_image.gee_id
            img_after = latest.processed_image.satellite_image.gee_id

            if not img_before or not img_after:
                continue

            self.stdout.write(f"  - Comparing {previous.analysis_date.date()} vs {latest.analysis_date.date()}")
            
            # Detect Loss and calculate area via GEE
            result = analyzer.calculate_forest_loss(img_before, img_after)
            loss_ha = result['loss_ha']
            loss_pct = result['loss_percentage']
            
            # Get Loss Tile URL
            loss_tile_url = analyzer.get_loss_tile_url(img_before, img_after)
            
            self.stdout.write(f"  - Detected Loss: {loss_ha:.2f} ha ({loss_pct:.2f}%)")
            
            # Create Alert if loss is significant (e.g. > 0.1 hectare)
            if loss_ha > 0.1:
                DeforestationAlert.objects.create(
                    aoi=aoi,
                    analysis_before=previous,
                    analysis_after=latest,
                    forest_loss_hectares=loss_ha,
                    loss_percentage=loss_pct,
                    loss_map_path=loss_tile_url
                )
                self.stdout.write(self.style.SUCCESS("  - Alert Created! Tile URL saved."))
