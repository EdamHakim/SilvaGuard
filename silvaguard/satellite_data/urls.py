from django.urls import path
from . import views

urlpatterns = [
    path('api/map-data/', views.api_get_map_data, name='api_map_data'),
]
