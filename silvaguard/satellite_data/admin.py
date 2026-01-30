from django.contrib import admin
from .models import AreaOfInterest, SatelliteImage

@admin.register(AreaOfInterest)
class AreaOfInterestAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'radius_km', 'created_at')
    search_fields = ('name',)

@admin.register(SatelliteImage)
class SatelliteImageAdmin(admin.ModelAdmin):
    list_display = ('image_id', 'aoi', 'acquisition_date', 'cloud_coverage', 'satellite_name')
    list_filter = ('satellite_name', 'aoi', 'acquisition_date')
    search_fields = ('image_id', 'aoi__name')
