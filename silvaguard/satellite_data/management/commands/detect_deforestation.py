from django.core.management.base import BaseCommand
from satellite_data.models import AreaOfInterest, VegetationAnalysis, DeforestationAlert
from satellite_data.detection import DeforestationDetector
from satellite_data.analysis import VegetationAnalyzer
import numpy as np

class Command(BaseCommand):
    help = 'Detects deforestation by comparing vegetation analysis results over time'

    def handle(self, *args, **options):
        detector = DeforestationDetector()
        analyzer = VegetationAnalyzer() # Helper to load data if needed, or we mock here

        aois = AreaOfInterest.objects.all()
        
        if not aois.exists():
            self.stdout.write(self.style.WARNING("No AOIs found."))
            return

        for aoi in aois:
            self.stdout.write(f"Checking AOI: {aoi.name}...")
            
            # Get all analysis results sorted by date
            analyses = VegetationAnalysis.objects.filter(
                processed_image__satellite_image__aoi=aoi
            ).order_by('analysis_date')
            
            count = analyses.count()
            if count < 2:
                self.stdout.write(f"  - Not enough data points ({count}). Need at least 2.")
                continue
                
            # Simple Logic: Compare latest with earliest (or previous)
            # For this prototype, let's compare the last two
            latest = analyses.last()
            previous = analyses[count - 2]
            
            self.stdout.write(f"  - Comparing {previous.analysis_date.date()} vs {latest.analysis_date.date()}")
            
            # Mock Loading Arrays (Simulating loading the saved heatmaps/arrays)
            # In real app: ndvi_before = rasterio.open(previous.heatmap_file_path).read(1)
            ndvi_before = np.random.rand(100, 100)
            ndvi_after = np.random.rand(100, 100) # Random will definitely show change
            
            # Detect
            result = detector.detect_loss(ndvi_before, ndvi_after)
            
            # Estimate Area
            loss_ha = detector.estimate_area_hectares(result['loss_pixels'])
            
            self.stdout.write(f"  - Detected Loss: {loss_ha:.2f} ha ({result['loss_percentage']:.2f}%)")
            
            # Create Alert if loss > threshold (e.g. 0.0 value, any loss)
            if loss_ha > 0:
                DeforestationAlert.objects.create(
                    aoi=aoi,
                    analysis_before=previous,
                    analysis_after=latest,
                    forest_loss_hectares=loss_ha,
                    loss_percentage=result['loss_percentage'],
                    loss_map_path="media/alerts/mock_loss_map.png"
                )
                self.stdout.write(self.style.SUCCESS("  - Alert Created!"))
