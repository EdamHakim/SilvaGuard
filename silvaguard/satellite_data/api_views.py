from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import AreaOfInterest, DeforestationAlert

@login_required
def get_aois(request):
    """
    Returns a list of all Areas of Interest as JSON.
    """
    aois = AreaOfInterest.objects.all()
    data = []
    for aoi in aois:
        data.append({
            'id': aoi.id,
            'name': aoi.name,
            'latitude': aoi.latitude,
            'longitude': aoi.longitude,
            'radius_km': aoi.radius_km,
        })
    return JsonResponse({'status': 'success', 'data': data})

@login_required
def get_alerts(request):
    """
    Returns a list of all active Deforestation Alerts as JSON.
    """
    alerts = DeforestationAlert.objects.all().select_related('aoi')
    data = []
    for alert in alerts:
        data.append({
            'id': alert.id,
            'aoi_name': alert.aoi.name,
            'lat': alert.aoi.latitude, # Simplifying: using AOI center for alert marker
            'lon': alert.aoi.longitude,
            'loss_ha': alert.forest_loss_hectares,
            'loss_pct': alert.loss_percentage,
            'date': alert.detected_at.strftime('%Y-%m-%d'),
        })
    return JsonResponse({'status': 'success', 'data': data})
