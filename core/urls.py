# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='inicio'),
    path('reservas/', views.reservas, name='reservas'),
    path('tarifas/', views.tarifas, name='tarifas'),
    path('contacto/', views.contacto, name='contacto'),
    path('administrador/calendario', views.calendario, name='calendario'),
    path('administrador/choferes', views.choferes, name='choferes'),
    path('administrador/clientes', views.clientes, name='clientes'),
    path('administrador/', views.admin_config, name='admin_config'),
]