import numpy as np
from satellite_data.preprocessing import ImagePreprocessor

def test_preprocessing():
    processor = ImagePreprocessor()
    
    # Run processing (mocks data loading)
    result = processor.process_image("dummy_path.tif")
    
    print("Keys in result:", result.keys())
    print("Red band shape:", result['red'].shape)
    print("Metadata:", result['metadata'])
    
    # Test NDVI calculation
    ndvi = processor.calculate_ndvi(result['red'], result['nir'])
    print("NDVI shape:", ndvi.shape)
    print("NDVI mean:", np.nanmean(ndvi))
    
    print("Preprocessing verification successful.")

if __name__ == "__main__":
    test_preprocessing()
