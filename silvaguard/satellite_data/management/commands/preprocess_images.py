from django.core.management.base import BaseCommand
from satellite_data.models import SatelliteImage, ProcessedImage
from satellite_data.preprocessing import ImagePreprocessor
import os

class Command(BaseCommand):
    help = 'Runs preprocessing on raw satellite images'

    def handle(self, *args, **options):
        raw_images = SatelliteImage.objects.filter(processed_version__isnull=True)
        processor = ImagePreprocessor()

        if not raw_images.exists():
            self.stdout.write(self.style.WARNING('No new images to preprocess.'))
            return

        self.stdout.write(f"Preprocessing {raw_images.count()} images...")

        for img in raw_images:
            try:
                self.stdout.write(f"Processing ID: {img.image_id}")
                
                # Mock Path
                dummy_path = f"raw_data/{img.image_id}.tif"
                
                # Run Logic
                result = processor.process_image(dummy_path)
                
                # Save Result
                ProcessedImage.objects.create(
                    satellite_image=img,
                    processed_file_path=f"processed_data/{img.image_id}_clean.tif",
                    ndvi_mean=0.0, # Will be calculated in analysis phase, or here if we merge logic
                    processed_metadata=result['metadata']
                )
                
                self.stdout.write(self.style.SUCCESS(f"  - Done."))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  - Error: {str(e)}"))
