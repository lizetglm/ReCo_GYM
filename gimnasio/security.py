"""
Módulo de seguridad para protección contra ataques XSS y inyección de código.
Proporciona funciones de sanitización, validación y escapado de datos.
"""

from django.utils.html import escape
from django.utils.text import slugify
import re
import bleach


def sanitize_text_input(text):
    """
    Sanitiza texto de entrada para prevenir XSS.
    Remueve caracteres peligrosos y espacios en blanco excesivos.
    
    Args:
        text (str): Texto a sanitizar
        
    Returns:
        str: Texto sanitizado
    """
    if not isinstance(text, str):
        return ""
    
    # Strip whitespace
    text = text.strip()
    
    # Limitar longitud
    text = text[:1000]
    
    # Usar Django's escape para HTML
    text = escape(text)
    
    return text


def sanitize_html(html_content, allowed_tags=None):
    """
    Sanitiza HTML removiendo etiquetas potencialmente peligrosas.
    Solo mantiene etiquetas seguras.
    
    Args:
        html_content (str): HTML a sanitizar
        allowed_tags (list): Tags permitidos (default: ['p', 'br', 'strong', 'em', 'u', 'a'])
        
    Returns:
        str: HTML sanitizado
    """
    if not html_content:
        return ""
    
    if allowed_tags is None:
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a']
    
    allowed_attributes = {'a': ['href', 'title']}
    
    # Usar bleach para remover tags peligrosas
    cleaned = bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )
    
    return cleaned


def validate_email(email):
    """
    Valida formato de email.
    
    Args:
        email (str): Email a validar
        
    Returns:
        bool: True si es válido, False en caso contrario
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone):
    """
    Valida formato de teléfono (solo números y caracteres permitidos).
    
    Args:
        phone (str): Teléfono a validar
        
    Returns:
        bool: True si es válido, False en caso contrario
    """
    # Permite: números, espacios, guiones, paréntesis, + al inicio
    pattern = r'^\+?[\d\s\-\(\)]{8,20}$'
    return bool(re.match(pattern, phone))


def validate_socio_id(socio_id):
    """
    Valida formato de ID de socio (ej: S001).
    
    Args:
        socio_id (str): ID de socio a validar
        
    Returns:
        bool: True si es válido, False en caso contrario
    """
    # Acepta: letra seguida de 1-3 dígitos
    pattern = r'^[A-Z]{1,3}\d{1,4}$'
    return bool(re.match(pattern, socio_id.strip().upper()))


def sanitize_search_query(query, max_length=100):
    """
    Sanitiza queries de búsqueda para prevenir inyección SQL/XSS.
    
    Args:
        query (str): Query de búsqueda
        max_length (int): Longitud máxima permitida
        
    Returns:
        str: Query sanitizada
    """
    if not query:
        return ""
    
    # Strip whitespace
    query = query.strip()
    
    # Limitar longitud
    query = query[:max_length]
    
    # Remover caracteres potencialmente peligrosos
    # Mantener: letras, números, espacios, guiones, acentos
    query = re.sub(r'[^\w\s\-áéíóúñ]', '', query, flags=re.UNICODE)
    
    # Remover múltiples espacios
    query = re.sub(r'\s+', ' ', query)
    
    # Escapar para HTML
    query = escape(query)
    
    return query


def sanitize_filename(filename):
    """
    Sanitiza nombres de archivo para prevenir path traversal y otros ataques.
    
    Args:
        filename (str): Nombre de archivo
        
    Returns:
        str: Nombre de archivo sanitizado
    """
    # Remover path traversal
    filename = filename.replace('../', '').replace('..\\', '')
    
    # Usar Django's slugify para nombres seguros
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    safe_name = slugify(name)
    
    if ext:
        # Solo permitir extensiones de archivo seguuras
        allowed_extensions = ['pdf', 'txt', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'jpg', 'jpeg', 'png', 'gif']
        if ext.lower() in allowed_extensions:
            return f"{safe_name}.{ext.lower()}"
    
    return safe_name


def escape_javascript_string(text):
    """
    Escapa texto para usar de forma segura dentro de JavaScript.
    
    Args:
        text (str): Texto a escapar
        
    Returns:
        str: Texto escapado para JavaScript
    """
    if not isinstance(text, str):
        return ""
    
    text = escape(text)
    # Escapar caracteres especiales de JavaScript
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    text = text.replace("'", "\\'")
    text = text.replace('\n', '\\n')
    text = text.replace('\r', '\\r')
    
    return text


def validate_url(url, allowed_schemes=None):
    """
    Valida URLs para prevenir ataques javascript: y data: URLs.
    
    Args:
        url (str): URL a validar
        allowed_schemes (list): Esquemas permitidos (default: ['http', 'https'])
        
    Returns:
        bool: True si es válida y segura, False en caso contrario
    """
    if not url:
        return False
    
    if allowed_schemes is None:
        allowed_schemes = ['http', 'https']
    
    # URLs relativas son permitidas (comienzan con /)
    if url.startswith('/'):
        return True
    
    # Verificar esquema
    if '://' not in url:
        return False
    
    scheme = url.split('://')[0].lower()
    
    # Bloquear esquemas peligrosos
    dangerous_schemes = ['javascript', 'data', 'vbscript', 'about']
    if scheme in dangerous_schemes:
        return False
    
    # Permitir solo esquemas seguros
    if scheme not in allowed_schemes:
        return False
    
    return True


def create_safe_context(data_dict):
    """
    Prepara un diccionario de contexto asegurando que los valores estén sanitizados.
    
    Args:
        data_dict (dict): Diccionario de datos
        
    Returns:
        dict: Diccionario con valores sanitizados
    """
    safe_context = {}
    
    for key, value in data_dict.items():
        if isinstance(value, str):
            safe_context[key] = sanitize_text_input(value)
        else:
            safe_context[key] = value
    
    return safe_context
