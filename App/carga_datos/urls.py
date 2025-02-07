from django.urls import path
from App.carga_datos import views

urlpatterns = [
    path('', views.form_carga_datos, name="form_carga_datos"),
    path('inicio', views.inicio, name="inicio"),
    path('busqueda_datos/', views.busqueda_datos, name="busqueda_datos"),
]