from django import forms
from django.forms import ModelForm
from .models import Usuarios

class usuarioform(ModelForm):
    class Meta:
        model= Usuarios
        fields="__all__"
        widgets={
            'Nombres':forms.TextInput(
                attrs={
                    'placeholder':'Debe ingresar sus nombres',
                    'class':'form-control'
                }
            ),
            'Apellidos':forms.TextInput(
                attrs={
                    'placeholder':'Debe ingresar sus apellidos',
                    'class':'form-control'
                }
            ),
            'Rut':forms.TextInput(
                    attrs={
                        'placeholder':'Debe ingresar Rut',
                        'class':'form-control',
                        'type':'number'
                        }
            ),
            'Telefono':forms.TextInput(
                    attrs={
                        'placeholder':'Debe ingresar Telefono',
                        'class':'form-control',
                        'type':'number'
                        }
            ),
            'Correo':forms.TextInput(
                attrs={
                    'placeholder':'Debe ingresar su correo',
                    'class':'form-control'
                }
            ),
            'ClaveUsuario':forms.TextInput(
                attrs={
                    'placeholder':'Debe ingresar su nueva clave',
                    'class':'form-control'
                }
            ),
            'Recurrente': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            )
                    
        }