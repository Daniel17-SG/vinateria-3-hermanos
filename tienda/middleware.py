from django.utils.deprecation import MiddlewareMixin


class NoCacheAuthenticatedMiddleware(MiddlewareMixin):
    """
    Middleware que inyecta cabeceras anti-caché a TODAS las respuestas
    cuando el usuario está autenticado. Elimina el problema de "sesiones fantasma".
    """
    
    def process_response(self, request, response):
        if not request.user.is_authenticated:
            return response
        
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response
