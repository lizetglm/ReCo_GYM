from django.conf import settings
import secrets
import string

class SecurityHeadersMiddleware:
    """
    Middleware que añade cabeceras HTTP de seguridad a todas las respuestas.
    Protege contra: clickjacking, MIME-sniffing, ataques XSS, inyección de código, etc.
    Implementa Content-Security-Policy (CSP) estricto para prevenir XSS.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Generar nonce único para cada request (para scripts inline)
        nonce = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        request.csp_nonce = nonce
        
        response = self.get_response(request)
        
        # Evita que navegadores interpreten tipos MIME incorrectos (previene MIME sniffing attacks)
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Evita que la app se incruste en frames de otros sitios (previene clickjacking)
        response['X-Frame-Options'] = 'DENY'
        
        # Protección XSS: Indica al navegador que debe usar su XSS filter
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Controla qué información del Referrer se envía a otros sitios
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Desactiva permisos peligrosos (geolocalización, micrófono, cámara)
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=(), payment=()'
        
        # CSP es la mejor defensa contra XSS. Restringe qué recursos pueden cargarse.
        csp = (
            f"default-src 'self'; "
            f"script-src 'self' 'unsafe-inline' 'nonce-{nonce}'; "
            f"style-src 'self' 'unsafe-inline'; "    # Estilos: self + inline (necesario para compatibilidad)
            f"img-src 'self' data: https:; "          # Imágenes: local, data URIs, y https
            f"font-src 'self' data:; "                # Fuentes: locales y data URIs
            f"connect-src 'self' https:; "            # XHR/Fetch: solo mismo origen y https
            f"frame-ancestors 'none'; "               # No se puede embebed en iframes
            f"form-action 'self'; "                   # Solo enviar formularios al mismo origen
            f"base-uri 'self'; "                      # Restringe el <base> tag
            f"upgrade-insecure-requests;"             # Upgrade HTTP a HTTPS automáticamente
        )
        response['Content-Security-Policy'] = csp
        
        # CSP Report-Only: para testing (reporta violaciones sin bloquear)
        response['Content-Security-Policy-Report-Only'] = csp + f" report-uri /api/csp-report/"
        
        # HSTS: Fuerza HTTPS en futuras requests (solo en producción)
        if getattr(settings, 'SECURE_HSTS_SECONDS', 0):
            response['Strict-Transport-Security'] = f"max-age={settings.SECURE_HSTS_SECONDS}; includeSubDomains; preload"

        return response