from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import CustomUser

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form, 'next': request.GET.get('next', '')})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    from satellite_data.models import AreaOfInterest, VegetationAnalysis, DeforestationAlert
    from django.db.models import Sum, Avg
    
    aois = AreaOfInterest.objects.all()
    # Total Monitored Area: Sum of (PI * R^2) in hectares
    # Radius is in km, Area = PI * R^2 sq km = 100 * PI * R^2 hectares
    
    if aois.exists():
        total_area_ha = sum([a.radius_km**2 * 3.14159 * 100 for a in aois]) # approx ha
        latest_analyses = VegetationAnalysis.objects.filter(
            processed_image__satellite_image__aoi__in=aois
        ).order_by('-processed_image__satellite_image__acquisition_date')
        avg_health = latest_analyses.first().forest_cover_percentage if latest_analyses.exists() else 0.0
        mode = "Monitored Zones"
    else:
        # Global Fallback - Hardcoded for performance to avoid blocking login
        avg_health = 31.2 # World approximate
        total_area_ha = 14800000000 # World Land Area in ha
        mode = "World Wide"

    active_alerts = DeforestationAlert.objects.count()
    total_loss = sum([a.forest_loss_hectares for a in DeforestationAlert.objects.all()])
    recent_alerts = DeforestationAlert.objects.all().order_by('-detected_at')[:5]
    
    context = {
        'total_area_ha': f"{total_area_ha:,.0f}",
        'avg_health': f"{avg_health:.1f}",
        'active_alerts': active_alerts,
        'total_loss': f"{total_loss:,.1f}",
        'mode': mode,
        'recent_alerts': recent_alerts,
    }
    
    return render(request, 'home.html', context)
