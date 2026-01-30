import numpy as np

class VegetationAnalyzer:
    """
    Performs vegetation analysis on preprocessed satellite data.
    """

    def calculate_ndvi(self, red_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
        """
        Calculates Normalized Difference Vegetation Index (NDVI).
        Formula: (NIR - Red) / (NIR + Red)
        """
        # Ensure floating point arithmetic
        red = red_band.astype(float)
        nir = nir_band.astype(float)
        
        # Avoid division by zero
        denominator = (nir + red)
        denominator[denominator == 0] = 0.0001
        
        ndvi = (nir - red) / denominator
        return ndvi

    def analyze_forest_cover(self, ndvi_array: np.ndarray, threshold: float = 0.5) -> dict:
        """
        Analyzes the NDVI array to determine forest coverage metrics.
        
        Args:
            ndvi_array: 2D numpy array of NDVI values.
            threshold: Value above which a pixel is considered 'dense vegetation' or forest.

        Returns:
            dict: {
                'mean_ndvi': float,
                'min_ndvi': float,
                'max_ndvi': float,
                'forest_pixels': int,
                'total_pixels': int,
                'forest_percentage': float
            }
        """
        # Mask out NaN values if any (from cloud masking)
        valid_pixels = ndvi_array[~np.isnan(ndvi_array)]
        
        if valid_pixels.size == 0:
            return {
                'mean_ndvi': 0.0,
                'min_ndvi': 0.0,
                'max_ndvi': 0.0,
                'forest_pixels': 0,
                'total_pixels': 0,
                'forest_percentage': 0.0
            }

        mean_ndvi = np.mean(valid_pixels)
        min_ndvi = np.min(valid_pixels)
        max_ndvi = np.max(valid_pixels)
        
        # Count pixels above threshold
        forest_mask = valid_pixels > threshold
        forest_count = np.sum(forest_mask)
        total_count = valid_pixels.size
        percentage = (forest_count / total_count) * 100
        
        return {
            'mean_ndvi': float(mean_ndvi),
            'min_ndvi': float(min_ndvi),
            'max_ndvi': float(max_ndvi),
            'forest_pixels': int(forest_count),
            'total_pixels': int(total_count),
            'forest_percentage': float(percentage)
        }

    def generate_heatmap(self, ndvi_array: np.ndarray, output_path: str):
        """
        Generates a visual heatmap from the NDVI array (Mock implementation for now).
        In a real scenario, this would use matplotlib or rasterio to save an image.
        """
        # Mock: Just saving a text file pretending to be an image for the prototype
        # Real implementation would save a PNG/JPG or GeoTIFF
        with open(output_path, 'w') as f:
            f.write("Mock NDVI Heatmap File")
        
        return output_path
