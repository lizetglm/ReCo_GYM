from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('clases/', views.lista_clases, name='lista_clases'),
    path('login/', views.login_usuario, name='login_usuario'),
    path('registro/', views.registro_usuario, name='registro_usuario'),
]