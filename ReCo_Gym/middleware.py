from django.conf import settings

class SecurityHeadersMiddleware:
    """
    Middleware que añade cabeceras HTTP de seguridad a todas las respuestas.
    Protege contra: clickjacking, MIME-sniffing, ataques XSS, etc.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Evita que navegadores interpreten tipos MIME incorrectos
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Evita que la app se incruste en frames de otros sitios 
        response['X-Frame-Options'] = 'DENY'
        
        # Controla qué información del Referrer se envía a otros sitios **
        response['Referrer-Policy'] = 'same-origin'
        
        # Desactiva permisos peligrosos (geolocalización, micrófono)
        response['Permissions-Policy'] = 'geolocation=(), microphone=()'
        
        # Content Security Policy básico (ajusta según tus recursos)
        response['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
        
        # HSTS (fuerza HTTPS, solo si lo tienes habilitado)
        if getattr(settings, 'SECURE_HSTS_SECONDS', 0):
            response['Strict-Transport-Security'] = f"max-age={settings.SECURE_HSTS_SECONDS}; includeSubDomains"

        return response