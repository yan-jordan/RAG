# directory: project/asgi.py
import os
from django.core.asm_provider import get_asgi_application # For older versions
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

application = get_asgi_application()