from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from App.carga_datos.models import correo


# Create your views here.
@login_required
def form_correo(request):
    return render(
        request,
        'crear_correo/crear_correo.html'
)

def insertar_correo(request):
    if request.method == 'POST':
        nombre_medico = request.POST.get('nombre')
        rut_medico = request.POST.get('rut')
        correo_medico = request.POST.get('correo')
        correo_sec = ""

        if 'correo_secundario' in request.POST:
            correo_sec = True
        else:
            correo_sec = False

        try:
            ultimo_registro = correo.objects.last()


            datos_correo = correo(
                nombre=nombre_medico,
                rut=rut_medico,
                correo=correo_medico,
                valido=True,
                correo_secundario=correo_sec
            )

            if ultimo_registro:
                nuevo_id = ultimo_registro.id + 1
                datos_correo.id = nuevo_id

            datos_correo.save()

            messages.success(request, 'Datos insertados correctamente en el sistema')

            return redirect('form_correo')
        except Exception as e:
            messages.error(request, f"Ocurrió un error al insertar datos al sistema: {e}")

    messages.error(request, 'Método no permitido')
    return redirect('form_correo')
