# core/views.py
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from faker import Faker
from .form import usuarioform
from .models import Usuarios
import random

#Funcion de validacion de rut

def validar_rut(rut):
    """
    Valida un RUT chileno (con o sin puntos/guión)
    """
    
    rut = rut.upper().replace(".", "").replace("-", "")
    
    # Valida el formato y la longitud básica
    if not rut or not rut[:-1].isdigit():
        return False
    
    # Extrae el dígito verificador
    dv = rut[-1]
    
    # Aplica el algoritmo de Módulo 11
    factor = 2
    suma = 0
    for digito in reversed(rut[:-1]):
        suma += int(digito) * factor
        factor = factor + 1 if factor < 7 else 2
        
    dv_calculado = 11 - (suma % 11)
    
    # Compara el dígito verificador calculado con el original
    if dv_calculado == 11:
        dv_final = "0"
    elif dv_calculado == 10:
        dv_final = "K"
    else:
        dv_final = str(dv_calculado)
        
    return dv == dv_final


# ✅ Función para validar si el usuario es superusuario
def es_admin(user):
    return user.is_superuser

# Vistas públicas
def index(request):
    return render(request, 'core/index.html')

def reservas(request):
    return render(request, 'core/reservas.html')

def tarifas(request):
    return render(request, 'core/tarifas.html')

def contacto(request):
    return render(request, 'core/contacto.html')

# ✅ Vistas de administrador (requieren login + superuser)
@login_required
@user_passes_test(es_admin)
def clientes(request):
    Listado_usuarios = Usuarios.objects.all()
    return render(request, 'core/clientesAdministrador.html', {"clientes": Listado_usuarios})

"""
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
"""

@login_required
@user_passes_test(es_admin)
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

@login_required
@user_passes_test(es_admin)
def calendario(request):
    return render(request, 'core/calendarioAdministrador.html')
"""
@login_required
@user_passes_test(es_admin)
def form_clientes(request):
    form = usuarioform()
    mensaje =""
    if request.method == 'POST':
        form = usuarioform(request.POST, request.FILES)
        if form.is_valid():
            rut = request.POST.get('rut', None)
            if rut in rut.objects.values_list('rut', flat=True):
                mensaje="Este rut ya está registrado"
            else:
                form.save()
                mensaje="Datos Guardados Correctamente"
    return render(request, 'core/form_crearusuarios.html',{"form":form,"mensaje":mensaje})
"""
@login_required
@user_passes_test(es_admin)
def form_clientes(request):
    form = usuarioform()
    mensaje = ""
    if request.method == 'POST':
        form = usuarioform(request.POST)
        if form.is_valid():
            rut = form.cleaned_data.get('Rut')
            
            # ✅ Paso a paso:
            # 1. Valida el RUT usando la función
            if not validar_rut(rut):
                mensaje = "El RUT ingresado no es válido."
            # 2. Si el RUT es válido, comprueba si ya existe
            elif Usuarios.objects.filter(Rut=rut).exists():
                mensaje = "Este RUT ya está registrado."
            # 3. Si todo es correcto, guarda el formulario
            else:
                form.save()
                mensaje = "Datos Guardados Correctamente."
    
    return render(request, 'core/form_crearusuarios.html', {"form": form, "mensaje": mensaje})

def form_modpro(request, id):
    Usuario = Usuarios.objects.get(Rut=id)
    mensaje=""
    if request.method == 'POST':
        form = usuarioform(request.POST, request.FILES, instance=Usuario)
        if form.is_valid():
            form.save()
            mensaje = "Datos Modificado Correctamente"
            return redirect(to="clientes")
    else:
        return render(request, "core/form_modusuario.html", {"form":usuarioform(instance=Usuario), "mensaje":mensaje})

@login_required
@user_passes_test(es_admin)
def admin_config(request):
    return render(request, 'core/reservasAdministrador.html')
