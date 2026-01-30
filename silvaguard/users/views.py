from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

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
    total_area_ha = sum([314.159 * (aoi.radius_km ** 2) for aoi in aois])
    
    latest_analyses = []
    for aoi in aois:
        latest = VegetationAnalysis.objects.filter(
            processed_image__satellite_image__aoi=aoi
        ).order_by('-processed_image__satellite_image__acquisition_date').first()
        if latest:
            latest_analyses.append(latest)
            
    avg_health = sum([a.forest_cover_percentage for a in latest_analyses]) / len(latest_analyses) if latest_analyses else 0
    
    active_alerts = DeforestationAlert.objects.count()
    total_loss = DeforestationAlert.objects.aggregate(Sum('forest_loss_hectares'))['forest_loss_hectares__sum'] or 0
    
    context = {
        'total_area_ha': int(total_area_ha),
        'avg_health': int(avg_health),
        'active_alerts': active_alerts,
        'total_loss': round(total_loss, 1)
    }
    
    return render(request, 'home.html', context)
