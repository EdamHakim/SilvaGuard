from django.core.management.base import BaseCommand
from satellite_data.models import ProcessedImage, VegetationAnalysis
from satellite_data.analysis import VegetationAnalyzer

class Command(BaseCommand):
    help = 'Performs vegetation analysis on GEE images'

    def handle(self, *args, **options):
        analyzer = VegetationAnalyzer()
        
        # Get processed images that don't have analysis yet
        items = ProcessedImage.objects.filter(vegetation_analysis__isnull=True)
        self.stdout.write(f"Analyzing {items.count()} images via Google Earth Engine...")
        
        for item in items:
            img = item.satellite_image
            if not img.gee_id:
               continue

            self.stdout.write(f"Analyzing GEE Asset: {img.gee_id}")
            
            try:
                # Perform GEE Analysis
                result = analyzer.analyze_gee_image(img.gee_id)
                
                VegetationAnalysis.objects.create(
                    processed_image=item,
                    mean_ndvi=result['mean_ndvi'] if result['mean_ndvi'] else 0.0,
                    forest_cover_percentage=result['forest_percentage'],
                    heatmap_file_path="GEE_LAYER" # No local file
                )
                self.stdout.write(f"  - Analysis complete. Forest Cover: {result['forest_percentage']:.2f}%")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  - Error: {e}"))

        self.stdout.write(self.style.SUCCESS("GGE Analysis complete."))
