from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from App.carga_datos.models import correo,liqui_honorario_total, Anulado
import json
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages

# Create your views here.

@login_required
def anular(request):
    assert isinstance(request, HttpRequest)

    return render(request, 'anular/anular.html')

@csrf_exempt
def filtrorut(request, rut):
    if request.method == "POST":
        correos_asociados = correo.objects.filter(rut=rut, valido=True)
        lista_correos = [correo_asociado.correo for correo_asociado in correos_asociados]
        return JsonResponse({'correos': lista_correos})

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def anulado(request):
    if request.method == 'POST':
        try:
            motivo = request.POST.get('motivo_anulacion', '')
            anulado_data = request.POST.get('correosSeleccionados', '')

            datos_lista = json.loads(anulado_data)

            for item in datos_lista:
                correo_individual = item['correo']
                rut_individual = item['rut']

                resultados = correo.objects.filter(correo=correo_individual, rut=rut_individual)

                if resultados.exists():
                    for correo_obj in resultados:
                        correo_obj.valido = False
                        correo_obj.save()

                        # Obtener el último ID registrado y sumarle 1
                        ultimo_registro = Anulado.objects.order_by('-id').first()
                        nuevo_id = (ultimo_registro.id + 1) if ultimo_registro else 1

                        registro_anulado = Anulado.objects.create(
                            id=nuevo_id,
                            motivo_anulacion=motivo,
                            fecha_anulacion=timezone.now(),
                            responsable=request.user.username if request.user.is_authenticated else None,
                            correo_id=correo_obj
                        )
                        registro_anulado.save()

                        messages.success(request, 'Correo se ha anulado correctamente.')
                else:
                    messages.error(request, 'No se encontraron correos para anular.')

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return HttpResponseRedirect(reverse("anular"))
