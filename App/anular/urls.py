from django.urls import path
from App.anular import views

urlpatterns = [
    path('', views.anular, name="anular"),
    path('filtrorut/<str:rut>/', views.filtrorut, name="filtrorut"),
    path('anulado/', views.anulado, name="anulado"),
]