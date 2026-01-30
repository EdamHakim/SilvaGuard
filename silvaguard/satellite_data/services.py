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
                .sort('CLOUDY_PIXEL_PERCENTAGE')

            # 3. Get Metadata (Limit to 50 to avoid overloading)
            # Fetching 'system:index', 'CLOUDY_PIXEL_PERCENTAGE', etc.
            images_info = s2.limit(50).getInfo()

            if 'features' in images_info:
                for img in images_info['features']:
                    props = img['properties']
                    
                    # Construct metadata object
                    metadata = {
                        'image_id': img['id'], # e.g., COPERNICUS/S2_SR/20210101T...
                        'acquisition_date': props.get('DATATAKE_IDENTIFIER', '').split('_')[1], # extracting date from ID roughly, or use 'system:time_start'
                        # Better way to get date:
                        # 'acquisition_date': datetime.fromtimestamp(props['system:time_start']/1000), 
                        # But for simplicity let's rely on Django handling strings or convert nicely
                         
                        'cloud_coverage': props.get('CLOUDY_PIXEL_PERCENTAGE', 0),
                        'satellite_name': 'Sentinel-2',
                        'platform': props.get('SPACECRAFT_NAME', 'Sentinel-2'),
                        'processing_level': 'Level-2A',
                        'center_latitude': aoi_lat,
                        'center_longitude': aoi_lon,
                        'gee_id': img['id'] # Store GEE ID for later processing
                    }
                    
                    # Date conversion
                    # GEE returns time in ms timestamp
                    import datetime
                    timestamp = props.get('system:time_start')
                    if timestamp:
                        metadata['acquisition_date'] = datetime.datetime.fromtimestamp(timestamp / 1000.0)

                    results.append(metadata)

        except Exception as e:
            print(f"Error fetching GEE data: {e}")

        return results
