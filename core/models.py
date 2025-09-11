from django.db import models

# Create your models here.
class Clientes(models.Model):
    Rut = models.CharField(primary_key=True, max_length=12, unique=True)
    Nombres = models.CharField(max_length=50)
    Apellidos = models.CharField(max_length=60)
    Telefono = models.CharField(max_length=20)
    Correo =models.EmailField(blank=True, null=True)
    Cantidad_viajes= models.IntegerField(default=0)
    Recurrente= models.BooleanField(default=False)

    def __str__(self):
        return self.Rut
    
class Rol_usuario(models.Model):
    id_Rol = models.AutoField(primary_key=True)
    nombre_Rol = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_Rol
    

class Usuarios(models.Model):

    Rut = models.CharField(primary_key=True, max_length=12, unique=True)
    Nombres = models.CharField(max_length=50)
    Apellidos = models.CharField(max_length=60)
    Correo = models.EmailField(blank=False, null=False)
    ClaveUsuario= models.CharField(max_length=15)
    Rol = models.ForeignKey(Rol_usuario,on_delete=models.CASCADE, default=3)
    
    def __str__(self):
        return self.Rut
    


