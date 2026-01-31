from django.core.management.base import BaseCommand
from satellite_data.services import SilvaGuardOrchestrator

class Command(BaseCommand):
    help = 'Triggers the SilvaGuard Monitoring Pulse (Collect -> Analyze -> Detect)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=15,
            help='Number of past days to check for new images (default: 15)'
        )
        parser.add_argument(
            '--max-cloud',
            type=float,
            default=20.0,
            help='Maximum cloud cover percentage allowed (default: 20.0)'
        )

    def handle(self, *args, **options):
        days = options['days']
        max_cloud = options['max_cloud']
        
        self.stdout.write(self.style.MIGRATE_HEADING(f"🚀 Starting SilvaGuard Pulse ({days} days window)..."))
        
        orchestrator = SilvaGuardOrchestrator()
        results = orchestrator.run_pulse(days=days, max_cloud=max_cloud)
        
        self.stdout.write(self.style.SUCCESS("\n✅ SilvaGuard Pulse Complete"))
        self.stdout.write(f"  - AOIs Processed: {results['aois_processed']}")
        self.stdout.write(f"  - New Images: {results['new_images']}")
        self.stdout.write(f"  - Alerts Created: {results['alerts_created']}")
