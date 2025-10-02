# En tu archivo core/forms.py
from django import forms
from .models import Clientes, Rol_usuario, Usuarios, Conductores, Vehiculos, Tarifas

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
                    'placeholder': 'Debe ingresar el rut sin guion ni puntos, Ej. 123456789',
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

#-------------------------------------------------------------------------------------------------------------------------------

class CustomLoginForm(forms.Form):
    username = forms.CharField(
        label="Rut",
        max_length=9,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su Rut sin puntos ni guion, Ej: 123456789'
        })
    )
    password = forms.CharField(
        label="Contraseña",
        max_length=15,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña'
        })
    )
    # Se agrega el campo de recordar contraseña como un CheckboxInput
    recuerdame = forms.BooleanField(
        required=False, 
        label="Recordar contraseña",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
#-------------------------------------------------------------------------------------------------------------------------------

class ChoferForm(forms.ModelForm):
    class Meta:
        model = Conductores
        fields = "__all__"
        widgets = {
            'usuario': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'Telefono': forms.TextInput(
                attrs={
                    'placeholder': 'Debe ingresar teléfono',
                    'class': 'form-control',
                    'type': 'tel'
                }
            ),
            'img_licencia_conducir': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control-file'
                }
            ),
            'Vencimiento_licencia_conducir': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
            'estado': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'Direccion': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Debe ingresar dirección',
                }
            ),
            'Nacionalidad': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nacionalidad',
                }
            ),
            'Edad': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Edad',
                }
            ),
            'total_viajes_realizados': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'readonly': 'readonly' # Este campo no debe ser editable por el usuario
                }
            ),
            'vehiculo': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
        }

#-------------------------------------------------------------------------------------------------------------------------------
class VehiculosForm(forms.ModelForm):
    class Meta:
        model = Vehiculos
        fields = "__all__"
        widgets = {
            'marca': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej. Nissan'
                }
            ),
            'modelo': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej. X-Trail'
                }
            ),
            'año_modelo': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej. 2023'
                }
            ),
            'patente': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej. ABCD-12'
                }
            ),
            'color': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej. Blanco'
                }
            ),
            'revision_tecnica_vencimiento': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
            'soap_vencimiento': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
            'Vencimiento_permiso_circulacion': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
            'img_revision': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control-file'
                }
            ),
            'img_soap': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control-file'
                }
            ),
            'img_permiso_circulacion': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control-file'
                }
            ),
        }
        
#-------------------------------------------------------------------------------------------------------------------------------

class TarifasForm(forms.ModelForm):

    class Meta:
        model = Tarifas
        fields = "__all__" 
        widgets = {
            'Nombre_Comuna': forms.TextInput(
                attrs={
                    'placeholder': 'Ej: Aeropuerto Internacional, Santiago Centro',
                    'class': 'form-control',
            }),
            'Valor': forms.NumberInput(attrs={
                    'placeholder': 'Ej: 15000',
                    'class': 'form-control'
            }),
        }