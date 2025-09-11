from django.db import models

# Create your models here.
class Usuarios(models.Model):
    Rut = models.CharField(primary_key=True, max_length=12, unique=True)
    Nombres = models.CharField(max_length=50)
    Apellidos = models.CharField(max_length=60)
    Telefono = models.CharField(max_length=20)
    Correo =models.CharField(max_length=50)
    ClaveUsuario= models.CharField(max_length=15)
    Cantidad_viajes= models.IntegerField(default=0)
    Recurrente= models.BooleanField(default=False)

    def __str__(self):
        return self.Rut
    

