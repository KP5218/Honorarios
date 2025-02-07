from django.urls import path

from App.carga_correos_masivo import views

urlpatterns = [
    path('', views.form_carga_correos, name="form_carga_correos"),
]