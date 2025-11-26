from django.utils.html import escape
from django.utils.text import slugify
import re
import bleach


def sanitize_text_input(text):
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
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone):
    # Permite: números, espacios, guiones, paréntesis, + al inicio
    pattern = r'^\+?[\d\s\-\(\)]{8,20}$'
    return bool(re.match(pattern, phone))


def validate_socio_id(socio_id):
    # Acepta: letra seguida de 1-3 dígitos
    pattern = r'^[A-Z]{1,3}\d{1,4}$'
    return bool(re.match(pattern, socio_id.strip().upper()))


def sanitize_search_query(query, max_length=100):
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
    filename = filename.replace('../', '').replace('..\\', '')
    
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    safe_name = slugify(name)
    
    if ext:
        # Solo permitir extensiones de archivo seguuras
        allowed_extensions = ['pdf', 'txt', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'jpg', 'jpeg', 'png', 'gif']
        if ext.lower() in allowed_extensions:
            return f"{safe_name}.{ext.lower()}"
    
    return safe_name


def escape_javascript_string(text):
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
    safe_context = {}
    
    for key, value in data_dict.items():
        if isinstance(value, str):
            safe_context[key] = sanitize_text_input(value)
        else:
            safe_context[key] = value
    
    return safe_context
