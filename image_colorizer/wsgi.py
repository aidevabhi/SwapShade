"""
WSGI config for image_colorizer project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'image_colorizer.settings')

application = get_wsgi_application()