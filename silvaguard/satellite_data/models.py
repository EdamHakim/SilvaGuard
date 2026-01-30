from django.db import models

class AreaOfInterest(models.Model):
    """
    Represents a geographic area to monitor.
    Currently defined by a center point (lat/lon) and a radius.
    """
    name = models.CharField(max_length=100, help_text="Descriptive name for the area")
    latitude = models.FloatField(help_text="Latitude of the center point")
    longitude = models.FloatField(help_text="Longitude of the center point")
    radius_km = models.FloatField(default=10.0, help_text="Radius of the area in kilometers")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class SatelliteImage(models.Model):
    """
    Metadata for a satellite image captured over an AOI.
    Stores reference to the external image (Sentinel-2) but not the raw data.
    """
    aoi = models.ForeignKey(AreaOfInterest, on_delete=models.CASCADE, related_name='images')
    acquisition_date = models.DateTimeField(help_text="Date and time when the image was captured")
    cloud_coverage = models.FloatField(help_text="Cloud coverage percentage (0-100)")
    satellite_name = models.CharField(max_length=50, default='Sentinel-2')
    image_id = models.CharField(max_length=255, unique=True, help_text="Unique identifier from the satellite provider")
    gee_id = models.CharField(max_length=255, null=True, blank=True, help_text="Google Earth Engine Asset ID")
    metadata_json = models.JSONField(null=True, blank=True, help_text="Additional metadata from the provider")

    class Meta:
        ordering = ['-acquisition_date']

    def __str__(self):
        return f"{self.satellite_name} - {self.acquisition_date.strftime('%Y-%m-%d')} ({self.cloud_coverage}%)"

class ProcessedImage(models.Model):
    """
    Stores metadata and file paths for preprocessed satellite imagery.
    Linked to the original raw SatelliteImage.
    """
    satellite_image = models.OneToOneField(SatelliteImage, on_delete=models.CASCADE, related_name='processed_version')
    processed_file_path = models.CharField(max_length=255, help_text="Path to the processed GeoTIFF/Array file")
    processed_date = models.DateTimeField(auto_now_add=True)
    ndvi_mean = models.FloatField(null=True, blank=True, help_text="Average NDVI value for quick reference")
    
    processed_metadata = models.JSONField(default=dict, help_text="Details on masking, normalization, etc.")

    def __str__(self):
        return f"Processed: {self.satellite_image.image_id}"

class VegetationAnalysis(models.Model):
    """
    Results of vegetation analysis (NDVI) performed on a preprocessed image.
    """
    processed_image = models.OneToOneField(ProcessedImage, on_delete=models.CASCADE, related_name='vegetation_analysis')
    mean_ndvi = models.FloatField(help_text="Average NDVI value for the area")
    forest_cover_percentage = models.FloatField(help_text="Percentage of pixels classified as forest (NDVI > 0.5)")
    heatmap_file_path = models.TextField(help_text="Path or URL to the visual NDVI heatmap")
    analysis_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"NDVI Analysis: {self.processed_image.satellite_image.image_id}"

class DeforestationAlert(models.Model):
    """
    Represents a detected deforestation event between two time periods.
    """
    aoi = models.ForeignKey(AreaOfInterest, on_delete=models.CASCADE, related_name='alerts')
    analysis_before = models.ForeignKey(VegetationAnalysis, on_delete=models.CASCADE, related_name='alerts_as_before')
    analysis_after = models.ForeignKey(VegetationAnalysis, on_delete=models.CASCADE, related_name='alerts_as_after')
    
    forest_loss_hectares = models.FloatField(help_text="Estimated area of forest lost in hectares")
    loss_percentage = models.FloatField(help_text="Percentage of forest lost relative to previous state")
    detected_at = models.DateTimeField(auto_now_add=True)
    
    # In a real system, this would store a polygon or heatmap of the specific loss area
    loss_map_path = models.TextField(null=True, blank=True, help_text="Path or URL to the visual change map")
    
    def __str__(self):
        return f"Alert: {self.aoi.name} - {self.forest_loss_hectares:.2f}ha lost"


