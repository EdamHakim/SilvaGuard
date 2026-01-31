from django.urls import path
from . import views

urlpatterns = [
    path('aois/', views.aoi_list, name='aoi_list'),
    path('aois/add/', views.aoi_create, name='aoi_create'),
    path('alerts/<int:pk>/', views.alert_detail, name='alert_detail'),
    path('pulse/', views.guard_pulse_trigger, name='guard_pulse_trigger'),
    path('api/map-data/', views.api_get_map_data, name='api_map_data'),
]
