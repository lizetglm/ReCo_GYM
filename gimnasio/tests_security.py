"""
Pruebas unitarias para verificar protecciones contra XSS.
Ejecutar con: python manage.py test gimnasio.tests_security

Este archivo contiene pruebas que verifican que la aplicación
está protegida contra ataques XSS comunes.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from gimnasio.models import Socio, Entrenador, Clase
from gimnasio.security import (
    sanitize_text_input,
    sanitize_search_query,
    validate_url,
    validate_phone,
    escape_javascript_string,
    validate_socio_id,
)
from datetime import date


class SecuritySanitizationTest(TestCase):
    """Pruebas de sanitización de entrada"""

    def test_sanitize_text_input_removes_script_tags(self):
        """sanitize_text_input debe remover tags <script>"""
        malicious = '<script>alert("XSS")</script>Texto'
        result = sanitize_text_input(malicious)
        self.assertNotIn('<script>', result)
        self.assertNotIn('alert', result)

    def test_sanitize_text_input_escapes_html(self):
        """sanitize_text_input debe escapar HTML"""
        text = '<div onclick="alert(1)">Click</div>'
        result = sanitize_text_input(text)
        self.assertNotIn('<div', result)
        self.assertIn('&lt;', result)

    def test_sanitize_text_input_limits_length(self):
        """sanitize_text_input debe limitar longitud"""
        long_text = 'a' * 2000
        result = sanitize_text_input(long_text)
        self.assertLessEqual(len(result), 1000)

    def test_sanitize_search_query_removes_dangerous_chars(self):
        """sanitize_search_query debe remover caracteres peligrosos"""
        query = "María<script>'; DROP TABLE users;--"
        result = sanitize_search_query(query)
        self.assertNotIn('<', result)
        self.assertNotIn('>', result)
        self.assertNotIn(';', result)
        self.assertNotIn("'", result)

    def test_sanitize_search_query_allows_normal_text(self):
        """sanitize_search_query debe permitir texto normal"""
        query = "María García"
        result = sanitize_search_query(query)
        # Después del escapado
        self.assertIn('María', result)
        self.assertIn('García', result)

    def test_escape_javascript_string(self):
        """escape_javascript_string debe escapar para JavaScript seguro"""
        text = 'test"value\nwith\rspecial'
        result = escape_javascript_string(text)
        self.assertIn('\\"', result)  # Comilla doble escapada
        self.assertIn('\\n', result)  # Newline escapado
        self.assertNotIn('"', result.replace('\\"', ''))


class SecurityValidationTest(TestCase):
    """Pruebas de validación"""

    def test_validate_url_blocks_javascript(self):
        """validate_url debe bloquear URLs javascript:"""
        self.assertFalse(validate_url('javascript:alert(1)'))

    def test_validate_url_blocks_data_urls(self):
        """validate_url debe bloquear data: URLs"""
        self.assertFalse(validate_url('data:text/html,<script>alert(1)</script>'))

    def test_validate_url_blocks_vbscript(self):
        """validate_url debe bloquear vbscript: URLs"""
        self.assertFalse(validate_url('vbscript:msgbox(1)'))

    def test_validate_url_allows_https(self):
        """validate_url debe permitir https URLs"""
        self.assertTrue(validate_url('https://example.com'))

    def test_validate_url_allows_relative_paths(self):
        """validate_url debe permitir rutas relativas"""
        self.assertTrue(validate_url('/dashboard/'))

    def test_validate_phone_format(self):
        """validate_phone debe validar formatos de teléfono"""
        # Válidos
        self.assertTrue(validate_phone('123-456-7890'))
        self.assertTrue(validate_phone('+1 (123) 456-7890'))
        self.assertTrue(validate_phone('1234567890'))

        # Inválidos
        self.assertFalse(validate_phone('abc'))
        self.assertFalse(validate_phone('123'))

    def test_validate_socio_id_format(self):
        """validate_socio_id debe validar formato de ID"""
        # Válidos
        self.assertTrue(validate_socio_id('S001'))
        self.assertTrue(validate_socio_id('ABC123'))

        # Inválidos
        self.assertFalse(validate_socio_id('001'))  # Sin letra
        self.assertFalse(validate_socio_id('S'))    # Sin número


class XSSProtectionHeadersTest(TestCase):
    """Pruebas de headers de seguridad XSS"""

    def setUp(self):
        self.client = Client()
        # Crear usuario de prueba
        self.user = User.objects.create_user(username='admin', password='test123', is_staff=True)

    def test_security_headers_present(self):
        """Verificar que headers de seguridad están presentes"""
        self.client.login(username='admin', password='test123')
        response = self.client.get('/dashboard/')

        # Verificar headers
        self.assertIn('X-Content-Type-Options', response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')

        self.assertIn('X-Frame-Options', response)
        self.assertEqual(response['X-Frame-Options'], 'DENY')

        self.assertIn('X-XSS-Protection', response)
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')

        self.assertIn('Content-Security-Policy', response)
        self.assertIn("script-src 'self'", response['Content-Security-Policy'])

    def test_csp_header_includes_nonce(self):
        """CSP debe incluir nonce para scripts inline seguros"""
        self.client.login(username='admin', password='test123')
        response = self.client.get('/dashboard/')

        csp = response.get('Content-Security-Policy', '')
        self.assertIn("script-src 'self' 'nonce-", csp)


class SocioFormXSSTest(TestCase):
    """Pruebas XSS en formularios de socio"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='test123', is_staff=True)
        self.client.login(username='admin', password='test123')

    def test_socio_nombre_xss_protection(self):
        """El campo nombre en socio debe estar protegido contra XSS"""
        xss_payload = '<script>alert("XSS")</script>Pedro'

        response = self.client.post('/socios/form/', {
            'nombre': xss_payload,
            'apellido': 'García',
            'telefono': '123-456-7890',
            'domicilio': 'Calle Principal 123',
            'tipo_socio': 'externo',
        })

        # Verificar que el socio fue creado pero el nombre está sanitizado
        if response.status_code == 302:  # Redirect después de success
            socio = Socio.objects.last()
            self.assertNotIn('<script>', socio.nombre)
            self.assertFalse(socio.nombre.startswith('<script>'))

    def test_socio_domicilio_xss_protection(self):
        """El campo domicilio debe estar protegido contra XSS"""
        xss_payload = 'Calle Principal 123<img src=x onerror="alert(1)">'

        response = self.client.post('/socios/form/', {
            'nombre': 'Pedro',
            'apellido': 'García',
            'telefono': '123-456-7890',
            'domicilio': xss_payload,
            'tipo_socio': 'externo',
        })

        if response.status_code == 302:
            socio = Socio.objects.last()
            self.assertNotIn('onerror', socio.domicilio)
            self.assertNotIn('<img', socio.domicilio)


class SearchQueryXSSTest(TestCase):
    """Pruebas XSS en búsqueda"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='test123', is_staff=True)
        self.client.login(username='admin', password='test123')

        # Crear algunos socios para búsqueda
        for i in range(3):
            Socio.objects.create(
                id_socio=f'S{i:03d}',
                nombre=f'Socio{i}',
                apellido='Test',
                telefono='123456',
                domicilio='Dir Test',
                estado='activo'
            )

    def test_search_query_xss_protection(self):
        """Búsqueda debe sanitizar query parameters"""
        xss_query = '<script>alert("XSS")</script>'

        response = self.client.get('/socios/', {'q': xss_query})

        # La respuesta debe estar segura (no ejecutar JavaScript)
        self.assertNotIn('<script>alert', response.content.decode())

    def test_search_query_normal_search(self):
        """Búsqueda normal debe funcionar"""
        response = self.client.get('/socios/', {'q': 'Socio'})

        # Debe encontrar resultados
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # Verificar que hay contenido de socios
        self.assertIn('Socio', content)


class DjangoTemplateEscapingTest(TestCase):
    """Pruebas de escapado automático en templates"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='test123', is_staff=True)
        self.client.login(username='admin', password='test123')

        # Crear socio con nombre potencialmente malicioso
        self.socio = Socio.objects.create(
            id_socio='S001',
            nombre='<img src=x onerror="alert(1)">',
            apellido='Test',
            telefono='123456',
            domicilio='Dir',
            estado='activo'
        )

    def test_socio_nombre_escaped_in_template(self):
        """Nombres en templates deben estar escapados"""
        response = self.client.get('/socios/')

        content = response.content.decode()

        # No debe contener la imagen potencialmente maliciosa sin escapar
        self.assertNotIn('<img src=x onerror', content)

        # Debe contener el nombre escapado
        self.assertIn('&lt;img', content)


if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner

    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['gimnasio.tests_security'])
