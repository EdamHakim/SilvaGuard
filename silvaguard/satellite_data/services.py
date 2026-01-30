import random
from datetime import timedelta
from typing import List, Dict, Any

class Sentinel2Service:
    """
    Service to handle interactions with Sentinel-2 satellite data providers.
    Currently mocks data retrieval for development and testing purposes.
    """

    def fetch_metadata(self, aoi_lat: float, aoi_lon: float, start_date, end_date, max_cloud_cover: float = 20.0) -> List[Dict[str, Any]]:
        """
        Simulates fetching metadata for available Sentinel-2 images over a specific area.

        Args:
            aoi_lat (float): Latitude of the Area of Interest center.
            aoi_lon (float): Longitude of the Area of Interest center.
            start_date (datetime): Start of the search window.
            end_date (datetime): End of the search window.
            max_cloud_cover (float): Maximum acceptable cloud coverage percentage (0-100).

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing image metadata.
        """
        results = []
        current_date = start_date

        # Simulate finding an image every ~5 days (Sentinel-2 revisit time)
        while current_date <= end_date:
            # 80% chance to find an image on a pass day
            if random.random() > 0.2:
                cloud_cover = round(random.uniform(0, 100), 2)
                
                # Filter by cloud coverage
                if cloud_cover <= max_cloud_cover:
                    
                    # Generate a mock unique ID
                    image_id = f"S2_{current_date.strftime('%Y%m%d')}_T{random.randint(10, 60)}XXX_R{random.randint(0, 100)}_{random.randint(1000, 9999)}"
                    
                    metadata = {
                        'image_id': image_id,
                        'acquisition_date': current_date,
                        'cloud_coverage': cloud_cover,
                        'satellite_name': 'Sentinel-2',
                        'platform': 'Sentinel-2A' if random.random() > 0.5 else 'Sentinel-2B',
                        'processing_level': 'Level-2A',
                        'center_latitude': aoi_lat,
                        'center_longitude': aoi_lon
                    }
                    results.append(metadata)

            # Advance 5 days for next potential pass
            current_date += timedelta(days=5)

        return results
