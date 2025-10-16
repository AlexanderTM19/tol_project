# core/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 
from django.shortcuts import render

urlpatterns = [
    path('', views.index, name='inicio'),
    path('reservas/', views.reservas, name='reservas'),
    path('reservas/web/crear', views.crear_reserva_web, name='crear_reserva_web'),
    path('tarifas/', views.tarifas, name='tarifas'),
    path('contacto/', views.contacto, name='contacto'),

    # Sección administrador (protegida con login)
    path('administrador/calendario', views.calendario, name='calendario'),
    path('administrador/choferes', views.choferes, name='choferes'),
    path('administrador/vehiculo', views.vehiculo, name='vehiculo'),
    path('administrador/form_crearConductor', views.form_crear_conductor, name='form_crear_conductor'),
    path('administrador/form_crearVehiculo', views.form_crear_vehiculo, name='form_crear_vehiculo'),
    path('administrador/clientes', views.clientes, name='clientes'),
    path('administrador/vist_Usuarios', views.vist_Usuarios, name='vist_Usuarios'), 
    path('administrador/vista_tarifas_admin', views.vista_tarifas_admin, name='vista_tarifas_admin'),
    path('administrador/form_mod_tarifa/<id>', views.form_mod_tarifa, name='form_mod_tarifa'),
    path('administrador/form_crear_usuarios', views.form_crear_usuarios, name='form_crear_usuarios'),
    path('administrador/form_modUser/<id>',views.form_mod_usu, name='form_mod_usu'),
    path('administrador/form_Rol', views.form_Rol, name='form_Rol'),
    path('administrador/form_clientes', views.form_clientes, name='form_clientes'),
    path('administrador/form_modpro/<id>',views.form_modpro, name='form_modpro'),
    path('administrador/', views.admin_config, name='admin_config'),
    path('administrador/estadisticas', views.estadisticas, name='estadisticas'),
    path('administrador/reservas-web/pendientes', views.reservas_web_pendientes, name='reservas_web_pendientes'),
    path('administrador/reservas-web/aceptar', views.aceptar_reserva_web, name='aceptar_reserva_web'),
    path('administrador/reservas-web/rechazar', views.rechazar_reserva_web, name='rechazar_reserva_web'),
    path('administrador/reservas/crear', views.crear_reserva_admin, name='crear_reserva_admin'),
    path('delete_Tarifa/<id>',views.delete_Tarifa,name='delete_Tarifa'),

    # Login y Logout
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='inicio'), name='logout'),

    # Ficha conductor y perfil conductor
    path('ficha-conductor/', views.ficha_conductor, name='ficha_conductor'),
    path('perfil-conductor/', views.perfil_conductor_view, name='perfil_conductor'),
    path('servicios-conductor/', views.servicios_conductor, name='servicios_conductor'),


]
