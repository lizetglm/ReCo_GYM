from django.db import models

# Create your models here.
class Socios(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    edad = models.IntegerField()
    GENDER_CHOICES = [("M","Masculino"),("F","Femenino"),("O","Otro")]
    genero = models.CharField(max_length=20, choices=GENDER_CHOICES)
    email = models.EmailField()
    telefono = models.CharField(max_length=30, blank=True, null=True)
    direccion = models.CharField(max_length=255)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    gerente = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=False, blank=False, 
        on_delete=models.SET_NULL
    )
    