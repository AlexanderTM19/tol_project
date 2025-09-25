from django.db import models
from django.utils import timezone

#Modelo de los clientes 
class Clientes(models.Model):
    Rut = models.CharField(primary_key=True, max_length=12, unique=True)
    Nombres = models.CharField(max_length=50)
    Apellidos = models.CharField(max_length=60)
    Telefono = models.CharField(max_length=20)
    Correo =models.EmailField(blank=True, null=True)
    Cantidad_viajes= models.IntegerField(default=0)
    

    def __str__(self):
        return self.Rut

#----------------------------------------------------------------------------------------------------------------------------------
#Modelo de los Roles de usuario
class Rol_usuario(models.Model):
    id_Rol = models.AutoField(primary_key=True)
    nombre_Rol = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_Rol
    
#----------------------------------------------------------------------------------------------------------------------------------
#Modelo de los usuarios del sistema
class Usuarios(models.Model):

    Rut = models.CharField(primary_key=True, max_length=12, unique=True)
    Nombres = models.CharField(max_length=50)
    Apellidos = models.CharField(max_length=60)
    Correo = models.EmailField(blank=False, null=False)
    ClaveUsuario= models.CharField(max_length=15)
    Rol = models.ForeignKey(Rol_usuario,on_delete=models.CASCADE, default=3)
    last_login = models.DateTimeField(blank=True, null=True) 
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    @property
    def is_authenticated(self):
        # Esta propiedad es necesaria para que Django sepa si el usuario ha iniciado sesión.
        return True

    def __str__(self):
        return self.Rut
    
#----------------------------------------------------------------------------------------------------------------------------------
#Modelo de los vehiculos
class Vehiculos(models.Model):
    id_vehiculo = models.AutoField(primary_key=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    año_modelo = models.IntegerField()
    patente = models.CharField(max_length=10, unique=True)
    color = models.CharField(max_length=30)
    revision_tecnica_vencimiento = models.DateField()
    soap_vencimiento = models.DateField()
    vencimiento_permiso_circulacion = models.DateField(default=timezone.now)
    img_revision = models.ImageField(upload_to='Vehiculos/Revisiones/', blank=True, null=True)
    img_soap = models.ImageField(upload_to='Vehiculos/Soaps/', blank=True, null=True)
    img_permiso_circulacion = models.ImageField(upload_to='Vehiculos/Permisos_circulacion/', blank=True, null=True)

    def __str__(self):
        return f'Vehiculo marca:{self.marca} modelo: {self.modelo} patente:({self.patente})'
        
#----------------------------------------------------------------------------------------------------------------------------------
# Modelo de Conductores
class Conductores(models.Model):
    usuario = models.OneToOneField(Usuarios, on_delete=models.CASCADE, primary_key=True)
    Telefono = models.CharField(max_length=20)
    img_licencia_conducir = models.ImageField(upload_to='Conductores/Licencias_conduccion/', blank=True, null=True)
    Vencimiento_licencia_conducir= models.DateField()
    ESTADOS = [
        ('DISPONIBLE', 'Disponible'),
        ('OCUPADO', 'Ocupado'),
        ('INACTIVO', 'Inactivo'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='INACTIVO')
    Direccion = models.CharField(max_length=50)
    Nacionalidad = models.CharField(max_length=20)
    Edad = models.IntegerField()
    # Contador para el número de viajes
    total_viajes_realizados = models.IntegerField(default=0)
    # Un conductor puede estar asignado a un vehículo (ForeignKey).
    vehiculo = models.ForeignKey(Vehiculos, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.usuario.Nombres} {self.usuario.Apellidos}'