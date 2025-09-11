# En tu archivo core/forms.py
from django import forms
from .models import Clientes, Rol_usuario, Usuarios

#-------------------------------------------------------------------------------------------------------------------------------
class ClientesForm(forms.ModelForm):
    class Meta:
        model = Clientes
        fields = "__all__"
        widgets = {
            'Nombres': forms.TextInput(
                attrs={
                    'placeholder': 'Debe ingresar sus nombres',
                    'class': 'form-control'
                }
            ),
            'Apellidos': forms.TextInput(
                attrs={
                    'placeholder': 'Debe ingresar sus apellidos',
                    'class': 'form-control'
                }
            ),
            'Rut': forms.TextInput(
                attrs={
                    # No uses type='number' para el RUT
                    'placeholder': 'Ej: 12345678-9', 
                    'class': 'form-control'
                }
            ),
            'Telefono': forms.TextInput(
                attrs={
                    'placeholder': 'Debe ingresar teléfono',
                    'class': 'form-control',
                    'type': 'tel' # Usa 'tel' para teléfonos
                }
            ),
            'Correo': forms.EmailInput( # Usa EmailInput para correos
                attrs={
                    'placeholder': 'Debe ingresar su correo',
                    'class': 'form-control'
                }
            ),
            # El campo 'Cantidad_viajes' no necesita un widget si es solo de lectura
            # El campo 'Recurrente' ya está bien
            'Recurrente': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            )
        }

#-------------------------------------------------------------------------------------------------------------------------------
class Rol_Form(forms.ModelForm):
    class Meta:
        model = Rol_usuario
        # Incluye solo los campos que quieres que el usuario edite
        fields = ['nombre_Rol'] 
        
        # Opcional: añade widgets para mejorar la apariencia y experiencia
        widgets = {
            'nombre_Rol': forms.TextInput(
                attrs={
                    'placeholder': 'Ej. Administrador, Cliente, Chofer',
                    'class': 'form-control'
                }
            )
        }

#-------------------------------------------------------------------------------------------------------------------------------


class UsuariosForm(forms.ModelForm):
    class Meta:
        model = Usuarios
        fields = "__all__" 
        widgets = {
            'Rut': forms.TextInput(
                attrs={
                    'placeholder': 'Ej. 12.345.678-9',
                    'class': 'form-control'
                }
            ),
            'Nombres': forms.TextInput(
                attrs={
                    'placeholder': 'Debe ingresar sus nombres',
                    'class': 'form-control'
                }
            ),
            'Apellidos': forms.TextInput(
                attrs={
                    'placeholder': 'Debe ingresar sus apellidos',
                    'class': 'form-control'
                }
            ),
            'Correo': forms.EmailInput(
                attrs={
                    'placeholder': 'usuario@ejemplo.com',
                    'class': 'form-control'
                }
            ),
            'ClaveUsuario': forms.PasswordInput(
                attrs={
                    'placeholder': 'Ingrese una clave',
                    'class': 'form-control'
                }
            ),
            'Rol': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
        }