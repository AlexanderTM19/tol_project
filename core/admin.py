from django.contrib import admin
from .models import Usuarios, Clientes, Rol_usuario
# Register your models here.


admin.site.register(Usuarios)
admin.site.register(Clientes)
admin.site.register(Rol_usuario)