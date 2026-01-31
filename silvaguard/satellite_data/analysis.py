import ee
import datetime
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
                maxPixels=1e12
            )
            
            forest_fraction = stats.get('FOREST').getInfo()
            
            # For 'mean_ndvi' field (legacy name), we can store mean tree probability
            mean_prob_stats = trees_prob.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=region,
                scale=20,
                maxPixels=1e12
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

    def get_loss_tile_url(self, gee_asset_before: str, gee_asset_after: str) -> str:
        """
        Generates a Tile URL highlighting the forest loss areas.
        """
        try:
            img_before = ee.Image(gee_asset_before)
            img_after = ee.Image(gee_asset_after)
            
            # Get Dynamic World for both
            def get_dw(img):
                region = img.geometry()
                dw_col = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1") \
                    .filterBounds(region) \
                    .filterDate(img.date(), img.date().advance(1, 'day')) \
                    .filter(ee.Filter.eq('system:index', img.get('system:index')))
                dw = ee.Image(dw_col.first())
                if not dw:
                    dw_col = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1") \
                        .filterBounds(region) \
                        .filterDate(img.date().advance(-2, 'hour'), img.date().advance(2, 'hour'))
                    dw = ee.Image(dw_col.first())
                return dw

            dw_before = get_dw(img_before)
            dw_after = get_dw(img_after)
            
            if not dw_before or not dw_after:
                return ""
                
            # Forest Mask (Prob > 0.5)
            forest_before = dw_before.select('trees').gt(0.5)
            forest_after = dw_after.select('trees').gt(0.5)
            
            # Loss = Was Forest AND Is Now NOT Forest
            loss = forest_before.And(forest_after.Not()).rename('loss')
            
            # Mask so we only show the loss (1s)
            loss_masked = loss.updateMask(loss)
            
            # Visualization
            viz_params = {
                'min': 0,
                'max': 1,
                'palette': ['#ef4444'] #SilvaGuard Red
            }
            
            map_id = loss_masked.getMapId(viz_params)
            return map_id['tile_fetcher'].url_format
            
        except Exception as e:
            print(f"Failed to generate loss tile: {e}")
            return ""

    def calculate_forest_loss(self, gee_asset_before: str, gee_asset_after: str, region=None) -> dict:
        """
        Calculates forest loss in hectares between two dates using GEE.
        """
        try:
            img_before = ee.Image(gee_asset_before)
            img_after = ee.Image(gee_asset_after)
            
            if not region:
                region = img_after.geometry()

            # Get Dynamic World
            def get_dw(img):
                dw_col = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1") \
                    .filterBounds(img.geometry()) \
                    .filterDate(img.date(), img.date().advance(1, 'day')) \
                    .filter(ee.Filter.eq('system:index', img.get('system:index')))
                dw = ee.Image(dw_col.first())
                if not dw:
                    dw_col = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1") \
                        .filterBounds(img.geometry()) \
                        .filterDate(img.date().advance(-2, 'hour'), img.date().advance(2, 'hour'))
                    dw = ee.Image(dw_col.first())
                return dw

            dw_before = get_dw(img_before)
            dw_after = get_dw(img_after)
            
            if not dw_before or not dw_after:
                return {'loss_ha': 0.0, 'loss_percentage': 0.0}

            # Forest Mask (Prob > 0.5)
            forest_before = dw_before.select('trees').gt(0.5)
            forest_after = dw_after.select('trees').gt(0.5)
            
            # Loss = Was Forest (1) AND Is Now NOT Forest (1)
            loss = forest_before.And(forest_after.Not()).rename('loss')
            
            # Calculate Area using pixelArea()
            area_image = loss.multiply(ee.Image.pixelArea())
            
            stats = area_image.reduceRegion(
                reducer=ee.Reducer.sum(),
                geometry=region,
                scale=10,
                maxPixels=1e12
            )
            
            loss_sq_m = stats.get('loss').getInfo()
            loss_ha = (loss_sq_m / 10000.0) if loss_sq_m else 0.0
            
            # Initial Forest Area for percentage
            initial_area_image = forest_before.multiply(ee.Image.pixelArea())
            initial_stats = initial_area_image.reduceRegion(
                reducer=ee.Reducer.sum(),
                geometry=region,
                scale=10,
                maxPixels=1e12
            )
            initial_forest_sq_m = initial_stats.get('trees').getInfo() if 'trees' in initial_stats.getInfo() else initial_stats.get('constant').getInfo()
            # Dynamic World select('trees').gt(0.5) might return 'trees' or 'constant' in stats
            
            # Fallback for key name
            if not initial_forest_sq_m:
                 # Try finding any non-zero value in stats
                 val_list = list(initial_stats.getInfo().values())
                 initial_forest_sq_m = val_list[0] if val_list else 0.0

            loss_pct = (loss_ha / (initial_forest_sq_m/10000.0) * 100) if initial_forest_sq_m and initial_forest_sq_m > 0 else 0.0

            return {
                'loss_ha': loss_ha,
                'loss_percentage': loss_pct
            }
            
        except Exception as e:
            print(f"Failed to calculate forest loss: {e}")
            return {'loss_ha': 0.0, 'loss_percentage': 0.0}

    def get_global_stats(self) -> dict:
        """
        Calculates forest statistics for the entire world using a coarse scale.
        """
        try:
            # Use most recent month for stats
            now_str = datetime.datetime.now().strftime('%Y-%m-%d')
            end_date = ee.Date(now_str)
            start_date = end_date.advance(-1, 'month')
            
            # Global collection
            dw_col = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1").filterDate(start_date, end_date)
            
            # Median composite for stability
            mosaic = dw_col.select('trees').median()
            
            # Binary mask (>0.5 prob)
            forest_mask = mosaic.gt(0.5)
            
            # Reduce over global bounds at coarse scale (e.g. 10km)
            # Scaling is CRITICAL for global results to not time out
            stats = forest_mask.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=ee.Geometry.Rectangle([-180, -90, 180, 90], 'EPSG:4326', False),
                scale=5000, 
                maxPixels=1e13
            )
            
            forest_fraction = stats.get('trees').getInfo()
            
            # Total Land Area check (approx world land area in ha: ~14.8 billion)
            # But let's just use the fraction
            
            return {
                'avg_forest_prob': forest_fraction * 100 if forest_fraction else 0.0,
                'is_global': True
            }
        except Exception as e:
            print(f"Global Stats Failed: {e}")
            return {'avg_forest_prob': 0.0, 'is_global': False}

    def get_global_stats(self) -> dict:
        """
        Calculates forest statistics for the entire world using a coarse scale.
        """
        try:
            # Use most recent month for stats
            now_str = datetime.datetime.now().strftime('%Y-%m-%d')
            end_date = ee.Date(now_str)
            start_date = end_date.advance(-1, 'month')
            
            # Global collection
            dw_col = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1").filterDate(start_date, end_date)
            
            # Median composite for stability
            mosaic = dw_col.select('trees').median()
            
            # Binary mask (>0.5 prob)
            forest_mask = mosaic.gt(0.5)
            
            # Reduce over global bounds at coarse scale (e.g. 5km)
            stats = forest_mask.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=ee.Geometry.Rectangle([-180, -90, 180, 90], 'EPSG:4326', False),
                scale=5000, 
                maxPixels=1e13
            )
            
            forest_fraction = stats.get('trees').getInfo()
            
            return {
                'avg_forest_prob': forest_fraction * 100 if forest_fraction else 0.0,
                'is_global': True
            }
        except Exception as e:
            print(f"Global Stats Failed: {e}")
            return {'avg_forest_prob': 0.0, 'is_global': False}

    def get_mosaic_tile_url(self, lat: float = None, lon: float = None, radius_km: float = None) -> str:
        """
        Generates a Mosaic Tile URL.
        If lat/lon/radius are provided, it clips to that area.
        Otherwise, it returns a global mosaic.
        """
        try:
            # Use a recent 3-month window for a stable mosaic
            now_str = datetime.datetime.now().strftime('%Y-%m-%d')
            end_date = ee.Date(now_str)
            start_date = end_date.advance(-3, 'month')
            
            dw_col = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1") \
                .filterDate(start_date, end_date)
            
            if lat is not None and lon is not None and radius_km is not None:
                point = ee.Geometry.Point([lon, lat])
                region = point.buffer(radius_km * 1000)
                dw_col = dw_col.filterBounds(region)
                # For specific regions, we can be more aggressive with mean/median
                mosaic = dw_col.select('trees').mean().clip(region)
            else:
                # Global Mode: Use a lower resolution mean for performance
                mosaic = dw_col.select('trees').mean()
            
            viz_params = {
                'min': 0,
                'max': 1,
                'palette': ['#000000', '#10b981'] # Black to SilvaGuard Green
            }
            
            map_id = mosaic.getMapId(viz_params)
            return map_id['tile_fetcher'].url_format
            
        except Exception as e:
            print(f"Failed to generate mosaic tile: {e}")
            return ""

    def generate_heatmap(self, gee_asset_id: str):
        """
        Returns the GEE Tile URL.
        """
        return self.get_gee_tile_url(gee_asset_id)
