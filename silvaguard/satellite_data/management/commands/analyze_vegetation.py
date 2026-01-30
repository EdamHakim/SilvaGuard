from django.core.management.base import BaseCommand
from satellite_data.models import ProcessedImage, VegetationAnalysis
from satellite_data.analysis import VegetationAnalyzer
import numpy as np
import os

class Command(BaseCommand):
    help = 'Performs vegetation analysis on preprocessed images'

    def handle(self, *args, **options):
        processed_images = ProcessedImage.objects.filter(vegetation_analysis__isnull=True)
        analyzer = VegetationAnalyzer()

        if not processed_images.exists():
            self.stdout.write(self.style.WARNING('No new processed images to analyze.'))
            return

        self.stdout.write(f"Analyzing {processed_images.count()} images...")

        for img in processed_images:
            try:
                self.stdout.write(f"Processing ID: {img.satellite_image.image_id}")
                
                # Mock loading data (In real world: rasterio.open(img.processed_file_path))
                # Generating mock arrays similar to preprocessing step
                # Assuming 100x100 image for consistency
                red_band = np.random.rand(100, 100)
                nir_band = np.random.rand(100, 100)

                # Calculate NDVI
                ndvi_grid = analyzer.calculate_ndvi(red_band, nir_band)
                
                # Analyze Forest Cover
                stats = analyzer.analyze_forest_cover(ndvi_grid)
                
                # Generate Mock Heatmap File
                heatmap_filename = f"heatmap_{img.satellite_image.image_id}.txt" # Mocking image as text
                # Ideally save to MEDIA_ROOT
                heatmap_path = f"media/heatmaps/{heatmap_filename}"
                os.makedirs('media/heatmaps', exist_ok=True)
                
                analyzer.generate_heatmap(ndvi_grid, heatmap_path)

                # Save Results
                VegetationAnalysis.objects.create(
                    processed_image=img,
                    mean_ndvi=stats['mean_ndvi'],
                    forest_cover_percentage=stats['forest_percentage'],
                    heatmap_file_path=heatmap_path
                )
                
                self.stdout.write(self.style.SUCCESS(f"  - Analysis complete. Forest Cover: {stats['forest_percentage']:.2f}%"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  - Error analyzing {img.satellite_image.image_id}: {str(e)}"))
