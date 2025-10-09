from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('clases/', views.lista_clases, name='lista_clases'),
]