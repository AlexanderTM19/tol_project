# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.db.utils import IntegrityError
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from faker import Faker
from .form import ClientesForm, UsuariosForm, Rol_Form, CustomLoginForm, PasswordResetRequestForm, PasswordResetConfirmForm, ChoferForm, VehiculosForm, TarifasForm, ReservasForm, ReservasWebForm,TrasporteForm
from .models import Clientes, Usuarios, Rol_usuario, Conductores, Vehiculos, Tarifas, Reservas, ReservasWeb,Trasporte, PasswordResetToken
import random
import json
from django.http import JsonResponse, HttpResponse
import secrets
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.db.models import Count, Q
from django.utils.dateformat import DateFormat 
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_GET
from django.utils import timezone
from django.contrib import messages 
from openpyxl import Workbook

# âŒ FUNCIÃ“N events_json ELIMINADA para revertir la funcionalidad AJAX del calendario.
# def events_json(request):
#     # ... cÃ³digo eliminado ...
#     pass


# Función de validación de RUT
def validar_rut(rut):
    """
    Valida un RUT chileno (con o sin puntos/guiÃ³n)
    """
    
    rut = rut.upper().replace(".", "").replace("-", "")
    
    # Valida el formato y la longitud bÃ¡sica
    if not rut or not rut[:-1].isdigit():
        return False
    
    # Extrae el dÃ­gito verificador
    dv = rut[-1]
    
    # Aplica el algoritmo de MÃ³dulo 11
    factor = 2
    suma = 0
    for digito in reversed(rut[:-1]):
        suma += int(digito) * factor
        factor = factor + 1 if factor < 7 else 2
        
    dv_calculado = 11 - (suma % 11)
    
    # Compara el dÃ­gito verificador calculado con el original
    if dv_calculado == 11:
        dv_final = "0"
    elif dv_calculado == 10:
        dv_final = "K"
    else:
        dv_final = str(dv_calculado)
        
    return dv == dv_final


# âœ… FunciÃ³n para validar si el usuario es superusuario
def es_admin(user):
    return user.is_superuser

# Vistas pÃºblicas
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

# Vista personalizada de login con redirecciÃ³n por perfil
# Vista personalizada de login con redireccion por perfil
def login_view(request):
    error = None
    if request.method == "POST":
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                try:
                    if user.Rol.nombre_Rol == 'Administrador' or user.Rol.nombre_Rol == 'Secretaria':
                        return redirect('admin_config')
                    elif user.Rol.nombre_Rol == 'Chofer':
                        return redirect('ficha_conductor')
                    else:
                        return redirect('inicio')
                except AttributeError:
                    return redirect('inicio')
            else:
                error = "Usuario o contrasena incorrectos"
        else:
            error = "Usuario o contrasena incorrectos"
    else:
        form = CustomLoginForm()
    return render(request, 'core/login.html', {'form': form, 'error': error })

# Flujo para recuperar contrasena sin hash
def password_reset_request(request):
    form = PasswordResetRequestForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        rut = form.cleaned_data.get('rut', '').strip()
        correo = form.cleaned_data.get('correo', '').strip().lower()

        usuario = Usuarios.objects.filter(
            Rut__iexact=rut,
            Correo__iexact=correo
        ).first()
        if not usuario:
            messages.error(request, 'No se encontro un usuario con esos datos.')
            return render(request, 'core/password_reset_request.html', {'form': form})

        PasswordResetToken.objects.filter(usuario=usuario, usado=False).update(usado=True)
        token = secrets.token_urlsafe(32)
        registro = PasswordResetToken.objects.create(usuario=usuario, token=token)
        reset_link = request.build_absolute_uri(reverse('password_reset_confirm', args=[registro.token]))

        try:
            nombre_completo = f"{getattr(usuario, 'Nombres', '').strip()} {getattr(usuario, 'Apellidos', '').strip()}".strip()
            saludo = f"Hola, {nombre_completo}" if nombre_completo else "Hola"
            mensaje = (
                f"{saludo},\n\n"
                "Recibimos una solicitud para restablecer la contraseña de tu cuenta. "
                "Si fuiste tú, abre el siguiente enlace seguro y define una nueva contraseña:\n\n"
                f"{reset_link}\n\n"
                "Este enlace es personal y tiene un tiempo limitado de vigencia. "
                "Si no solicitaste el cambio, puedes ignorar este correo y tu contraseña seguirá siendo la misma.\n\n"
                "Gracias por utilizar nuestros servicios.\n"
                "Equipo de soporte"
            )
            send_mail(
                subject='Restablecimiento de contraseña',
                message=mensaje,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@tol.local'),
                recipient_list=[usuario.Correo],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request, 'Si los datos son correctos, te enviamos un correo con el enlace de recuperacion.')
        return render(request, 'core/password_reset_request.html', {'form': PasswordResetRequestForm()})

    return render(request, 'core/password_reset_request.html', {'form': form})


def password_reset_confirm(request, token):
    token_obj = get_object_or_404(PasswordResetToken, token=token)
    if not token_obj.esta_vigente():
        messages.error(request, 'El enlace ya no es valido. Solicita uno nuevo.')
        return render(request, 'core/password_reset_confirm.html', {'form': None, 'token_valido': False})

    form = PasswordResetConfirmForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        nueva = form.cleaned_data.get('nueva_contrasena')
        token_obj.usuario.ClaveUsuario = nueva
        token_obj.usuario.save()
        token_obj.usado = True
        token_obj.save()
        messages.success(request, 'Contrasena actualizada. Ya puedes iniciar sesion.')
        return redirect('login')

    return render(request, 'core/password_reset_confirm.html', {'form': form, 'token_valido': True})

# Vista para ficha del conductor
from django.contrib.auth.decorators import login_required
@login_required
def ficha_conductor(request):
    try:
        conductor = Conductores.objects.select_related('usuario', 'vehiculo').get(usuario=request.user)
    except Conductores.DoesNotExist:
        conductor = None

    try:
        # 1. Filtramos solo las reservas que han sido 'REALIZADO'.
        # 2. Ordenamos por la 'Fecha' y luego por la 'Hora' (descendente).
        # 3. Usamos .select_related('Chofer_asignado') para obtener los datos del conductor de una vez.
        
        # El mÃ©todo .latest() funciona si el campo es DateTimeField. 
        # Como tienes DateField y TimeField por separado, la forma mÃ¡s fiable es usar .order_by() y tomar el primero.
        
        ultima_reserva = Reservas.objects.filter(
            estado='REALIZADO',
            Chofer_asignado__isnull=False # Asegura que tenga un conductor asignado
        ).select_related('Chofer_asignado').order_by('-Fecha', '-Hora').first()
        
        if ultima_reserva:
            ultimo_conductor = ultima_reserva.Chofer_asignado
        else:
            ultimo_conductor = None
            
    except Reservas.DoesNotExist:
        # Esto maneja el caso en que no hay reservas en absoluto
        ultimo_conductor = None
    
    # Anotar cantidad de servicios REALIZADOS por conductor usando el reverse accessor correcto
    Listado_conductores = Conductores.objects.all().annotate(
        servicios_realizados=Count('reservas', filter=Q(reservas__estado='REALIZADO'))
    )

    # Conductor con mÃ¡s y menos servicios realizados
    conductor_mas_servicios = Listado_conductores.order_by('-servicios_realizados', 'Nro_ficha').first()
    conductor_menos_servicios = Listado_conductores.order_by('servicios_realizados', 'Nro_ficha').first()
    
    context = {
    # ... otros datos ...
    'ultima_reserva_realizada': ultima_reserva,        # La reserva completa (para fecha/hora)
    'ultimo_conductor_servicio': ultimo_conductor, 
    'conductor': conductor,
    'Lista_conductores': Listado_conductores,
    'total_filas': Listado_conductores.count(),
    'conductor_mas_servicios': conductor_mas_servicios,
    'conductor_menos_servicios': conductor_menos_servicios,
    'vehiculo': conductor.vehiculo if conductor else None,# El objeto Conductor (si existe)
    }

    
    return render(request, 'core/fichaConductor.html', context)


@login_required
def perfil_conductor_view(request):
    try:
        conductor = Conductores.objects.select_related('usuario', 'vehiculo').get(usuario=request.user)
    except Conductores.DoesNotExist:
        return redirect('inicio')

    # Calcular servicios totales realizados (estado REALIZADO) por este conductor
    servicios_realizados = Reservas.objects.filter(Chofer_asignado=conductor, estado='REALIZADO').count()

    contexto = {
        'conductor': conductor,
        'vehiculo': conductor.vehiculo,
        'servicios_realizados': servicios_realizados,
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

# âœ… Vistas de administrador (requieren login + superuser)
@login_required
@user_passes_test(es_admin)
def clientes(request):
    Listado_clientes = Clientes.objects.all()
    return render(request, 'core/clientesAdministrador.html', {"clientes": Listado_clientes})

#-------------------------------------------------------------------------------------------------------------------------------
def api_ingresos_mensual(request, year, month):
    """
    Devuelve los ingresos (Monto_tarifa) por dÃ­a para un mes y aÃ±o especÃ­ficos,
    para alimentar el filtro 'mes' del grÃ¡fico.
    """
    
    try:
        # 1. Obtener la suma de ingresos por dÃ­a
        ingresos_por_dia = Reservas.objects.filter(
            Fecha__year=year,
            Fecha__month=month,
            estado='REALIZADO'
        ).values('Fecha__day').annotate(total=Sum('Monto_tarifa')).order_by('Fecha__day')
        
        # Calcular cuÃ¡ntos dÃ­as tiene ese mes (para inicializar el array)
        if year > 0 and month >= 1 and month <= 12:
            try:
                # Usamos el dÃ­a 1 del mes siguiente menos un dÃ­a (dÃ­a 0)
                # para obtener el Ãºltimo dÃ­a del mes actual.
                dias_en_mes = (datetime(year, month % 12 + 1, 1) - datetime(year, month, 1)).days if month < 12 else 31
            except ValueError:
                # Si el mes es 12, calcular dÃ­as de diciembre
                dias_en_mes = 31
        else:
            return JsonResponse({'error': 'ParÃ¡metros de fecha invÃ¡lidos'}, status=400)

        ingresos_data = [0] * dias_en_mes
        
        # 2. Llenar el array de datos
        for item in ingresos_por_dia:
            # Los dÃ­as en Django son 1-N. El Ã­ndice del array es 0-(N-1).
            monto_en_miles = (item['total'] or 0) / 1000
            ingresos_data[item['Fecha__day'] - 1] = round(monto_en_miles, 2)
            
        # 3. Devolver los datos en formato JSON
        return JsonResponse({'ingresos': ingresos_data})
        
    except Exception as e:
        # Manejo bÃ¡sico de errores de servidor/DB
        return JsonResponse({'error': str(e)}, status=500)


def api_ingresos_anual(request, year):
    """Devuelve los ingresos (Monto_tarifa) por mes para un aÃ±o especÃ­fico.
    Responde con JSON { 'labels': [...], 'ingresos': [...] } donde los ingresos estÃ¡n en 'miles' (divididos por 1000).
    """
    try:
        ingresos_por_mes = Reservas.objects.filter(
            Fecha__year=year,
            estado='REALIZADO'
        ).values('Fecha__month').annotate(total=Sum('Monto_tarifa')).order_by('Fecha__month')

        meses_nombre = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
        ingresos_data = [0] * 12
        for item in ingresos_por_mes:
            idx = item.get('Fecha__month', 1) - 1
            ingresos_data[idx] = round(((item.get('total') or 0) / 1000), 2)

        return JsonResponse({'labels': meses_nombre, 'ingresos': ingresos_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@user_passes_test(es_admin)
@require_GET
def estadisticas_data(request):
    """Endpoint de ingresos con totales filtrados.
    Devuelve etiquetas/datasets (montos en miles para el gr?fico) y totales en CLP:
    { labels, datasets, total_empresa, ingreso_personal }
    """
    period = request.GET.get('period', 'anio')
    try:
        now = datetime.now().date()
        if period == 'anio':
            year = int(request.GET.get('year', now.year))
            labels = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
            values = [0] * 12
            total_empresa = 0
            q = Reservas.objects.filter(estado='REALIZADO', Fecha__year=year).values('Fecha__month').annotate(total=Sum('Monto_tarifa'))
            for it in q:
                m = int(it.get('Fecha__month', 1)) - 1
                monto = (it.get('total') or 0)
                total_empresa += monto
                values[m] = round((monto / 1000), 2)
            datasets = [{ 'label': f'Ingresos {year}', 'data': values }]
            ingreso_personal = int(total_empresa * 0.20)
            return JsonResponse({ 'labels': labels, 'datasets': datasets, 'total_empresa': total_empresa, 'ingreso_personal': ingreso_personal })

        if period == 'mes':
            year = int(request.GET.get('year', now.year))
            month = int(request.GET.get('month', now.month))
            from calendar import monthrange
            dim = monthrange(year, month)[1]
            labels = [str(i) for i in range(1, dim+1)]
            values = [0] * dim
            total_empresa = 0
            q = Reservas.objects.filter(estado='REALIZADO', Fecha__year=year, Fecha__month=month).values('Fecha__day').annotate(total=Sum('Monto_tarifa'))
            for it in q:
                d = int(it.get('Fecha__day', 1)) - 1
                if 0 <= d < dim:
                    monto = (it.get('total') or 0)
                    total_empresa += monto
                    values[d] = round((monto / 1000), 2)
            datasets = [{ 'label': f'Ingresos {month}/{year}', 'data': values }]
            ingreso_personal = int(total_empresa * 0.20)
            return JsonResponse({ 'labels': labels, 'datasets': datasets, 'total_empresa': total_empresa, 'ingreso_personal': ingreso_personal })

        if period == 'semana':
            year = int(request.GET.get('year', now.year))
            week = int(request.GET.get('week', now.isocalendar()[1]))
            import datetime as _dt
            monday = _dt.date.fromisocalendar(year, week, 1)
            labels = ['Lun','Mar','Mie','Jue','Vie','Sab','Dom']
            values = []
            total_empresa = 0
            for i in range(7):
                day = monday + _dt.timedelta(days=i)
                total = Reservas.objects.filter(estado='REALIZADO', Fecha=day).aggregate(total=Sum('Monto_tarifa')).get('total') or 0
                total_empresa += total
                values.append(round((total / 1000), 2))
            datasets = [{ 'label': f'Ingresos semana {week}/{year}', 'data': values }]
            ingreso_personal = int(total_empresa * 0.20)
            return JsonResponse({ 'labels': labels, 'datasets': datasets, 'total_empresa': total_empresa, 'ingreso_personal': ingreso_personal })

        if period == 'dia':
            date_str = request.GET.get('date', now.isoformat())
            try:
                d = datetime.strptime(date_str, '%Y-%m-%d').date()
            except Exception:
                d = now
            labels = [f"{h}:00" for h in range(24)]
            values = [0] * 24
            total_empresa = 0
            q = Reservas.objects.filter(estado='REALIZADO', Fecha=d)
            for r in q:
                try:
                    h = int(r.Hora.hour)
                    if 0 <= h < 24:
                        monto = (r.Monto_tarifa or 0)
                        total_empresa += monto
                        values[h] += monto
                except Exception:
                    continue
            values = [ round((v / 1000), 2) for v in values ]
            datasets = [{ 'label': f'Ingresos {d.isoformat()}', 'data': values }]
            ingreso_personal = int(total_empresa * 0.20)
            return JsonResponse({ 'labels': labels, 'datasets': datasets, 'total_empresa': total_empresa, 'ingreso_personal': ingreso_personal })

        if period == 'rango':
            def parse_date(s):
                try:
                    return datetime.strptime(s, '%Y-%m-%d').date()
                except Exception:
                    return None

            from1 = request.GET.get('from1')
            to1 = request.GET.get('to1')
            from2 = request.GET.get('from2')
            to2 = request.GET.get('to2')

            d1 = parse_date(from1)
            d2 = parse_date(to1)
            labels = []
            datasets = []
            total_empresa = 0
            if d1 and d2 and d1 <= d2:
                days = (d2 - d1).days + 1
                labels = [f'D?a {i+1}' for i in range(days)]
                vals = []
                for i in range(days):
                    day = d1 + timedelta(days=i)
                    total = Reservas.objects.filter(estado='REALIZADO', Fecha=day).aggregate(total=Sum('Monto_tarifa')).get('total') or 0
                    total_empresa += total
                    vals.append(round((total / 1000), 2))
                datasets.append({ 'label': f'Rango 1 ({d1} a {d2})', 'data': vals })

            if from2 and to2:
                d3 = parse_date(from2)
                d4 = parse_date(to2)
                if d3 and d4 and d3 <= d4:
                    days2 = (d4 - d3).days + 1
                    maxlen = max(len(labels), days2)
                    if len(labels) < maxlen:
                        labels = labels + [f'D?a {i+1}' for i in range(len(labels), maxlen)]
                    vals2 = []
                    for i in range(days2):
                        day = d3 + timedelta(days=i)
                        total = Reservas.objects.filter(estado='REALIZADO', Fecha=day).aggregate(total=Sum('Monto_tarifa')).get('total') or 0
                        vals2.append(round((total / 1000), 2))
                    if len(vals2) < maxlen:
                        vals2 = vals2 + [None] * (maxlen - len(vals2))
                    datasets.append({ 'label': f'Rango 2 ({d3} a {d4})', 'data': vals2 })

            ingreso_personal = int(total_empresa * 0.20)
            return JsonResponse({ 'labels': labels, 'datasets': datasets, 'total_empresa': total_empresa, 'ingreso_personal': ingreso_personal })

        return JsonResponse({ 'labels': [], 'datasets': [], 'total_empresa': 0, 'ingreso_personal': 0 })

    except Exception as e:
        return JsonResponse({ 'error': str(e) }, status=500)
#-------------------------------------------------------------------------------------------------------------------------------

@login_required
@user_passes_test(es_admin)
def estadisticas(request):
    # Consultas reales para las tarjetas
    # Servicios por estado (modelo Reservas)
    servicios_realizados = Reservas.objects.filter(estado='REALIZADO').count()
    servicios_por_realizar = Reservas.objects.filter(estado='PENDIENTE').count()
    servicios_cancelados = Reservas.objects.filter(estado='CANCELADO').count()

    # Clientes: no hay campo de fecha de creaciÃ³n, usamos Cantidad_viajes como proxy
    clientes_nuevos = Clientes.objects.filter(Cantidad_viajes=0).count()
    clientes_frecuentes = Clientes.objects.filter(Cantidad_viajes__gt=0).count()

    # Totales monetarios: sumar Monto_tarifa de Reservas REALIZADO
    total_empresa_agg = Reservas.objects.filter(estado='REALIZADO').aggregate(total=Sum('Monto_tarifa'))
    total_empresa = total_empresa_agg.get('total') or 0

    # Ingreso personal: estimaciÃ³n (esta suposiciÃ³n se mantiene por ahora).
    ingreso_personal = int(total_empresa * 0.20)

    # ----------------------------------------------------------------------
    # â­ MODIFICACIONES PARA EL GRÃFICO DE INGRESOS MENSUALES
    # ----------------------------------------------------------------------
    
    current_year = datetime.now().year
    
    # 1. Obtener la suma de ingresos por mes del aÃ±o actual
    # Usamos __year y __month para agrupar por mes y aÃ±o
    ingresos_por_mes = Reservas.objects.filter(
        Fecha__year=current_year,
        estado='REALIZADO'
    ).values('Fecha__month').annotate(total=Sum('Monto_tarifa')).order_by('Fecha__month')
    
    # 2. Preparar los datos en formato de lista para el JSON
    meses_nombre = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
    ingresos_data = [0] * 12 # Inicializar 12 meses a 0
    
    for item in ingresos_por_mes:
        # Los meses en Django son 1-12. El Ã­ndice del array es 0-11.
        # Dividimos por 1000 para que el grÃ¡fico muestre "CLP - miles" (como lo pide tu JS)
        monto_en_miles = (item['total'] or 0) / 1000
        ingresos_data[item['Fecha__month'] - 1] = round(monto_en_miles, 2)
        
    # 3. Serializar los datos a JSON strings
    ingresos_mensuales_json = json.dumps(ingresos_data)
    etiquetas_meses_json = json.dumps(meses_nombre)

    contexto = {
        'servicios_realizados': servicios_realizados,
        'servicios_por_realizar': servicios_por_realizar,
        'servicios_cancelados': servicios_cancelados,
        'clientes_nuevos': clientes_nuevos,
        'clientes_frecuentes': clientes_frecuentes,
        'total_empresa': total_empresa,
        'ingreso_personal': ingreso_personal,
        
        # â­ AÃ±adir los datos del grÃ¡fico al contexto
        'ingresos_mensuales_json': ingresos_mensuales_json,
        'etiquetas_meses_json': etiquetas_meses_json,
    }
    
    return render(request, 'core/estadisticas.html', contexto)
#-------------------------------------------------------------------------------------------------------------------------------
@login_required
@user_passes_test(es_admin)
def choferes(request):
    # 1. InicializaciÃ³n del formulario para el contexto GET/Error
    chofer_form = ChoferForm()
    # Aseguramos que el campo 'vehiculo' sea requerido al inicializar
    chofer_form.fields['vehiculo'].required = True
    
    # --- LÃ³gica de Manejo de Solicitud POST ---
    if request.method == 'POST':
        # Instanciar el formulario con los datos POST
        chofer_form_to_handle = ChoferForm(request.POST, request.FILES)
        chofer_form_to_handle.fields['vehiculo'].required = True # Reafirmar required
        
        if chofer_form_to_handle.is_valid():
            try:
                # Guardar el objeto en la base de datos
                chofer_form_to_handle.save()
                
                # APLICAR PRG (Post-Redirect-Get): RedirecciÃ³n exitosa
                messages.success(request, "Chofer registrado correctamente.")
                return redirect('choferes')
            
            except IntegrityError:
                # Error de integridad (ej: DNI/RUT/Usuario ya existe)
                messages.error(request, "No se pudo registrar el chofer. El DNI/RUT/Usuario ya estÃ¡ asignado.")
                # El formulario con errores se pasa al contexto
                chofer_form = chofer_form_to_handle 
            
            except Exception:
                # Capturar cualquier otro error inesperado
                messages.error(request, "Error inesperado al registrar el chofer. Contacta a soporte.")
                chofer_form = chofer_form_to_handle
        
        else:
            # El formulario NO es vÃ¡lido (errores de validaciÃ³n de campos)
            messages.error(request, "Corrige los datos marcados e intÃ©ntalo nuevamente.")
            chofer_form = chofer_form_to_handle
            
        # Si hubo un POST con error, el flujo continÃºa a la secciÃ³n final para renderizar la pÃ¡gina con errores.
        
    # --- LÃ³gica GET (se ejecuta para GET y para POST con errores) ---
    
    # Obtener lista de choferes (asumo que 'Conductores' es tu modelo)
    # select_related mejora la eficiencia al obtener datos relacionados
    try:
        lista_choferes = (
            Conductores.objects
            .select_related('usuario', 'vehiculo')
            .prefetch_related('reservas_set', 'reservas_set__Origen')
            .all()
        )
    except NameError:
        # En caso de que el modelo Conductores no estÃ© definido/importado
        lista_choferes = [] 
        
    contexto = {
        'choferes': lista_choferes,
        # Contiene el form limpio (GET) o con errores y datos ingresados (POST fallido)
        'chofer_form': chofer_form, 
    }

    return render(request, 'core/choferesAdministrador.html', contexto)
#-------------------------------------------------------------------------------------------------------------------------------
def vehiculo(request):
    """
    Vista para manejar el registro de nuevos vehÃ­culos.
    """
    vehiculo_form = TrasporteForm()

    if request.method == 'POST':
        form_to_handle = TrasporteForm(request.POST, request.FILES)
        
        if form_to_handle.is_valid():
            try:
                form_to_handle.save()
                messages.success(request, "VehÃ­culo registrado correctamente.")
                return redirect('vehiculo')
            except IntegrityError as e:
            # 'e' ahora contiene el objeto de la excepciÃ³n IntegrityError
            # str(e) convierte ese objeto en su representaciÃ³n de cadena (el mensaje del error).
                messages.error(request, f"No se pudo registrar el vehÃ­culo. Error tÃ©cnico: {e}")
                vehiculo_form = form_to_handle # Mantiene el formulario con el error para mostrarlo
        else:
            messages.error(request, "Corrige los datos marcados e intÃ©ntalo nuevamente.")
            vehiculo_form = form_to_handle # Mantiene el formulario con los errores de validaciÃ³n

    # LÃ³gica GET: se ejecuta para el mÃ©todo GET y para POST con errores de validaciÃ³n/IntegrityError
    Lista_vehiculos = Trasporte.objects.all()
    
    contexto = {
        'vehiculos': Lista_vehiculos,
        'vehiculo_form': vehiculo_form,
    }

    return render(request, 'core/vehiculosAdministrador.html', contexto)

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
                mensaje = "Error: El usuario o algÃºn dato ya estÃ¡ registrado."
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
                mensaje = "Error: Esta patente ya estÃ¡ registrada."
    else:
        form = VehiculosForm()
    
    return render(request, 'core/form_crearVehiculo.html', {"form": form, "mensaje": mensaje})
#-------------------------------------------------------------------------------------------------------------------------------

@login_required
@user_passes_test(es_admin)
def calendario(request):
    eventos = _construir_eventos_reservas()
    contexto = {
        'reservas_json': json.dumps(eventos, ensure_ascii=False),
    }
    return render(request, 'core/calendarioAdministrador.html', contexto)

#-------------------------------------------------------------------------------------------------------------------------------

@login_required
@user_passes_test(es_admin)

def vista_tarifas_admin(request):
    mensaje = None
    
    # Manejar la creaciÃ³n de una nueva tarifa (cuando se envÃ­a el formulario del modal)
    if request.method == 'POST':
        form = TarifasForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                mensaje = "Tarifa guardada correctamente."
                # DespuÃ©s de guardar, redirigir o crear un nuevo formulario vacÃ­o
                form = TarifasForm() 
            except IntegrityError:
                mensaje = "Error: La comuna ya tiene una tarifa registrada."
                
        else:
            mensaje = "Error al validar los datos de la tarifa."
            # Si el formulario no es vÃ¡lido, se mantiene para mostrar los errores en el modal
            
    else:
        # Si es una peticiÃ³n GET, crea un formulario vacÃ­o
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
@login_required
@user_passes_test(es_admin)
def delete_Tarifa(request, id):
    tarifa_eliminar = Tarifas.objects.get(id_tarifa=id)
    tarifa_eliminar.delete()
    return redirect(to="vista_tarifas_admin")

#-------------------------------------------------------------------------------------------------------------------------------
@login_required
@user_passes_test(es_admin)
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
                mensaje = "Este Rol ya estÃ¡ registrado."
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
            
            # âœ… Paso a paso:
            # 1. Valida el RUT usando la funciÃ³n
            if not validar_rut(rut):
                mensaje = "El RUT ingresado no es vÃ¡lido."
            # 2. Si el RUT es vÃ¡lido, comprueba si ya existe
            elif Usuarios.objects.filter(Rut=rut).exists():
                mensaje = "Este RUT ya estÃ¡ registrado."
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
            
            # âœ… Paso a paso:
            # 1. Valida el RUT usando la funciÃ³n
            if not validar_rut(rut):
                mensaje = "El RUT ingresado no es vÃ¡lido."
            # 2. Si el RUT es vÃ¡lido, comprueba si ya existe
            elif Clientes.objects.filter(Rut=rut).exists():
                mensaje = "Este RUT ya estÃ¡ registrado."
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
def _construir_eventos_reservas():
    reservas = Reservas.objects.select_related('Origen', 'Destino', 'Chofer_asignado__usuario').all()
    eventos = []
    # Fecha/hora actual sin tz para comparar con Date/Time de la BD
    ahora = timezone.localtime().replace(tzinfo=None)
    for reserva in reservas:
        inicio = datetime.combine(reserva.Fecha, reserva.Hora)
        # Auto-marcar como REALIZADO si la fecha/hora ya pasÃ³ y no estÃ¡ cancelada
        if inicio < ahora and (reserva.estado or 'PENDIENTE') == 'PENDIENTE':
            reserva.estado = 'REALIZADO'
            try:
                reserva.save(update_fields=['estado'])
            except Exception:
                # En caso de algÃºn error de escritura, continuamos mostrando el estado derivado
                pass
        nombre_cliente = f"{reserva.Nombre_Cliente} {reserva.Apellidos_Cliente}".strip()
        chofer_asignado = None
        if reserva.Chofer_asignado and reserva.Chofer_asignado.usuario:
            chofer_usuario = reserva.Chofer_asignado.usuario
            chofer_asignado = f"{chofer_usuario.Nombres} {chofer_usuario.Apellidos}".strip()

        estado = (reserva.estado or '').lower()
        clase_estado = f"evt-{estado}" if estado else ''

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
                'nro_vuelo': reserva.nro_vuelo or '',
                'chofer': chofer_asignado or 'Sin asignar',
                'monto': reserva.Monto_tarifa or 0 ,
                'estado': reserva.estado or 'PENDIENTE',
            },
            'classNames': [clase_estado] if clase_estado else [],
        })

    return eventos


def _enviar_correo_confirmacion_reserva(reserva):
    """
    Envía un correo de confirmación de recepción de reserva al cliente (si hay correo).
    No afirma confirmación definitiva, solo que la solicitud fue recibida.
    """
    destinatario = (reserva.Correo or '').strip()
    if not destinatario:
        return
    try:
        nombre = f"{reserva.Nombre_Cliente} {reserva.Apellidos_Cliente}".strip() or "Cliente"
        fecha_hora = datetime.combine(reserva.Fecha, reserva.Hora).strftime('%d-%m-%Y %H:%M')
        origen = reserva.Origen.Nombre_Comuna if reserva.Origen else 'Por confirmar'
        destino = reserva.Destino.Nombre_Comuna if reserva.Destino else 'Por confirmar'
        direccion = reserva.Dirrecion or 'Por confirmar'
        nro_vuelo = reserva.nro_vuelo or 'No informado'
        tarifa = reserva.Monto_tarifa if reserva.Monto_tarifa not in (None, '') else 'Por confirmar'

        asunto = "Hemos recibido su solicitud de reserva"
        mensaje = (
            f"Estimado/a {nombre},\n\n"
            "Hemos recibido su solicitud de reserva con exito. Enviaremos la confirmacion o aceptacion en breve.\n\n"
            "Detalle de la solicitud:\n"
            f"- Fecha y hora: {fecha_hora}\n"
            f"- Origen: {origen}\n"
            f"- Destino: {destino}\n"
            f"- Direccion: {direccion}\n"
            f"- Numero de vuelo: {nro_vuelo}\n"
            f"- Tarifa: {tarifa}\n\n"
            "Este correo es solo de recepcion. Nos contactaremos pronto para confirmar o ajustar cualquier detalle.\n\n"
            "Gracias por preferirnos.\n"
        )
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@tol.local'),
            recipient_list=[destinatario],
            fail_silently=True,
        )
    except Exception:
        # No interrumpir el flujo principal si el correo falla
        pass


@login_required
@user_passes_test(es_admin)
@require_GET
def exportar_reserva_excel(request, reserva_id):
    """
    Genera un archivo Excel con los datos clave de una reserva.
    Incluye: nombre completo, fecha y hora, dirección exacta y comuna, número de vuelo y tarifa.
    """
    reserva = get_object_or_404(Reservas.objects.select_related('Origen', 'Destino'), pk=reserva_id)
    wb = Workbook()
    ws = wb.active
    ws.title = "Reserva"

    ws.append(["Nombre y apellido", "Fecha y hora", "Dirección exacta y comuna", "Número de vuelo", "Tarifa"])

    fecha_hora = datetime.combine(reserva.Fecha, reserva.Hora)
    comuna = ''
    if reserva.Origen and reserva.Origen.Nombre_Comuna:
        comuna = reserva.Origen.Nombre_Comuna
    elif reserva.Destino and reserva.Destino.Nombre_Comuna:
        comuna = reserva.Destino.Nombre_Comuna
    direccion = reserva.Dirrecion or ''
    direccion_completa = f"{direccion} - {comuna}" if comuna else direccion
    tarifa = reserva.Monto_tarifa if reserva.Monto_tarifa is not None else ''

    ws.append([
        f"{reserva.Nombre_Cliente} {reserva.Apellidos_Cliente}".strip(),
        fecha_hora.strftime('%d-%m-%Y %H:%M'),
        direccion_completa,
        reserva.nro_vuelo or '',
        tarifa,
    ])

    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter
        for cell in col:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        ws.column_dimensions[col_letter].width = min(max_length + 2, 50)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=reserva_{reserva.Id_reserva}.xlsx'
    wb.save(response)
    return response


@login_required
@user_passes_test(es_admin)
def admin_config(request):
    mensaje = None
    
    # ----------------------------------------------------------------------
    # 1. LÃ“GICA POST (Cuando se envÃ­a el formulario del modal) - SIN AJAX
    # ----------------------------------------------------------------------
    if request.method == 'POST':
        
        # Instancia el formulario con los datos enviados por el usuario
        form = ReservasForm(request.POST)
        
        if form.is_valid():
            # El formulario es vÃ¡lido, guardar la reserva
            reserva_nueva = form.save(commit=False)
            if not reserva_nueva.estado:
                reserva_nueva.estado = 'PENDIENTE'
            
            # NOTA: AquÃ­ puedes asignar campos que no estÃ¡n en el formulario (si es necesario)
            # reserva_nueva.Confirmacion = True # Ejemplo
            
            reserva_nueva.save()
            _enviar_correo_confirmacion_reserva(reserva_nueva)
            
            # Comportamiento POST/Redirect/Get (para envÃ­os tradicionales)
            return redirect('admin_config') 

        else:
            # Si el formulario NO es vÃ¡lido
            mensaje = "Error al guardar la reserva. Revise los campos."
            # El formulario con errores se pasa al contexto.
            
    # ----------------------------------------------------------------------
    # 2. LÃ“GICA GET (Cuando se carga la pÃ¡gina por primera vez o despuÃ©s de un POST exitoso)
    # ----------------------------------------------------------------------
    else:
        # En una solicitud GET, inicializa un formulario vacÃ­o
        form = ReservasForm()

    eventos = _construir_eventos_reservas()

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


@login_required
@user_passes_test(es_admin)
@require_POST
def crear_reserva_admin(request):
    form = ReservasForm(request.POST)
    if form.is_valid():
        reserva = form.save(commit=False)
        if not reserva.estado:
            reserva.estado = 'PENDIENTE'
        reserva.save()
        _enviar_correo_confirmacion_reserva(reserva)
        # Construir payload de evento para FullCalendar
        chofer_nombre = 'Sin asignar'
        if reserva.Chofer_asignado and reserva.Chofer_asignado.usuario:
            u = reserva.Chofer_asignado.usuario
            chofer_nombre = f"{u.Nombres} {u.Apellidos}".strip()

        evento = {
            'id': str(reserva.Id_reserva),
            'title': f"Reserva - {reserva.Nombre_Cliente} {reserva.Apellidos_Cliente}".strip(),
            'start': datetime.combine(reserva.Fecha, reserva.Hora).isoformat(),
            'extendedProps': {
                'clienteNombre': f"{reserva.Nombre_Cliente} {reserva.Apellidos_Cliente}".strip(),
                'clienteTelefono': reserva.Telefono,
                'clienteCorreo': reserva.Correo or '',
                'desde': reserva.Origen.Nombre_Comuna if reserva.Origen else '',
                'hasta': reserva.Destino.Nombre_Comuna if reserva.Destino else '',
                'nro_vuelo': reserva.nro_vuelo or '',
                'chofer': chofer_nombre,
                'monto': reserva.Monto_tarifa,
                'estado': reserva.estado or 'PENDIENTE',
                'Confirmacion_pagoConductor': True,
                'mediopago': reserva.mediopago,
                'comentario': reserva.Comentario,
                
            },
            'classNames': [f"evt-{(reserva.estado or '').lower()}"] if reserva.estado else [],
        }
        return JsonResponse({'exito': True, 'evento': evento})

    # Serializar errores de formulario de manera simple
    return JsonResponse({'exito': False, 'errores': form.errors}, status=400)


@require_POST
def crear_reserva_web(request):
    try:
        datos = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'exito': False, 'mensaje': 'Solicitud invÃ¡lida'}, status=400)

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
            'nro_vuelo': reserva.nro_vuelo or '',
            'desde': reserva.Origen.Nombre_Comuna if reserva.Origen else '',
            'hasta': reserva.Destino.Nombre_Comuna if reserva.Destino else '',
            'direccion': reserva.Dirrecion,
            'fecha': reserva.Fecha.strftime('%Y-%m-%d'),
            'hora': reserva.Hora.strftime('%H:%M'),
            'personas': reserva.Cantidad_pasajeros,
            'maletas': reserva.Cantidad_maletas,
            'mediopago': reserva.mediopago,
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
        return JsonResponse({'exito': False, 'mensaje': 'Solicitud invÃ¡lida'}, status=400)

    reserva_id = datos.get('reserva_id')
    chofer_id = datos.get('chofer_id')
    
    # â­ MODIFICACIÃ“N 1: Obtener el monto de la solicitud JSON
    monto_tarifa = datos.get('monto_tarifa') 

    if not reserva_id or not chofer_id or monto_tarifa is None:
        # Nota: monto_tarifa se valida como 'is None' porque podrÃ­a ser 0
        return JsonResponse({'exito': False, 'mensaje': 'Datos incompletos (reserva, chofer o monto faltantes)'}, status=400)

    try:
        # Convertir monto a entero, asumiendo que el campo en el modelo es IntegerField
        monto_tarifa = int(monto_tarifa)
    except (ValueError, TypeError):
        return JsonResponse({'exito': False, 'mensaje': 'Monto de tarifa invÃ¡lido'}, status=400)


    reserva_web = get_object_or_404(ReservasWeb, pk=reserva_id)
    chofer = get_object_or_404(Conductores.objects.select_related('usuario'), pk=chofer_id)

    # Crear la nueva reserva confirmada
    reserva_confirmada = Reservas.objects.create(
        Nombre_Cliente=reserva_web.Nombre_Cliente,
        Apellidos_Cliente=reserva_web.Apellidos_Cliente,
        Telefono=reserva_web.Telefono,
        Correo=reserva_web.Correo,
        nro_vuelo=reserva_web.nro_vuelo,
        Origen=reserva_web.Origen,
        Destino=reserva_web.Destino,
        
        # â­ MODIFICACIÃ“N 2: Asignar el monto
        Monto_tarifa=monto_tarifa, 
        
        Dirrecion=reserva_web.Dirrecion,
        Fecha=reserva_web.Fecha,
        Hora=reserva_web.Hora,
        Cantidad_pasajeros=reserva_web.Cantidad_pasajeros,
        Cantidad_maletas=reserva_web.Cantidad_maletas,
        Confirmacion=True,
        Chofer_asignado=chofer,
        mediopago=reserva_web.mediopago,
        Confirmacion_pagoConductor=False,
        Comentario=reserva_web.Comentario 
    )

    _enviar_correo_confirmacion_reserva(reserva_confirmada)

    # Preparar el objeto evento para el calendario
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
            'nro_vuelo': reserva_confirmada.nro_vuelo or '',
            'monto': str(reserva_confirmada.Monto_tarifa), # Opcional: incluir el monto en el evento
            'chofer': f"{chofer.usuario.Nombres} {chofer.usuario.Apellidos}".strip(),
            'estado': reserva_confirmada.estado or 'PENDIENTE',
            'Confirmacion_pagoConductor': reserva_confirmada.Confirmacion_pagoConductor or '',
            'mediopago': reserva_confirmada.mediopago or '',
            'Comentario': reserva_confirmada.Comentario or 'Sin comentario',
        },
        'classNames': [f"evt-{(reserva_confirmada.estado or '').lower()}"] if reserva_confirmada.estado else [],
    }

    # Eliminar la reserva web original
    reserva_web.delete()

    return JsonResponse({'exito': True, 'evento': evento})

@login_required
@user_passes_test(es_admin)
@require_POST
def rechazar_reserva_web(request):
    try:
        datos = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'exito': False, 'mensaje': 'Solicitud invÃ¡lida'}, status=400)

    reserva_id = datos.get('reserva_id')

    if not reserva_id:
        return JsonResponse({'exito': False, 'mensaje': 'Datos incompletos'}, status=400)

    reserva_web = get_object_or_404(ReservasWeb, pk=reserva_id)
    reserva_web.delete()

    return JsonResponse({'exito': True})

@login_required
@user_passes_test(es_admin)
def delete_Tarifa(request, id):
    tarifa_eliminar = Tarifas.objects.get(id_tarifa=id)
    tarifa_eliminar.delete()
    return redirect(to="vista_tarifas_admin")

#-------------------------------------------------------------------------------------------------------------------------------
@login_required
@user_passes_test(es_admin)
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

