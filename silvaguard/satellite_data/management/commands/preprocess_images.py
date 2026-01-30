from django.core.management.base import BaseCommand
from satellite_data.models import SatelliteImage, ProcessedImage

class Command(BaseCommand):
    help = 'Registers images for GEE analysis (bypassing local preprocessing)'

    def handle(self, *args, **options):
        # In GEE workflow, we don't download/process files locally.
        # We just mark them as ready by creating a ProcessedImage record.
        
        images = SatelliteImage.objects.filter(processed_version__isnull=True)
        self.stdout.write(f"Found {images.count()} images pending GEE registration...")

        for img in images:
            if not img.gee_id:
                self.stdout.write(f"Skipping {img.image_id}: No GEE ID.")
                continue
                
            ProcessedImage.objects.create(
                satellite_image=img,
                processed_file_path="GEE_COMPUTED",
                processed_metadata={'method': 'GEE_SERVER_SIDE'}
            )
            self.stdout.write(f"  - Registered {img.image_id} for GEE analysis.")

        self.stdout.write(self.style.SUCCESS("GEE Registration complete."))
