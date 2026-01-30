from django.contrib import admin
from .models import AreaOfInterest, SatelliteImage, ProcessedImage, VegetationAnalysis, DeforestationAlert

@admin.register(AreaOfInterest)
class AreaOfInterestAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'radius_km', 'created_at')
    search_fields = ('name',)

@admin.register(SatelliteImage)
class SatelliteImageAdmin(admin.ModelAdmin):
    list_display = ('image_id', 'aoi', 'acquisition_date', 'cloud_coverage', 'satellite_name')
    list_filter = ('satellite_name', 'aoi', 'acquisition_date')
    search_fields = ('image_id', 'aoi__name')

@admin.register(ProcessedImage)
class ProcessedImageAdmin(admin.ModelAdmin):
    list_display = ('satellite_image', 'processed_date', 'ndvi_mean')

@admin.register(VegetationAnalysis)
class VegetationAnalysisAdmin(admin.ModelAdmin):
    list_display = ('processed_image', 'mean_ndvi', 'forest_cover_percentage', 'analysis_date')

@admin.register(DeforestationAlert)
class DeforestationAlertAdmin(admin.ModelAdmin):
    list_display = ('aoi', 'forest_loss_hectares', 'loss_percentage', 'detected_at')
    list_filter = ('aoi', 'detected_at')
