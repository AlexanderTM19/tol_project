# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.db.utils import IntegrityError
from django.contrib.auth.decorators import login_required, user_passes_test
from faker import Faker
from .form import ClientesForm, UsuariosForm, Rol_Form, CustomLoginForm, ChoferForm, VehiculosForm, TarifasForm, ReservasForm, ReservasWebForm
from .models import Clientes, Usuarios, Rol_usuario, Conductores, Vehiculos, Tarifas, Reservas, ReservasWeb
import random
import json
from django.http import JsonResponse
from django.utils.dateformat import DateFormat 
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone

# ❌ FUNCIÓN events_json ELIMINADA para revertir la funcionalidad AJAX del calendario.
# def events_json(request):
#     # ... código eliminado ...
#     pass


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
    tarifas_lista = Tarifas.objects.all()
    formulario = ReservasWebForm()
    contexto = {
        'tarifas': tarifas_lista,
        'formulario_reserva_web': formulario,
    }
    return render(request, 'core/reservas.html', contexto)

def tarifas(request):
    tarifas_lista = Tarifas.objects.all()
    return render(request, 'core/tarifas.html', {"Tarifas": tarifas_lista})

def contacto(request):
    return render(request, 'core/contacto.html')

# Vista personalizada de login con redirección por perfil
def login_view(request):
    error = None
    # ✅ Usar el formulario personalizado para GET y POST
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Autentica al usuario usando tu backend personalizado
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Si las credenciales son válidas, loguea al usuario
                auth_login(request, user)
                
                try:
                    # ✅ Usa el objeto de usuario autenticado para obtener el Rol
                    # El 'user' devuelto por authenticate es tu objeto Usuarios
                    if user.Rol.nombre_Rol == 'Administrador' or user.Rol.nombre_Rol == 'Secretaria':
                        return redirect('admin_config')
                    elif user.Rol.nombre_Rol == 'Chofer':
                        return redirect('ficha_conductor')
                    else:
                        return redirect('inicio')
                        
                        
                except AttributeError:
                    # En caso de que el usuario no tenga un campo 'Rol' definido
                    return redirect('inicio')
            else:
                error = "Usuario o contraseña incorrectos"
        else:
            error = "Usuario o contraseña incorrectos"
    else:
        # ✅ Para peticiones GET, inicializa el formulario vacío
        form = CustomLoginForm()

    return render(request, 'core/login.html', {'form': form, 'error': error })

# Vista para ficha del conductor
from django.contrib.auth.decorators import login_required
@login_required
def ficha_conductor(request):
    try:
        conductor = Conductores.objects.select_related('usuario', 'vehiculo').get(usuario=request.user)
    except Conductores.DoesNotExist:
        conductor = None

    conductores = [44, 34, 29, 24, 33, 36, 25, 16, 31, 10, 27, 2, 7, 43, 21, 1, 37, 4, 12, 18, 15, 32, 5, 3, 13, 41]
    suspendidos = [26, 22, 6, 11]
    all_fichas = conductores + suspendidos
    all_fichas = sorted(set(all_fichas))
    fake = Faker('es_ES')
    grilla_conductores = []
    random.seed(42)
    for ficha in all_fichas:
        nombre = fake.first_name()
        apellido = fake.last_name()
        servicios = random.randint(1, 200)
        activo = ficha not in suspendidos
        grilla_conductores.append({
            "numero": ficha,
            "nombre": nombre,
            "apellido": apellido,
            "servicios": servicios,
            "activo": activo
        })
    total_filas = len(grilla_conductores)
    return render(request, 'core/fichaConductor.html', {
        'conductores': conductores,
        'suspendidos': suspendidos,
        'grilla_conductores': grilla_conductores,
        'total_filas': total_filas,
        'conductor': conductor,
        'vehiculo': conductor.vehiculo if conductor else None,
    })


@login_required
def perfil_conductor_view(request):
    try:
        conductor = Conductores.objects.select_related('usuario', 'vehiculo').get(usuario=request.user)
    except Conductores.DoesNotExist:
        return redirect('inicio')

    contexto = {
        'conductor': conductor,
        'vehiculo': conductor.vehiculo,
    }
    return render(request, 'core/perfilConductor.html', contexto)


@login_required
def servicios_conductor(request):
    try:
        conductor = Conductores.objects.select_related('usuario').get(usuario=request.user)
    except Conductores.DoesNotExist:
        return redirect('inicio')

    reservas_asignadas = Reservas.objects.select_related('Origen', 'Destino').filter(
        Chofer_asignado=conductor
    ).order_by('Fecha', 'Hora')

    ahora = timezone.localtime()
    ahora_naive = ahora.replace(tzinfo=None)

    reservas_enriquecidas = []
    for reserva in reservas_asignadas:
        inicio = datetime.combine(reserva.Fecha, reserva.Hora)
        es_pasada = inicio < ahora_naive
        reservas_enriquecidas.append({
            'instancia': reserva,
            'inicio': inicio,
            'es_pasada': es_pasada,
            'origen': reserva.Origen.Nombre_Comuna if reserva.Origen else '',
            'destino': reserva.Destino.Nombre_Comuna if reserva.Destino else '',
        })

    futuras = [res for res in reservas_enriquecidas if not res['es_pasada']]
    historicas = [res for res in reservas_enriquecidas if res['es_pasada']]

    contexto = {
        'conductor': conductor,
        'reservas_futuras': futuras,
        'reservas_historicas': historicas,
        'total_reservas': len(reservas_enriquecidas),
    }

    return render(request, 'core/serviciosConductor.html', contexto)
#-------------------------------------------------------------------------------------------------------------------------------

# ✅ Vistas de administrador (requieren login + superuser)
@login_required
@user_passes_test(es_admin)
def clientes(request):
    Listado_clientes = Clientes.objects.all()
    return render(request, 'core/clientesAdministrador.html', {"clientes": Listado_clientes})

#-------------------------------------------------------------------------------------------------------------------------------
def choferes(request):
    mensaje_vehiculo = ""
    mensaje_chofer = ""
    vehiculo_form = VehiculosForm()
    chofer_form = ChoferForm()
    chofer_form.fields['vehiculo'].required = True

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'vehiculo':
            vehiculo_form = VehiculosForm(request.POST, request.FILES)
            if vehiculo_form.is_valid():
                try:
                    vehiculo_form.save()
                    mensaje_vehiculo = "Vehiculo registrado correctamente."
                    vehiculo_form = VehiculosForm()
                except IntegrityError:
                    vehiculo_form.add_error('patente', "Esta patente ya está registrada.")
                    mensaje_vehiculo = "No se pudo registrar el vehiculo. Revisa la patente ingresada."
            else:
                mensaje_vehiculo = "Corrige los datos marcados e inténtalo nuevamente."

        elif form_type == 'chofer':
            chofer_form = ChoferForm(request.POST, request.FILES)
            chofer_form.fields['vehiculo'].required = True
            if chofer_form.is_valid():
                try:
                    chofer_form.save()
                    mensaje_chofer = "Chofer registrado correctamente."
                    chofer_form = ChoferForm()
                    chofer_form.fields['vehiculo'].required = True
                except IntegrityError:
                    chofer_form.add_error('usuario', "Este usuario ya está registrado como chofer.")
                    mensaje_chofer = "No se pudo registrar el chofer. Revisa la información ingresada."
            else:
                mensaje_chofer = "Corrige los datos marcados e inténtalo nuevamente."

    lista_choferes = Conductores.objects.select_related('usuario', 'vehiculo').all()
    Lista_vehiculos = Vehiculos.objects.all()
    contexto = {
        'choferes': lista_choferes,
        'vehiculos': Lista_vehiculos,
        'vehiculo_form': vehiculo_form,
        'mensaje_vehiculo': mensaje_vehiculo,
        'chofer_form': chofer_form,
        'mensaje_chofer': mensaje_chofer,
    }

    return render(request, 'core/choferesAdministrador.html', contexto)

#-------------------------------------------------------------------------------------------------------------------------------
@login_required
@user_passes_test(es_admin)
def form_crear_conductor(request):
    mensaje = ""
    if request.method == 'POST':
        form = ChoferForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                mensaje = "Datos Guardados Correctamente."
                form = ChoferForm()
            except IntegrityError:
                mensaje = "Error: El usuario o algún dato ya está registrado."
    else:
        form = ChoferForm()
    
    return render(request, 'core/form_crearConductor.html', {"form": form, "mensaje": mensaje})


@login_required
@user_passes_test(es_admin)
def form_crear_vehiculo(request):
    mensaje = ""
    if request.method == 'POST':
        form = VehiculosForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                mensaje = "Datos Guardados Correctamente."
                form = VehiculosForm()
            except IntegrityError:
                mensaje = "Error: Esta patente ya está registrada."
    else:
        form = VehiculosForm()
    
    return render(request, 'core/form_crearVehiculo.html', {"form": form, "mensaje": mensaje})
#-------------------------------------------------------------------------------------------------------------------------------

@login_required
@user_passes_test(es_admin)
def calendario(request):
    return render(request, 'core/calendarioAdministrador.html')

#-------------------------------------------------------------------------------------------------------------------------------

@login_required
@user_passes_test(es_admin)

def vista_tarifas_admin(request):
    mensaje = None
    
    # Manejar la creación de una nueva tarifa (cuando se envía el formulario del modal)
    if request.method == 'POST':
        form = TarifasForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                mensaje = "Tarifa guardada correctamente."
                # Después de guardar, redirigir o crear un nuevo formulario vacío
                form = TarifasForm() 
            except IntegrityError:
                mensaje = "Error: La comuna ya tiene una tarifa registrada."
                
        else:
            mensaje = "Error al validar los datos de la tarifa."
            # Si el formulario no es válido, se mantiene para mostrar los errores en el modal
            
    else:
        # Si es una petición GET, crea un formulario vacío
        form = TarifasForm()
    
    # Obtener todas las tarifas para mostrar la tabla
    tarifas_lista = Tarifas.objects.all()

    contexto = {
        'Tarifas': tarifas_lista,
        'form': form,
        'mensaje': mensaje,
    }
    
    return render(request, 'core/tarifasAdministrador.html', contexto)

#-------------------------------------------------------------------------------------------------------------------------------
def form_mod_tarifa(request, id):
    Tarifas_existentes = Tarifas.objects.get(id_tarifa=id)
    mensaje=""
    if request.method == 'POST':
        form = TarifasForm(request.POST, instance=Tarifas_existentes)
        if form.is_valid():
            form.save()
            mensaje = "Tarifa Modificada Correctamente"
            return redirect(to="vista_tarifas_admin")
    else:
        return render(request, "core/form_mod_tarifa.html", {"form":TarifasForm(instance=Tarifas_existentes), "mensaje":mensaje})

#-------------------------------------------------------------------------------------------------------------------------------


@login_required
@user_passes_test(es_admin)
def vist_Usuarios(request):
    Listado_usuarios = Usuarios.objects.all()
    return render(request, 'core/usuariosAdministrador.html ', {"Usuarios": Listado_usuarios})

#-------------------------------------------------------------------------------------------------------------------------------


@login_required
@user_passes_test(es_admin)
def form_Rol(request):
    form = Rol_Form()
    mensaje = ""
    if request.method == 'POST':
        form = Rol_Form(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data.get('nombre_Rol')
            if Rol_usuario.objects.filter(nombre_Rol = nombre ).exists():
                mensaje = "Este Rol ya está registrado."
            # 3. Si todo es correcto, guarda el formulario
            else:
                form.save()
                mensaje = "Datos Guardados Correctamente."
    
    return render(request, 'core/form_creaRol.html', {"form": form, "mensaje": mensaje})


#-------------------------------------------------------------------------------------------------------------------------------


@login_required
@user_passes_test(es_admin)
def form_crear_usuarios(request):
    form = UsuariosForm()
    mensaje = ""
    if request.method == 'POST':
        form = UsuariosForm(request.POST)
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
    
    return render(request, 'core/form_creaUsuarios.html', {"form": form, "mensaje": mensaje})

#-------------------------------------------------------------------------------------------------------------------------------
def form_mod_usu(request, id):
    Usuarios_existentes = Usuarios.objects.get(Rut=id)
    mensaje=""
    if request.method == 'POST':
        form = UsuariosForm(request.POST, request.FILES, instance=Usuarios_existentes)
        if form.is_valid():
            form.save()
            mensaje = "Usuario Modificado Correctamente"
            return redirect(to="vist_Usuarios")
    else:
        return render(request, "core/form_modUser.html", {"form":UsuariosForm(instance=Usuarios_existentes), "mensaje":mensaje})

#-------------------------------------------------------------------------------------------------------------------------------

#Esta es la vista de creacion del cliente 
@login_required
@user_passes_test(es_admin)
def form_clientes(request):
    form = ClientesForm()
    mensaje = ""
    if request.method == 'POST':
        form = ClientesForm(request.POST)
        if form.is_valid():
            rut = form.cleaned_data.get('Rut')
            
            # ✅ Paso a paso:
            # 1. Valida el RUT usando la función
            if not validar_rut(rut):
                mensaje = "El RUT ingresado no es válido."
            # 2. Si el RUT es válido, comprueba si ya existe
            elif Clientes.objects.filter(Rut=rut).exists():
                mensaje = "Este RUT ya está registrado."
            # 3. Si todo es correcto, guarda el formulario
            else:
                form.save()
                mensaje = "Datos Guardados Correctamente."
    
    return render(request, 'core/form_crearClientes.html', {"form": form, "mensaje": mensaje})

#-------------------------------------------------------------------------------------------------------------------------------
#esta es la vista de modificacion de el clliente
def form_modpro(request, id):
    Clientes_existentes = Clientes.objects.get(Rut=id)
    mensaje=""
    if request.method == 'POST':
        form = ClientesForm(request.POST, request.FILES, instance=Clientes_existentes)
        if form.is_valid():
            form.save()
            mensaje = "Datos Modificado Correctamente"
            return redirect(to="clientes")
    else:
        return render(request, "core/form_modusuario.html", {"form":ClientesForm(instance=Clientes_existentes), "mensaje":mensaje})

#-------------------------------------------------------------------------------------------------------------------------------
#Vista del administrador
@login_required
@user_passes_test(es_admin)
def admin_config(request):
    mensaje = None
    
    # ----------------------------------------------------------------------
    # 1. LÓGICA POST (Cuando se envía el formulario del modal) - SIN AJAX
    # ----------------------------------------------------------------------
    if request.method == 'POST':
        
        # Instancia el formulario con los datos enviados por el usuario
        form = ReservasForm(request.POST)
        
        if form.is_valid():
            # El formulario es válido, guardar la reserva
            reserva_nueva = form.save(commit=False)
            
            # NOTA: Aquí puedes asignar campos que no están en el formulario (si es necesario)
            # reserva_nueva.Confirmacion = True # Ejemplo
            
            reserva_nueva.save()
            
            # Comportamiento POST/Redirect/Get (para envíos tradicionales)
            return redirect('admin_config') 

        else:
            # Si el formulario NO es válido
            mensaje = "Error al guardar la reserva. Revise los campos."
            # El formulario con errores se pasa al contexto.
            
    # ----------------------------------------------------------------------
    # 2. LÓGICA GET (Cuando se carga la página por primera vez o después de un POST exitoso)
    # ----------------------------------------------------------------------
    else:
        # En una solicitud GET, inicializa un formulario vacío
        form = ReservasForm()

    reservas = Reservas.objects.select_related('Origen', 'Destino', 'Chofer_asignado__usuario').all()
    eventos = []
    for reserva in reservas:
        inicio = datetime.combine(reserva.Fecha, reserva.Hora)
        nombre_cliente = f"{reserva.Nombre_Cliente} {reserva.Apellidos_Cliente}".strip()
        chofer_asignado = None
        if reserva.Chofer_asignado and reserva.Chofer_asignado.usuario:
            chofer_usuario = reserva.Chofer_asignado.usuario
            chofer_asignado = f"{chofer_usuario.Nombres} {chofer_usuario.Apellidos}".strip()

        eventos.append({
            'id': str(reserva.Id_reserva),
            'title': f"Reserva - {nombre_cliente}".strip(),
            'start': inicio.isoformat(),
            'extendedProps': {
                'clienteNombre': nombre_cliente,
                'clienteTelefono': reserva.Telefono,
                'clienteCorreo': reserva.Correo or '',
                'desde': reserva.Origen.Nombre_Comuna if reserva.Origen else '',
                'hasta': reserva.Destino.Nombre_Comuna if reserva.Destino else '',
                'chofer': chofer_asignado or 'Sin asignar',
            }
        })

    contexto = {
        'form_reserva': form, 
        'mensaje': mensaje, 
        'reservas_json': json.dumps(eventos, ensure_ascii=False),
        'choferes_json': json.dumps([
            {
                'id': conductor.pk,
                'nombre': f"{conductor.usuario.Nombres} {conductor.usuario.Apellidos}".strip()
            }
            for conductor in Conductores.objects.select_related('usuario').all()
            if conductor.usuario
        ], ensure_ascii=False),
    }
    
    return render(request, 'core/reservasAdministrador.html', contexto)


@require_POST
def crear_reserva_web(request):
    try:
        datos = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'exito': False, 'mensaje': 'Solicitud inválida'}, status=400)

    formulario = ReservasWebForm(datos)
    if formulario.is_valid():
        formulario.save()
        return JsonResponse({'exito': True})

    return JsonResponse({'exito': False, 'errores': formulario.errors}, status=400)


@login_required
@user_passes_test(es_admin)
def reservas_web_pendientes(request):
    reservas_pendientes = ReservasWeb.objects.select_related('Origen', 'Destino').order_by('Fecha', 'Hora')
    datos = []
    for reserva in reservas_pendientes:
        datos.append({
            'id': reserva.Id_reserva,
            'nombre': f"{reserva.Nombre_Cliente} {reserva.Apellidos_Cliente}".strip(),
            'telefono': reserva.Telefono,
            'correo': reserva.Correo or '',
            'desde': reserva.Origen.Nombre_Comuna if reserva.Origen else '',
            'hasta': reserva.Destino.Nombre_Comuna if reserva.Destino else '',
            'direccion': reserva.Dirrecion,
            'fecha': reserva.Fecha.strftime('%Y-%m-%d'),
            'hora': reserva.Hora.strftime('%H:%M'),
            'personas': reserva.Cantidad_pasajeros,
            'maletas': reserva.Cantidad_maletas,
            'comentario': reserva.Comentario,
        })

    return JsonResponse({'reservas': datos})


@login_required
@user_passes_test(es_admin)
@require_POST
def aceptar_reserva_web(request):
    try:
        datos = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'exito': False, 'mensaje': 'Solicitud inválida'}, status=400)

    reserva_id = datos.get('reserva_id')
    chofer_id = datos.get('chofer_id')

    if not reserva_id or not chofer_id:
        return JsonResponse({'exito': False, 'mensaje': 'Datos incompletos'}, status=400)

    reserva_web = get_object_or_404(ReservasWeb, pk=reserva_id)
    chofer = get_object_or_404(Conductores.objects.select_related('usuario'), pk=chofer_id)

    reserva_confirmada = Reservas.objects.create(
        Nombre_Cliente=reserva_web.Nombre_Cliente,
        Apellidos_Cliente=reserva_web.Apellidos_Cliente,
        Telefono=reserva_web.Telefono,
        Correo=reserva_web.Correo,
        Origen=reserva_web.Origen,
        Destino=reserva_web.Destino,
        Dirrecion=reserva_web.Dirrecion,
        Fecha=reserva_web.Fecha,
        Hora=reserva_web.Hora,
        Cantidad_pasajeros=reserva_web.Cantidad_pasajeros,
        Cantidad_maletas=reserva_web.Cantidad_maletas,
        Confirmacion=True,
        Chofer_asignado=chofer,
    )

    evento = {
        'id': str(reserva_confirmada.Id_reserva),
        'title': f"Reserva - {reserva_confirmada.Nombre_Cliente} {reserva_confirmada.Apellidos_Cliente}".strip(),
        'start': datetime.combine(reserva_confirmada.Fecha, reserva_confirmada.Hora).isoformat(),
        'extendedProps': {
            'clienteNombre': f"{reserva_confirmada.Nombre_Cliente} {reserva_confirmada.Apellidos_Cliente}".strip(),
            'clienteTelefono': reserva_confirmada.Telefono,
            'clienteCorreo': reserva_confirmada.Correo or '',
            'desde': reserva_confirmada.Origen.Nombre_Comuna if reserva_confirmada.Origen else '',
            'hasta': reserva_confirmada.Destino.Nombre_Comuna if reserva_confirmada.Destino else '',
            'chofer': f"{chofer.usuario.Nombres} {chofer.usuario.Apellidos}".strip(),
        },
        'color': '#17a2b8',
    }

    reserva_web.delete()

    return JsonResponse({'exito': True, 'evento': evento})


@login_required
@user_passes_test(es_admin)
@require_POST
def rechazar_reserva_web(request):
    try:
        datos = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'exito': False, 'mensaje': 'Solicitud inválida'}, status=400)

    reserva_id = datos.get('reserva_id')

    if not reserva_id:
        return JsonResponse({'exito': False, 'mensaje': 'Datos incompletos'}, status=400)

    reserva_web = get_object_or_404(ReservasWeb, pk=reserva_id)
    reserva_web.delete()

    return JsonResponse({'exito': True})
