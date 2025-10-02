from django.contrib import admin
from .models import Usuarios, Clientes, Rol_usuario, ReservasWeb
# Register your models here.


admin.site.register(Usuarios)
admin.site.register(Clientes)
admin.site.register(Rol_usuario)
admin.site.register(ReservasWeb)
