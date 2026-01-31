import ee
from datetime import timedelta
from typing import List, Dict, Any
from .gee_utils import initialize_gee

class Sentinel2Service:
    """
    Service to handle interactions with Sentinel-2 via Google Earth Engine.
    """

    def __init__(self):
        initialize_gee()

    def fetch_metadata(self, aoi_lat: float, aoi_lon: float, start_date, end_date, max_cloud_cover: float = 20.0) -> List[Dict[str, Any]]:
        """
        Fetches metadata for available Sentinel-2 images over a specific area using GEE.
        """
        results = []
        
        try:
            # 1. Define Point and Region (Buffer)
            point = ee.Geometry.Point([aoi_lon, aoi_lat])
            region = point.buffer(10000).bounds() # 10km buffer approx

            # 2. Filter Collection
            s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
                .filterBounds(region) \
                .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', max_cloud_cover)) \
                .sort('system:time_start', False) # Newest first

            # 3. Get Metadata
            images_info = s2.limit(10).getInfo()

            if 'features' in images_info:
                for img in images_info['features']:
                    props = img['properties']
                    
                    import datetime
                    timestamp = props.get('system:time_start')
                    acquisition_date = datetime.datetime.fromtimestamp(timestamp / 1000.0, tz=datetime.timezone.utc) if timestamp else None

                    metadata = {
                        'image_id': img['id'],
                        'acquisition_date': acquisition_date,
                        'cloud_coverage': props.get('CLOUDY_PIXEL_PERCENTAGE', 0),
                        'satellite_name': 'Sentinel-2',
                        'platform': props.get('SPACECRAFT_NAME', 'Sentinel-2'),
                        'processing_level': 'Level-2A',
                        'center_latitude': aoi_lat,
                        'center_longitude': aoi_lon,
                        'gee_id': img['id']
                    }
                    results.append(metadata)

        except Exception as e:
            print(f"Error fetching GEE data: {e}")

        return results

class SilvaGuardOrchestrator:
    """
    The Orchestrator that manages the automated monitoring pulse.
    """

    def __init__(self):
        from .analysis import VegetationAnalyzer
        self.s2_service = Sentinel2Service()
        self.analyzer = VegetationAnalyzer()

    def run_pulse(self, days=7, max_cloud=20.0):
        """
        Executes a full monitoring cycle for all AOIs.
        """
        from .models import AreaOfInterest, SatelliteImage, ProcessedImage, VegetationAnalysis, DeforestationAlert
        from django.utils import timezone
        
        aois = AreaOfInterest.objects.all()
        pulse_results = {'aois_processed': 0, 'new_images': 0, 'alerts_created': 0}

        for aoi in aois:
            print(f"--- Pulsing AOI: {aoi.name} ---")
            pulse_results['aois_processed'] += 1
            
            # 1. Fetch Metadata
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            metadata_list = self.s2_service.fetch_metadata(aoi.latitude, aoi.longitude, start_date, end_date, max_cloud)

            for meta in metadata_list:
                # 2. Register Image
                sat_img, created = SatelliteImage.objects.get_or_create(
                    image_id=meta['image_id'],
                    defaults={
                        'aoi': aoi,
                        'acquisition_date': meta['acquisition_date'],
                        'cloud_coverage': meta['cloud_coverage'],
                        'satellite_name': meta['satellite_name'],
                        'gee_id': meta['gee_id'],
                        'metadata_json': {'platform': meta['platform'], 'processing_level': meta['processing_level']}
                    }
                )

                if created:
                    pulse_results['new_images'] += 1
                    print(f"  [New Image] {sat_img.image_id}")
                
                # 3. Process Image
                proc_img, proc_created = ProcessedImage.objects.get_or_create(
                    satellite_image=sat_img,
                    defaults={
                        'processed_file_path': "GEE_COMPUTED",
                        'processed_metadata': {'method': 'GEE_SERVER_SIDE'}
                    }
                )

                # 4. Analyze Vegetation
                analysis, anal_created = VegetationAnalysis.objects.get_or_create(
                    processed_image=proc_img,
                    defaults={
                        'mean_ndvi': 0.0,
                        'forest_cover_percentage': 0.0,
                        'heatmap_file_path': 'GEE_PENDING'
                    }
                )

                if anal_created or analysis.heatmap_file_path == 'GEE_PENDING':
                    gee_result = self.analyzer.analyze_gee_image(sat_img.gee_id)
                    tile_url = self.analyzer.generate_heatmap(sat_img.gee_id)
                    
                    analysis.mean_ndvi = gee_result['mean_ndvi']
                    analysis.forest_cover_percentage = gee_result['forest_percentage']
                    analysis.heatmap_file_path = tile_url
                    analysis.save()
                    print(f"  [Analyzed] Forest Cover: {analysis.forest_cover_percentage:.1f}%")

            # 5. Detect Deforestation (Comparison Pulse)
            analyses = VegetationAnalysis.objects.filter(
                processed_image__satellite_image__aoi=aoi
            ).order_by('processed_image__satellite_image__acquisition_date')

            if analyses.count() >= 2:
                latest = analyses.last()
                previous = analyses[analyses.count() - 2]
                
                # Only check if alert doesn't exist yet for this pair
                if not DeforestationAlert.objects.filter(analysis_before=previous, analysis_after=latest).exists():
                    print(f"  [Checking Alerts] {previous.analysis_date.date()} vs {latest.analysis_date.date()}")
                    comparison = self.analyzer.calculate_forest_loss(
                        previous.processed_image.satellite_image.gee_id,
                        latest.processed_image.satellite_image.gee_id
                    )
                    
                    if comparison['loss_ha'] > 0.1: # Threshold for alert
                        loss_tile = self.analyzer.get_loss_tile_url(
                            previous.processed_image.satellite_image.gee_id,
                            latest.processed_image.satellite_image.gee_id
                        )
                        alert = DeforestationAlert.objects.create(
                            aoi=aoi,
                            analysis_before=previous,
                            analysis_after=latest,
                            forest_loss_hectares=comparison['loss_ha'],
                            loss_percentage=comparison['loss_percentage'],
                            loss_map_path=loss_tile
                        )
                        pulse_results['alerts_created'] += 1
                        print(f"  [ALERT] {alert.forest_loss_hectares:.2f} ha lost!")

        return pulse_results
