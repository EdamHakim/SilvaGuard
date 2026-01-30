from django.db import models

class AreaOfInterest(models.Model):
    """
    Represents a geographic area to monitor.
    Currently defined by a center point (lat/lon) and a radius.
    Future iterations may use Polygon fields (e.g., GeoDjango).
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
    metadata_json = models.JSONField(null=True, blank=True, help_text="Additional metadata from the provider")

    class Meta:
        ordering = ['-acquisition_date']

    def __str__(self):
        return f"{self.satellite_name} - {self.acquisition_date.strftime('%Y-%m-%d')} ({self.cloud_coverage}%)"
