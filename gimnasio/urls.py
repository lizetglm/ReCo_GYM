from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.login_usuario, name='login_usuario'),
    path('dashboard/', views.dashboard, name='dashboard'), 
    path('logout/', views.logout_usuario, name='logout_usuario'),
    
    # Rutas de Socios (CRUD existente)
    path('socios/', views.socios_list, name='socios_list'),
    path('socio-form/', views.socio_form, name='socio_form'),
    path('socio-form/<int:pk>/', views.socio_form, name='socio_form'),
    path('socio-delete/<int:pk>/', views.eliminar_socio, name='eliminar_socio'),
    
    # Rutas de Clases (CRUD)
    path('clases/', views.lista_clases, name='lista_clases'), 
    path('clase-form/', views.clase_form, name='clase_form'), 
    path('clase-form/<int:pk>/', views.clase_form, name='clase_form'), 
    path('clase-delete/<int:pk>/', views.eliminar_clase, name='eliminar_clase'), 
    path('clase/inscripcion/<int:pk>/', views.inscripcion_clase_detalle, name='inscripcion_clase_detalle'), 
    path('clases/<int:clase_pk>/eliminar-inscripcion/<int:socio_pk>/', views.eliminar_inscripcion_clase, name='eliminar_inscripcion_clase'),

    # URLs para Instructores (Nombres de URL corregidos)
    path('instructores/', views.instructores_list, name='instructores_list'),
    path('instructor/agregar/', views.instructor_form, name='instructor_form'),
    path('instructor/editar/<int:pk>/', views.instructor_form, name='instructor_form'),
    path('instructor/eliminar/<int:pk>/', views.eliminar_instructor, name='eliminar_instructor'),
    
    # Rutas de Inscripción (Existente)
    path('inscribir/<int:socio_id>/<int:clase_id>/', views.inscribir_a_clase, name='inscribir_a_clase'),

    # Rutas de Autenticación (Existente)
    path('login/', views.login_usuario, name='login_usuario'),
    path('logout/', views.logout_usuario, name='logout_usuario'),

    #Rutas de Caja
    path('caja/', views.CajaView.as_view(), name='caja'),
    
    # Ventas de productos
    path('pagos/productos/', views.pago_productos, name='pago_productos'),
    path('pagos/productos/ticket/<int:venta_id>/', views.ticket_venta_pdf, name='ticket_venta_pdf'),
    
    # API (Existente)
    path('api/', include('gimnasio.api_urls')), 

    # Ruta de Socios ---------------------
    path('perfil/', views.perfil_socio, name='perfil_socio'),
    path('api/productos-por-categoria/<str:tipo>/', views.productos_por_categoria_api, name='productos_por_categoria_api'),
    path('socio-delete/<int:pk>/', views.eliminar_socio, name='eliminar_socio'),
    path('socio/reset-pass/<int:pk>/', views.reset_password_socio, name='reset_password_socio'),
    path('socio/perfil/<int:pk>/', views.perfil_socio, name='perfil_socio'), # <-- ¡Añade esta línea!
    path('perfil/clases/', views.perfil_lista_clases, name='perfil_lista_clases'),
    path('perfil/instructores/', views.perfil_instructores_list, name='perfil_instructores_list'),
    
    # NUEVA RUTA PARA WHATSAPP API
    path('api/enviar-whatsapp/', views.enviar_whatsapp_api, name='enviar_whatsapp_api')
]