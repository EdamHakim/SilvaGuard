import ee
from .gee_utils import initialize_gee

class VegetationAnalyzer:
    """
    Performs vegetation analysis on satellite data using Google Earth Engine.
    """
    
    def __init__(self):
        initialize_gee()

    def analyze_gee_image(self, gee_asset_id: str, aoi_geometry=None) -> dict:
        """
        Analyzes a GEE image using Dynamic World (GOOGLE/DYNAMICWORLD/V1).
        
        Args:
            gee_asset_id: The Sentinel-2 Asset ID (e.g., COPERNICUS/S2_SR_HARMONIZED/...)
            aoi_geometry: ee.Geometry object defining the area to reduce over.
            
        Returns:
            dict: Statistics including forest percentage (based on Dynamic World 'trees' class).
        """
        try:
            # 1. Get the S2 Image (for geometry/time)
            s2_image = ee.Image(gee_asset_id)
            region = aoi_geometry if aoi_geometry else s2_image.geometry()
            
            # 2. Find matching Dynamic World Image
            # Dynamic World images match S2 by time and bounds
            # We filter the DW collection 
            dw_col = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1") \
                .filterBounds(region) \
                .filterDate(s2_image.date(), s2_image.date().advance(1, 'day')) \
                .filter(ee.Filter.eq('system:index', s2_image.get('system:index')))
            
            # 3. Get the DW Image (Mosaic if multiple, but usually 1-to-1)
            # Use query to ensure we get the best match or closest in time
            dw_image = ee.Image(dw_col.first())
            
            if not dw_image:
                 # Fallback: Try simpler time filter if system:index doesn't align perfectly
                 dw_col = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1") \
                    .filterBounds(region) \
                    .filterDate(s2_image.date().advance(-2, 'hour'), s2_image.date().advance(2, 'hour'))
                 dw_image = ee.Image(dw_col.first())

            if not dw_image:
                 print(f"No Dynamic World image found for {gee_asset_id}")
                 return {'mean_ndvi': 0.0, 'forest_percentage': 0.0}

            # 4. Extract 'trees' probability (Band 'trees')
            # Dynamic World bands: water, trees, grass, flooded_vegetation, crops, shrub_and_scrub, built, bare, snow_and_ice
            trees_prob = dw_image.select('trees')
            
            # 5. Define Forest Mask (Probability > 0.5)
            forest_mask = trees_prob.gt(0.5).rename('FOREST')
            
            # 6. Statistics
            stats = forest_mask.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=region,
                scale=20,
                maxPixels=1e9
            )
            
            forest_fraction = stats.get('FOREST').getInfo()
            
            # For 'mean_ndvi' field (legacy name), we can store mean tree probability
            mean_prob_stats = trees_prob.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=region,
                scale=20,
                maxPixels=1e9
            )
            mean_tree_prob = mean_prob_stats.get('trees').getInfo()

            return {
                'mean_ndvi': mean_tree_prob if mean_tree_prob else 0.0, # Reuse field for Tree Prob
                'min_ndvi': 0.0,
                'max_ndvi': 1.0,
                'forest_percentage': forest_fraction * 100 if forest_fraction else 0.0
            }

        except Exception as e:
            print(f"GEE Analysis Failed for {gee_asset_id}: {e}")
            return {
                'mean_ndvi': 0.0, 'min_ndvi': 0.0, 'max_ndvi': 0.0, 'forest_percentage': 0.0
            }

    def get_gee_tile_url(self, gee_asset_id: str) -> str:
        """
        Generates a temporary Tile URL from GEE for the 'trees' probability.
        """
        try:
            s2_image = ee.Image(gee_asset_id)
            region = s2_image.geometry()
            
            # Find matching Dynamic World Image
            dw_col = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1") \
                .filterBounds(region) \
                .filterDate(s2_image.date(), s2_image.date().advance(1, 'day')) \
                .filter(ee.Filter.eq('system:index', s2_image.get('system:index')))
            
            dw_image = ee.Image(dw_col.first())
            
            if not dw_image:
                 dw_col = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1") \
                    .filterBounds(region) \
                    .filterDate(s2_image.date().advance(-2, 'hour'), s2_image.date().advance(2, 'hour'))
                 dw_image = ee.Image(dw_col.first())

            if not dw_image:
                return ""

            # Class 1 = Trees. Visualize probability.
            trees_prob = dw_image.select('trees')
            
            # Visualization parameters
            viz_params = {
                'min': 0,
                'max': 1,
                'palette': ['#000000', '#10b981'] # Black to SilvaGuard Green
            }
            
            map_id = trees_prob.getMapId(viz_params)
            return map_id['tile_fetcher'].url_format
            
        except Exception as e:
            print(f"Failed to get Tile URL: {e}")
            return ""

    def generate_heatmap(self, gee_asset_id: str):
        """
        Returns the GEE Tile URL.
        """
        return self.get_gee_tile_url(gee_asset_id)
