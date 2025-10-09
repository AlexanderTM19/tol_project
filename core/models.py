from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator 

#Modelo de los clientes 
class Clientes(models.Model):
    Rut = models.CharField(primary_key=True, max_length=12, unique=True)
    Nombres = models.CharField(max_length=50)
    Apellidos = models.CharField(max_length=60)
    Telefono = models.CharField(max_length=20)
    Correo = models.EmailField(blank=True, null=True)
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
class Trasporte(models.Model):
    id_trasporte = models.AutoField(primary_key=True)
    Tipos_trasportes = [
        ('SEDAN','sedan'),
        ('VAN', 'van'),
        ('SUV', 'suv'),
        ('LUXURY', 'luxury'),
    ]
    tipo_transporte = models.CharField(max_length=10, choices=Tipos_trasportes, default='SEDAN')
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    año_modelo = models.IntegerField()
    patente = models.CharField(max_length=10, unique=True)
    color = models.CharField(max_length=30)
    revision_tecnica_vencimiento = models.DateField()
    soap_vencimiento = models.DateField()
    vencimiento_permiso_circulacion = models.DateField()
    img_revision = models.ImageField(upload_to='Vehiculos/Revisiones/', blank=True, null=True)
    img_soap = models.ImageField(upload_to='Vehiculos/Soaps/', blank=True, null=True)
    img_permiso_circulacion = models.ImageField(upload_to='Vehiculos/Permisos_circulacion/', blank=True, null=True)

    def __str__(self):
        return f'Trasporte tipo:{self.tipo_transporte} marca:{self.marca} modelo: {self.modelo} patente:({self.patente})'
        
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
    vencimiento_permiso_circulacion = models.DateField()
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
    Nro_ficha = Nro_ficha = models.IntegerField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(1)] # Asegura que sea >= 1
    )
    img_foto_perfil = models.ImageField(upload_to='Conductores/Foto_perfil/', blank=True, null=True)
    img_licencia_conducir = models.ImageField(upload_to='Conductores/Licencias_conduccion/', blank=True, null=True)
    Vencimiento_licencia_conducir= models.DateField()
    ESTADOS = [
        ('DISPONIBLE', 'Disponible'),
        ('OCUPADO', 'Ocupado'),
        ('INACTIVO', 'Inactivo'),
        ('SUSPENDIDO', 'suspendido'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='INACTIVO')
    Direccion = models.CharField(max_length=50)
    Nacionalidad = models.CharField(max_length=20)
    Edad = models.IntegerField()
    # Contador para el número de viajes
    total_viajes_realizados = models.IntegerField(default=0)
    # Un conductor puede estar asignado a un vehículo (ForeignKey).
    vehiculo = models.ForeignKey(Trasporte, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.usuario.Nombres} {self.usuario.Apellidos}'
#----------------------------------------------------------------------------------------------------------------------------------
   
#Modelo de las tarifas
class Tarifas(models.Model):
    id_tarifa = models.AutoField(primary_key=True)
    Nombre_Comuna = models.CharField(max_length=50)
    Valor = models.IntegerField()
    
    def __str__(self):
        return self.Nombre_Comuna
    

#----------------------------------------------------------------------------------------------------------------------------------
   
#Modelo de las reservas

class Reservas(models.Model):
    Id_reserva = models.AutoField(primary_key=True, null=False)
    Nombre_Cliente = models.CharField(max_length=50, null=False)
    Apellidos_Cliente = models.CharField(max_length=50, null=False)
    Telefono = models.CharField(max_length=20, null=False)
    Correo = models.EmailField(blank=True, null=True)
    Origen = models.ForeignKey(Tarifas, on_delete=models.SET_NULL, null=True, blank=True,related_name='reservas_como_origen')
    Destino = models.ForeignKey(Tarifas, on_delete=models.SET_NULL, null=True, blank=True,related_name='reservas_como_destino')
    Dirrecion = models.CharField(max_length=50, null=False)
    Fecha = models.DateField()
    Hora = models.TimeField()
    Cantidad_pasajeros = models.IntegerField(validators=[
                MinValueValidator(0), # Mínimo permitido (por ejemplo, 0)
                MaxValueValidator(4)  # Máximo permitido (si solo quieres un dígito)
        ])
    Cantidad_maletas = models.IntegerField(
        validators=[
                MinValueValidator(0), # Mínimo permitido (por ejemplo, 0)
                MaxValueValidator(2)  # Máximo permitido (si solo quieres un dígito)
        ])
    Confirmacion = models.BooleanField(default=False)
    ESTADOS = [
        ('REALIZADO', 'realizado'),
        ('CANCELADO', 'ocupado'),
        ('PENDIENTE', 'pendiente'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')
    Chofer_asignado = models.ForeignKey(Conductores, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.Id_reserva




class ReservasWeb(models.Model):
    Id_reserva = models.AutoField(primary_key=True, null=False)
    Nombre_Cliente = models.CharField(max_length=50, null=False)
    Apellidos_Cliente = models.CharField(max_length=50, blank=True, default="")
    Telefono = models.CharField(max_length=20, null=False)
    Correo = models.EmailField(blank=True, null=True)
    Origen = models.ForeignKey(
        Tarifas,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservas_web_origen'
    )
    Destino = models.ForeignKey(
        Tarifas,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservas_web_destino'
    )
    Dirrecion = models.CharField(max_length=100, blank=True, default="")
    Fecha = models.DateField()
    Hora = models.TimeField()
    Cantidad_pasajeros = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(4)
        ]
    )
    Cantidad_maletas = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(3)
        ]
    )
    Vehiculo_solicitado = models.CharField(max_length=30, blank=True, default="")
    Comentario = models.TextField(blank=True, default="")
    Confirmacion = models.BooleanField(default=False)
    Creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reserva web de {self.Nombre_Cliente} para {self.Fecha}"

 
