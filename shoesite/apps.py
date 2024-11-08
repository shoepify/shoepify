# apps.py
from django.apps import AppConfig

class ShoesiteConfig(AppConfig):
    name = 'shoesite'

    def ready(self):
        import shoesite.signals  # Ensure signals are imported when the app is ready
