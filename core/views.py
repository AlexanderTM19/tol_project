# core/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from faker import Faker
import random


def es_admin(user):
    return user.is_superuser

def index(request):
    return render(request, 'core/index.html')

def reservas(request):
    return render(request, 'core/reservas.html')

def tarifas(request):
    return render(request, 'core/tarifas.html')

def contacto(request):
    return render(request, 'core/contacto.html')

def clientes(request):
    fake = Faker('es_ES')
    lista_clientes = []
    
    for _ in range(100):
        cliente = {
            'rut': fake.unique.random_number(digits=8, fix_len=True),
            'nombre': fake.name(),
            'telefono': fake.phone_number(),
            'correo': fake.email(),
            'recurrente': random.choice([True, False]),
        }
        rut = str(cliente['rut'])
        rut_formateado = f"{rut[:-7]}.{rut[-7:-4]}.{rut[-4:-1]}-{rut[-1]}"
        cliente['rut'] = rut_formateado
        
        lista_clientes.append(cliente)

    context = {
        'clientes': lista_clientes
    }
    return render(request, 'core/clientesAdministrador.html', context)

def choferes(request):
    fake = Faker('es_ES')  
    lista_choferes = []
    
    for _ in range(3):
        chofer = {
            'rut': fake.unique.random_number(digits=8, fix_len=True),
            'nombre': fake.name(),
            'telefono': fake.phone_number(),
            'correo': fake.email(),
            'pais': fake.country(),
            'direccion': fake.address(),
        }
        rut = str(chofer['rut'])
        rut_formateado = f"{rut[:-7]}.{rut[-7:-4]}.{rut[-4:-1]}-{rut[-1]}"
        chofer['rut'] = rut_formateado
        
        lista_choferes.append(chofer)

    context = {
        'choferes': lista_choferes
    }
    return render(request, 'core/choferesAdministrador.html', context)

def calendario(request):
    return render(request, 'core/calendarioAdministrador.html')

@login_required
@user_passes_test(es_admin)
def admin_config(request):
    return render(request, 'core/reservasAdministrador.html')