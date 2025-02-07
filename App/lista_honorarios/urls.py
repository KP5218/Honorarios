from django.urls import path
from App.lista_honorarios import views

urlpatterns = [
    path('', views.form_busqueda_datos, name="form_busqueda_datos"),
    path('descargarpdf', views.descargar_pdf, name="descargar_pdf"),
]