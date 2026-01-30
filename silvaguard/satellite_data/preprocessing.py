import numpy as np
# import rasterio # Commented out for now to ensure code runs even if install fails/mocks are needed
# from rasterio.mask import mask

class ImagePreprocessor:
    """
    Handles cleaning and preparing raw satellite data.
    """

    def process_image(self, raw_image_path):
        """
        Main pipeline: Load -> Cloud Mask -> Normalize -> Band Select.
        """
        # Mocking the pipeline for the hackathon prototype if raw files aren't present
        print(f"Processing image at {raw_image_path}...")
        
        # 1. Load Image (Mocking a 4-band image: R, G, B, NIR)
        # In reality: with rasterio.open(raw_image_path) as src: ...
        mock_data = np.random.rand(4, 100, 100) # 4 bands, 100x100 pixels
        
        # 2. Cloud Masking
        # Identify pixels with high values in Blue/Cirrus bands (Band 0 index for mock)
        # Simple thresholding mock
        cloud_mask = mock_data[0, :, :] > 0.8 # Assume high blue reflectance = cloud
        
        # Apply mask (set to NaN or 0)
        clean_data = mock_data.copy()
        for i in range(4):
            clean_data[i][cloud_mask] = 0.0 # simple cloud removal
            
        # 3. Normalization (Sentinel-2 is usually 0-10000, we want 0-1)
        # data = data / 10000.0
        # Our mock is already 0-1
        
        # 4. Band Selection (Extract Red and NIR for NDVI)
        # Assuming Band 0=Blue, 1=Green, 2=Red, 3=NIR
        red_band = clean_data[2]
        nir_band = clean_data[3]
        
        return {
            'red': red_band,
            'nir': nir_band,
            'cloud_mask': cloud_mask,
            'metadata': {'cloud_pixels_masked': int(np.sum(cloud_mask))}
        }

    def calculate_ndvi(self, red_band, nir_band):
        """
        (NIR - Red) / (NIR + Red)
        """
        # Handle division by zero
        denominator = (nir_band + red_band)
        denominator[denominator == 0] = 0.0001
        
        ndvi = (nir_band - red_band) / denominator
        return ndvi
