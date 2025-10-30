from twilio.rest import Client
from django.conf import settings
import re

def send_whatsapp_message(recipient_number, username, password, nombre, apellido):
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        return False, "Configuración de Twilio no disponible."

    if not recipient_number:
        return False, "Número de teléfono vacío."
    
    recipient_number = str(recipient_number).strip()
    if re.match(r'^\d{10,11}$', recipient_number):
        if recipient_number.startswith('0'):
            recipient_number = recipient_number[1:]
        if not recipient_number.startswith('521'):
            recipient_number = '521' + recipient_number
        recipient_number = '+' + recipient_number
    elif not recipient_number.startswith('+'):
        return False,
    
    to_number = f"whatsapp:{recipient_number}"

    body = (
        f"🎉 CUENTA CREADA - ANOTAR CREDENCIALES\n"
        f"¡Bienvenido(a), {nombre} {apellido}, a ReCo_GYM!\n\n"
        f"Tus credenciales de acceso son:\n"
        f"Usuario: {username}\n"
        f"Contraseña: {password}\n\n"
        f"¡Empieza a entrenar ya! 💪"
    )

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            from_='whatsapp:' + settings.TWILIO_WHATSAPP_NUMBER.lstrip('+'),
            body=body,
            to=to_number
        )
        print(f"Mensaje de WhatsApp enviado con SID: {message.sid}")
        return True, None
    except Exception as e:
        error_msg = f"Error al enviar mensaje de WhatsApp: {e}"
        print(error_msg)
        return False, error_msg