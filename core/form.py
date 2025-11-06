# En tu archivo core/forms.py
from django import forms
from .models import Clientes, Rol_usuario, Usuarios, Conductores, Vehiculos, Trasporte, Tarifas, Reservas, ReservasWeb
from django.core.validators import MinValueValidator, MaxValueValidator 


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
    # Asegurar estilo consistente en Cantidad_viajes si está presente en el modelo
    Cantidad_viajes = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

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
        # Excluimos last_login para no sobrescribirlo desde el formulario
        fields = ['Rut','Nombres','Apellidos','Correo','ClaveUsuario','Rol','is_active','is_staff','is_superuser'] 
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
                    'class': 'form-select'
                }
            ),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
            'Nro_ficha': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nro de ficha',
                }
            ),
            'img_foto_perfil': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control-file'
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
        exclude = ('id_vehiculo',) # Excluye el campo id_vehiculo
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
            'vencimiento_permiso_circulacion': forms.DateInput(
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
class TrasporteForm(forms.ModelForm):
    class Meta:
        model = Trasporte 
        fields = "__all__"
        widgets = {
            'tipo_transporte': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
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
            'vencimiento_permiso_circulacion': forms.DateInput(
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

#-------------------------------------------------------------------------------------------------------------------------------

class ReservasForm(forms.ModelForm):
    class Meta:
        model = Reservas
        # Excluimos 'estado' para usar el valor por defecto desde la vista
        fields = [
            'Nombre_Cliente', 'Apellidos_Cliente', 'Telefono', 'Correo','nro_vuelo',
            'Origen', 'Destino','Monto_tarifa', 'Dirrecion', 'Fecha', 'Hora',
            'Cantidad_pasajeros', 'Cantidad_maletas', 'Confirmacion',
            'Chofer_asignado'
        ]
        widgets = {
            'Nombre_Cliente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
            'Apellidos_Cliente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tus apellidos'}),
            'Telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 912345678'}),
            'Correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'opcional@ejemplo.com'}),
            'nro_vuelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu numero de vuelo (Ej: AB1234)'}),
            
            # Para los campos ForeignKey, se usa Select o SelectMultiple.
            # Puedes usar empty_label para que el usuario sepa que debe seleccionar
            'Origen': forms.Select(attrs={'class': 'form-select'}),
            'Destino': forms.Select(attrs={'class': 'form-select'}),
            'Dirrecion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Av. siempreviva 123'}),

            # Usamos widgets de HTML5 para mejor UI/UX en navegadores
            'Fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Hora': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),

            # Para campos numéricos, TextInput o NumberInput. 
            # El validador del modelo se encargará de limitar el rango.
            'Monto_tarifa': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 9999999}),
            'Cantidad_pasajeros': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 4}),
            'Cantidad_maletas': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 2}),
            'Chofer_asignado': forms.Select(attrs={'class': 'form-select'}),
            'Confirmacion': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    # Si quisieras asegurarte de que la Comuna de Origen NO sea igual a la Comuna de Destino
    def clean(self):
        cleaned_data = super().clean()
        origen = cleaned_data.get("Origen")
        destino = cleaned_data.get("Destino")

        if origen and destino and origen == destino:
            raise forms.ValidationError(
                "El Origen y el Destino no pueden ser la misma Comuna."
            )
        return cleaned_data


class ReservasWebForm(forms.ModelForm):
    class Meta:
        model = ReservasWeb
        fields = [
            'Nombre_Cliente',
            'Apellidos_Cliente',
            'Telefono',
            'Correo',
            'nro_vuelo',
            'Origen',
            'Destino',
            'Dirrecion',
            'Fecha',
            'Hora',
            'Cantidad_pasajeros',
            'Cantidad_maletas',
            'Vehiculo_solicitado',
            'Comentario',
        ]
        widgets = {
            'Nombre_Cliente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'Apellidos_Cliente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'Telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 912345678'}),
            'Correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'usuario@ejemplo.com'}),
            'nro_vuelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu numero de vuelo (Ej: AB1234)'}),
            'Origen': forms.Select(attrs={'class': 'form-select'}),
            'Destino': forms.Select(attrs={'class': 'form-select'}),
            'Dirrecion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección completa'}),
            'Fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Hora': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'Cantidad_pasajeros': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 4}),
            'Cantidad_maletas': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 3}),
            'Vehiculo_solicitado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipo de vehículo'}),
            'Comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Comentario opcional'}),
        }
