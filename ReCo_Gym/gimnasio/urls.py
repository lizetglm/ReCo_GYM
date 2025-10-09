from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('clases/', views.lista_clases, name='lista_clases'),
    path('login/', views.login_usuario, name='login_usuario'),
    path('logout/', views.logout_usuario, name='logout_usuario'),
]