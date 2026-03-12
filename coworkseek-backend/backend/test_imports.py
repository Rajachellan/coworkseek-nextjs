import traceback
import sys

try:
    import django
    from django.conf import settings
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()
    print("Django setup successful")
    
    from api.models import Location
    print("Models imported successfully")
    
except Exception:
    traceback.print_exc()
