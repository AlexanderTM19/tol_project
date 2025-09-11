# core/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.shortcuts import render

urlpatterns = [
    path('', views.index, name='inicio'),
    path('reservas/', views.reservas, name='reservas'),
    path('tarifas/', views.tarifas, name='tarifas'),
    path('contacto/', views.contacto, name='contacto'),

    # Sección administrador (protegida con login)
    path('administrador/calendario', views.calendario, name='calendario'),
    path('administrador/choferes', views.choferes, name='choferes'),
    path('administrador/clientes', views.clientes, name='clientes'),
    path('administrador/form_crearusuarios', views.form_clientes, name='form_clientes'),
    path('administrador/form_modpro/<id>',views.form_modpro, name='form_modpro'),
    path('administrador/', views.admin_config, name='admin_config'),

    # Login y Logout
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='inicio'), name='logout'),

    # Ficha conductor y perfil conductor
    path('ficha-conductor/', views.ficha_conductor, name='ficha_conductor'),
    path('perfil-conductor/', lambda request: render(request, 'core/perfilConductor.html'), name='perfil_conductor'),
]
