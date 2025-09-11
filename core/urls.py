# core/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

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
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='inicio'), name='logout'),
]
