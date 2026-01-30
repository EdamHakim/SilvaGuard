from django.core.management.base import BaseCommand
from django.utils import timezone
from satellite_data.models import AreaOfInterest, SatelliteImage
from satellite_data.services import Sentinel2Service
from datetime import timedelta

class Command(BaseCommand):
    help = 'Collects satellite image metadata for all defined Areas of Interest'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of past days to search for images (default: 7)'
        )
        parser.add_argument(
            '--max-cloud',
            type=float,
            default=20.0,
            help='Maximum allowed cloud coverage percentage (default: 20.0)'
        )

    def handle(self, *args, **options):
        days = options['days']
        max_cloud = options['max_cloud']
        
        service = Sentinel2Service()
        aois = AreaOfInterest.objects.all()

        if not aois.exists():
            self.stdout.write(self.style.WARNING('No Areas of Interest found. Please add an AOI in the admin panel.'))
            return

        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        self.stdout.write(f"Searching for Sentinel-2 images from {start_date.date()} to {end_date.date()}...")

        total_new_images = 0

        for aoi in aois:
            self.stdout.write(f"Processing AOI: {aoi.name}...")
            
            try:
                images_metadata = service.fetch_metadata(
                    aoi_lat=aoi.latitude,
                    aoi_lon=aoi.longitude,
                    start_date=start_date,
                    end_date=end_date,
                    max_cloud_cover=max_cloud
                )

                new_images_count = 0
                for meta in images_metadata:
                    # detailed metadata can be stored in the JSONField
                    extra_data = {
                        'platform': meta.get('platform'),
                        'processing_level': meta.get('processing_level')
                    }

                    # Create record if it doesn't exist
                    obj, created = SatelliteImage.objects.get_or_create(
                        image_id=meta['image_id'],
                        defaults={
                            'aoi': aoi,
                            'acquisition_date': meta['acquisition_date'],
                            'cloud_coverage': meta['cloud_coverage'],
                            'satellite_name': meta['satellite_name'],
                            'metadata_json': extra_data
                        }
                    )
                    
                    if created:
                        new_images_count += 1

                self.stdout.write(self.style.SUCCESS(f"  - Found {len(images_metadata)} images, {new_images_count} new."))
                total_new_images += new_images_count

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  - Error processing {aoi.name}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"\nCollection complete. Total new images saved: {total_new_images}"))
