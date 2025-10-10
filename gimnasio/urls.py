from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.login_usuario, name='login_usuario'),
    path('dashboard/', views.dashboard, name='dashboard'), 
    path('clases/', views.lista_clases, name='lista_clases'),
    path('login/', views.login_usuario, name='login_usuario'),
    path('logout/', views.logout_usuario, name='logout_usuario'),
    path('socios/', views.socios_list, name='socios_list'),
    path('socio-form/', views.socio_form, name='socio_form'),
    path('socio-form/<int:pk>/', views.socio_form, name='socio_form'),
    path('socio-delete/<int:pk>/', views.eliminar_socio, name='eliminar_socio'),
    path('api/', include('gimnasio.api_urls')), 
]