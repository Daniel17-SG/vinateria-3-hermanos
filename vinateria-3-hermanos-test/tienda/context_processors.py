from django.conf import settings

def google_maps_config(request):
    """Context processor para hacer disponible la API Key de Google Maps en todas las plantillas"""
    return {
        'GOOGLE_MAPS_API_KEY': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }
