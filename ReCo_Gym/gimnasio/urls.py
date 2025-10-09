from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('clases/', views.lista_clases, name='lista_clases'),
<<<<<<< HEAD
    path('login/', views.login_usuario, name='login_usuario'),
    path('logout/', views.logout_usuario, name='logout_usuario'),
=======
    path('api/', include('gimnasio.api_urls')),
>>>>>>> 1d4a44e (Avance API)
]