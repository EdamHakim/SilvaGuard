import numpy as np

class DeforestationDetector:
    """
    Detects changes in forest cover between two vegetation analysis results.
    """

    def detect_loss(self, ndvi_before: np.ndarray, ndvi_after: np.ndarray, threshold: float = 0.5) -> dict:
        """
        Compares two NDVI arrays to find areas that transitioned from Forest (>threshold) to Non-Forest (<threshold).
        
        Args:
            ndvi_before: NDVI array from earlier date.
            ndvi_after: NDVI array from later date.
            threshold: Forest threshold (default 0.5).
            
        Returns:
            dict: {
                'loss_pixels': int,
                'loss_percentage': float, # Relative to initial forest area
                'change_mask': np.ndarray
            }
        """
        # Identify forest in "before" image
        forest_before = ndvi_before > threshold
        
        # Identify forest in "after" image
        forest_after = ndvi_after > threshold
        
        # Loss = Was Forest AND Is Now NOT Forest
        loss_mask = forest_before & (~forest_after)
        
        loss_pixels = np.sum(loss_mask)
        initial_forest_pixels = np.sum(forest_before)
        
        if initial_forest_pixels == 0:
            loss_percentage = 0.0
        else:
            loss_percentage = (loss_pixels / initial_forest_pixels) * 100
            
        return {
            'loss_pixels': int(loss_pixels),
            'loss_percentage': float(loss_percentage),
            'change_mask': loss_mask
        }

    def estimate_area_hectares(self, pixel_count: int, pixel_resolution_m: float = 10.0) -> float:
        """
        Estimates area in hectares given a pixel count and resolution (Sentinel-2 is 10m).
        """
        area_sq_m = pixel_count * (pixel_resolution_m ** 2)
        area_hectares = area_sq_m / 10000.0
        return area_hectares
