from django.urls import path
from App.crear_correo import views

urlpatterns = [
    path('', views.form_correo, name="form_correo"),
    path('insertar_correo/', views.insertar_correo, name="insertar_correo"),
]