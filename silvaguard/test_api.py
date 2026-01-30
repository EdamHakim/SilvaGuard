import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silvaguard.settings')

import django
django.setup()

from satellite_data.views import api_get_map_data
from django.test import RequestFactory
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

factory = RequestFactory()
request = factory.get('/satellite/api/map-data/')
request.user = user

response = api_get_map_data(request)
print(response.content.decode('utf-8'))
