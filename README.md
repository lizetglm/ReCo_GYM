# ReCo_Gym - Plataforma de Gestión de Gimnasios

Sistema web integral desarrollado en Django para la administración eficiente de gimnasios, control de socios, membresías y puntos de venta.

## Despliegue en Producción
La aplicación se encuentra desplegada y operativa en Render:
**URL Pública:** [https://reco-gym-8tdz.onrender.com](https://reco-gym-8tdz.onrender.com)

## Características Principales
* **Gestión de Socios:** Registro de usuarios internos (suscripción) y externos (pago por clase).
* **Membresías:** Control de vencimientos y renovación de suscripciones.
* **Clases:** Programación de actividades y asignación de instructores.
* **Punto de Venta (Caja):** Venta de productos y cobro de mensualidades con generación de tickets.
* **Seguridad:** Protección contra ataques CSRF, XSS e Inyección SQL. Autenticación robusta.

## Tecnologías Utilizadas
* **Backend:** Python 3.12, Django 5.
* **Base de Datos:** PostgreSQL (Producción) / MySQL (Local).
* **Servidor Web:** Gunicorn (Linux) + WhiteNoise (Archivos estáticos).
* **Infraestructura:** Render Cloud.
* **CI/CD:** GitHub Actions para pruebas automáticas y Render para despliegue continuo.

## Instalación Local
1. **Clonar el repositorio:**
git clone [https://github.com/tu-usuario/ReCo_Gym.git](https://github.com/tu-usuario/ReCo_Gym.git)
cd ReCo_Gym

2. **Crear entorno virtual e instalar dependencias:**
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    pip install -r requirements.txt

3. **Configurar base de datos y migraciones:**
    python manage.py migrate

4. **Ejecutar servidor de desarrollo:**
    python manage.py runserver

## Credenciales de Prueba (Demo)
Admin: 
    user:recogym 
    passworw: recogym

Desarrollado para la materia de Desarrollo Web - 2025.