from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import AreaOfInterest, DeforestationAlert, VegetationAnalysis

@login_required
def api_get_map_data(request):
    """
    Returns GeoJSON data for AOIs and Alerts.
    """
    aois = AreaOfInterest.objects.all()
    alerts = DeforestationAlert.objects.all()
    
    features = []
    
    # Add AOIs as Polygons
    for aoi in aois:
        # Get latest analysis for this AOI to show the layer
        latest_analysis = VegetationAnalysis.objects.filter(
            processed_image__satellite_image__aoi=aoi
        ).order_by('-analysis_date').first()
        
        tile_url = latest_analysis.heatmap_file_path if latest_analysis else ""
        
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [aoi.longitude, aoi.latitude]
            },
            "properties": {
                "type": "AOI",
                "id": aoi.id,
                "name": aoi.name,
                "radius_km": aoi.radius_km,
                "tile_url": tile_url,
                "popup": f"<strong>{aoi.name}</strong><br>Radius: {aoi.radius_km}km" + 
                         (f"<br>Forest Cover: {latest_analysis.forest_cover_percentage:.1f}%" if latest_analysis else "")
            }
        })
        
    # Add Alerts
    for alert in alerts:
        # Alerts relate to an AOI. We can place them at the AOI center for now, 
        # or ideally we would have specific coordinates for the alert.
        # Let's put them slightly offset or just same location with different icon?
        # For simplicity, we'll use the AOI location but alert properties.
        
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [alert.aoi.longitude, alert.aoi.latitude]
            },
            "properties": {
                "type": "Alert",
                "id": alert.id,
                "loss_ha": alert.forest_loss_hectares,
                "loss_pct": alert.loss_percentage,
                "date": alert.detected_at.strftime("%Y-%m-%d"),
                "popup": f"⚠️ <strong>Deforestation Alert</strong><br>Loss: {alert.forest_loss_hectares:.1f} ha<br>Date: {alert.detected_at.strftime('%Y-%m-%d')}"
            }
        })

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return JsonResponse(geojson)
