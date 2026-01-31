from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from .models import AreaOfInterest, DeforestationAlert, VegetationAnalysis
from .forms import AreaOfInterestForm

@login_required
def api_get_map_data(request):
    """
    Returns GeoJSON data for AOIs and Alerts.
    """
    aois = AreaOfInterest.objects.all()
    alerts = DeforestationAlert.objects.all()
    
    features = []
    
    # Generate a background mosaic for the "whole map" effect
    global_tile_url = cache.get('global_mosaic_tile_url') # Try to get from cache first

    if not global_tile_url:
        from .analysis import VegetationAnalyzer
        analyzer = VegetationAnalyzer()
        center_aoi = aois.first()
        if center_aoi:
            # Regional focus
            global_tile_url = analyzer.get_mosaic_tile_url(center_aoi.latitude, center_aoi.longitude, 500) # Changed radius to 500km
        else:
            # Global focus if no AOIs exist
            global_tile_url = analyzer.get_mosaic_tile_url() # Call without arguments for global mosaic
        
        if global_tile_url:
            cache.set('global_mosaic_tile_url', global_tile_url, 3600) # Cache for 1 hour (3600 seconds)
    
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
                "tile_url": alert.loss_map_path, # GEE Loss Tile
                "popup": f"⚠️ <strong>Deforestation Alert</strong><br>Loss: {alert.forest_loss_hectares:.1f} ha<br>Date: {alert.detected_at.strftime('%Y-%m-%d')}"
            }
        })

    geojson = {
        "type": "FeatureCollection",
        "features": features,
        "global_tile_url": global_tile_url
    }
    
    print(f"Map Data API: Found {len(features)} features. Global URL length: {len(global_tile_url) if global_tile_url else 0}")
    
    return JsonResponse(geojson)

@login_required
def aoi_list(request):
    """
    Lists all Areas of Interest being monitored.
    """
    aois = AreaOfInterest.objects.all().order_by('-created_at')
    return render(request, 'satellite_data/aoi_list.html', {'aois': aois})

@login_required
def aoi_create(request):
    """
    View to add a new Area of Interest.
    """
    if request.method == 'POST':
        form = AreaOfInterestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('aoi_list')
    else:
        form = AreaOfInterestForm()
    
    return render(request, 'satellite_data/aoi_form.html', {'form': form, 'title': 'Add New Zone'})

@login_required
def guard_pulse_trigger(request):
    """
    Manually triggers the monitoring pulse from the UI.
    """
    if request.method == 'POST':
        from .services import SilvaGuardOrchestrator
        orchestrator = SilvaGuardOrchestrator()
        orchestrator.run_pulse(days=15)
        return redirect('home')

@login_required
def alert_detail(request, pk):
    """
    Detailed report for a specific Deforestation Alert.
    """
    from django.shortcuts import get_object_or_404
    alert = get_object_or_404(DeforestationAlert, pk=pk)
    
    # Get before/after imagery for comparison
    img_before = alert.analysis_before.processed_image.satellite_image
    img_after = alert.analysis_after.processed_image.satellite_image
    
    # We'll pass tiles and metadata to the template
    context = {
        'alert': alert,
        'img_before': img_before,
        'img_after': img_after,
        'aoi': alert.aoi,
    }
    
    return render(request, 'satellite_data/alert_detail.html', context)
    return redirect('home')
