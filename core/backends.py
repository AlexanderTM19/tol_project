# core/backends.py
from django.contrib.auth.backends import BaseBackend
from .models import Usuarios

class RutAuthenticationBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            usuario = Usuarios.objects.get(Rut=username)
            if usuario.ClaveUsuario == password:
                # Configura campos de is_superuser y is_staff en el objeto del usuario para verificar que accede cada uno
                if usuario.Rol.nombre_Rol == 'Administrador' or usuario.Rol.nombre_Rol == 'Secretaria':
                    usuario.is_superuser = True
                    usuario.is_staff = True
                else:
                    usuario.is_superuser = False
                    usuario.is_staff = False
                    
                usuario.save()
                return usuario
        except Usuarios.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return Usuarios.objects.get(pk=user_id)
        except Usuarios.DoesNotExist:
            return None