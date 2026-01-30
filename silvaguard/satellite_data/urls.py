from django.urls import path
from . import api_views

urlpatterns = [
    path('api/aois/', api_views.get_aois, name='get_aois'),
    path('api/alerts/', api_views.get_alerts, name='get_alerts'),
]
